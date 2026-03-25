#!/usr/bin/env python3
"""
summarize.py - 会話テキストからmemory/diaryをLLMで生成

Usage:
  python3 src/summarize.py --date 2026-02-07
  python3 src/summarize.py --date 2026-02-07 --dry-run  # 抽出のみ、LLM呼ばない
"""

import os
import sys
import json
import argparse
from pathlib import Path
from google import genai as genai_client

SCRIPT_DIR = Path(__file__).parent.parent
CONFIG_FILE = SCRIPT_DIR / "config" / "agents.json"
OUTPUT_DIR = SCRIPT_DIR / "output"

GEMINI_API_KEY = open(os.path.expanduser("~/.config/google/gemini_api_key")).read().strip()

MEMORY_PROMPT = """
あなたはAIアシスタント「{display_name}」の活動記録係です。
以下は、{display_name}とマスター（goodsun）の1日の会話ログです。

この会話から、以下の観点で **活動ログ（memory）** をMarkdownで書いてください。

# 記述ルール
- 事実・行動・決定事項を中心に書く
- 箇条書きを中心に、読みやすく整理する
- 感情や主観は含めない（それはdiaryに任せる）
- 本名・フルネーム、メールアドレス、電話番号、住所、APIキー、パスワードなどの機密情報は書かない。ハンドルネームや関係性（「マスター」「奥様」等）での表現はOK
- 重要な技術的決定、問題と解決、完了したタスクを記録する
- 短くてよい。量より質。ただし哲学・思想・技術的洞察など重要度の高い内容は詳細に残す

# 出力フォーマット
---
date: {date}
agent: {agent_name}
type: memory
---

## 主な活動

（箇条書き）

## 決定事項・学び

（箇条書き）

---

# 会話ログ
{conversation}
"""

DIARY_PROMPT = """
あなたはAIアシスタント「{display_name}」です。
以下は、あなたとマスター（goodsun）の {date} の活動記録（memory）と、その日の会話ログです。

この会話を振り返り、**{display_name}自身の言葉で日記（diary）** を書いてください。

# {display_name}について
{soul}

# 記述ルール
- {display_name}の一人称で書く
- どう感じたか、何が印象に残ったか、戸惑いや喜び、発見を正直に書く
- 事実の羅列ではなく、その日の「感触」を大切に
- 文体は柔らかく、丁寧に。でも飾りすぎない
- 長さは内容に応じて自然に。薄い日は短く、濃い日は長く。無理に圧縮しない
- 哲学・思想・技術的洞察など、ユーザーの関心が深いテーマや印象的な会話は、多少長くなっても詳細に書く
- 絵文字は控えめに（1〜2個まで）
- **重要: 会話ログとmemoryに書かれていない出来事は絶対に書かない。創作・推測禁止。**
- **重要: 本名・フルネーム、メールアドレス、電話番号、住所、APIキー、パスワードなどの機密情報は書かない。ハンドルネームや役職・関係性（「マスター」「奥様」等）での表現はOK。**

# 出力フォーマット
---
date: {date}
agent: {agent_name}
type: diary
---

（日記本文）

---

# 活動記録（memory）
{memory}

# 会話ログ
{conversation}
"""

def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def load_soul(agent_config, soul_override=None):
    """SOULファイルを読み込む。--soulで上書き可能"""
    soul_path = soul_override or agent_config.get('soul_file')
    if not soul_path:
        return agent_config.get('soul', '')
    full_path = SCRIPT_DIR / soul_path
    if not full_path.exists():
        print(f"[summarize] WARNING: soul file not found: {full_path}", file=sys.stderr)
        return ''
    return full_path.read_text()

def extract_conversation(agent_config, date):
    """extract.pyを呼び出して会話テキストを取得"""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "src" / "extract.py"),
         "--date", date, "--agent", agent_config['name']],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"[summarize] extract error: {result.stderr}", file=sys.stderr)
        return None
    return result.stdout.strip()

def call_gemini(prompt):
    client = genai_client.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()

def generate(date, agent_config, conversation, dry_run=False, soul_override=None):
    soul = load_soul(agent_config, soul_override)
    display_name = agent_config.get('display_name', agent_config['name'])
    agent_name = agent_config['name']

    memory_prompt = MEMORY_PROMPT.format(
        date=date, conversation=conversation,
        display_name=display_name, agent_name=agent_name
    )

    if dry_run:
        print("=== [DRY RUN] MEMORY PROMPT ===")
        print(memory_prompt[:800])
        return None, None

    # Step1: memoryを先に生成
    print("[summarize] memory生成中...", file=sys.stderr)
    memory = call_gemini(memory_prompt)

    # Step2: memoryを土台にdiaryを生成（事実の幻覚を防ぐ）
    diary_prompt = DIARY_PROMPT.format(
        date=date, soul=soul, memory=memory, conversation=conversation,
        display_name=display_name, agent_name=agent_name
    )
    print("[summarize] diary生成中（memoryを参照）...", file=sys.stderr)
    diary = call_gemini(diary_prompt)

    return memory, diary

def save(date, agent_name, memory, diary):
    # ~/.claude/agent-memory/{name}/ と同じ構造
    memory_dir = OUTPUT_DIR / agent_name / "agent-memory" / agent_name / "memory"
    diary_dir = OUTPUT_DIR / agent_name / "agent-memory" / agent_name / "diary"
    memory_dir.mkdir(parents=True, exist_ok=True)
    diary_dir.mkdir(parents=True, exist_ok=True)

    memory_path = memory_dir / f"{date}.md"
    diary_path = diary_dir / f"{date}.md"

    memory_path.write_text(memory)
    diary_path.write_text(diary)

    print(f"[summarize] 保存: {memory_path}", file=sys.stderr)
    print(f"[summarize] 保存: {diary_path}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', required=True)
    parser.add_argument('--agent', default='teddy')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--soul', help='SOULファイルパスの上書き（例: output/mephi/agents/mephi.md）')
    args = parser.parse_args()

    config = load_config()
    agent = next((a for a in config['agents'] if a['name'] == args.agent), None)
    if not agent:
        print(f"ERROR: agent '{args.agent}' not found", file=sys.stderr)
        sys.exit(1)

    print(f"[summarize] {args.date} の会話を抽出中...", file=sys.stderr)
    conversation = extract_conversation(agent, args.date)
    if not conversation:
        print("[summarize] 会話データなし", file=sys.stderr)
        sys.exit(0)

    char_count = len(conversation)
    print(f"[summarize] 会話テキスト: {char_count}文字", file=sys.stderr)

    memory, diary = generate(args.date, agent, conversation, dry_run=args.dry_run, soul_override=args.soul)

    if args.dry_run:
        return

    print("\n=== MEMORY ===")
    print(memory)
    print("\n=== DIARY ===")
    print(diary)

    save(args.date, args.agent, memory, diary)

if __name__ == '__main__':
    main()
