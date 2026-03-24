#!/usr/bin/env python3
"""
extract.py - OpenClawセッションjsonlから会話を抽出・フィルタリング

Usage:
  python3 src/extract.py --date 2026-02-07
  python3 src/extract.py --date 2026-02-07 --preview
"""

import os
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent.parent
CONFIG_FILE = SCRIPT_DIR / "config" / "agents.json"

HEARTBEAT_PATTERNS = [
    "HEARTBEAT_OK",
    "Read HEARTBEAT.md",
    "[cron:",
    "heartbeat poll",
]

def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def is_heartbeat_session(messages):
    """heartbeat/cronセッションかどうか判定"""
    if not messages:
        return True
    for msg in messages:
        role = msg.get('role', '')
        text = msg.get('text', '')
        if role == 'user':
            for pattern in HEARTBEAT_PATTERNS:
                if pattern in text:
                    return True
    return False

def extract_messages(jsonl_path):
    """jsonlファイルからuser/assistantのメッセージを抽出"""
    messages = []
    try:
        with open(jsonl_path) as f:
            for line in f:
                try:
                    d = json.loads(line.strip())
                except:
                    continue
                if d.get('type') != 'message':
                    continue
                msg = d.get('message', {})
                role = msg.get('role', '')
                if role not in ('user', 'assistant'):
                    continue
                content = msg.get('content', '')
                if isinstance(content, list):
                    text = '\n'.join(
                        c.get('text', '') for c in content
                        if isinstance(c, dict) and c.get('type') == 'text'
                    ).strip()
                else:
                    text = str(content).strip()
                # toolResult等の空メッセージはスキップ
                if not text:
                    continue
                messages.append({'role': role, 'text': text})
    except Exception as e:
        pass
    return messages

def extract_date(jsonl_path):
    """セッションファイルの日付を取得"""
    try:
        with open(jsonl_path) as f:
            first = json.loads(f.readline())
        ts = first.get('timestamp', '')
        return ts[:10] if ts else None
    except:
        return None

def load_sessions_for_date(sessions_dir, target_date):
    """指定日のセッションを全件読み込み、フィルタして返す"""
    sessions_dir = Path(sessions_dir)
    all_sessions = []

    for fpath in sessions_dir.glob("*.jsonl"):
        date = extract_date(fpath)
        if date != target_date:
            continue
        messages = extract_messages(fpath)
        if not messages:
            continue
        if is_heartbeat_session(messages):
            continue
        # userとassistant両方いるか
        roles = {m['role'] for m in messages}
        if 'user' not in roles or 'assistant' not in roles:
            continue
        all_sessions.append({
            'file': fpath.name,
            'messages': messages
        })

    # メッセージ数でソート（多い順）
    all_sessions.sort(key=lambda x: len(x['messages']), reverse=True)
    return all_sessions

def format_conversation(sessions):
    """セッションリストを会話テキストに変換"""
    lines = []
    for i, session in enumerate(sessions, 1):
        lines.append(f"=== セッション {i} ({session['file'][:8]}...) ===")
        for msg in session['messages']:
            role_label = "マスター" if msg['role'] == 'user' else "テディ"
            # 長すぎるメッセージは切り詰め
            text = msg['text']
            if len(text) > 500:
                text = text[:500] + "...(省略)"
            lines.append(f"[{role_label}] {text}")
        lines.append("")
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description='OpenClawセッションから会話を抽出')
    parser.add_argument('--date', required=True, help='対象日付 (YYYY-MM-DD)')
    parser.add_argument('--agent', default='teddy', help='エージェント名')
    parser.add_argument('--preview', action='store_true', help='抽出結果をプレビュー表示')
    parser.add_argument('--out', help='出力ファイルパス（省略時はstdout）')
    args = parser.parse_args()

    config = load_config()
    agent = next((a for a in config['agents'] if a['name'] == args.agent), None)
    if not agent:
        print(f"ERROR: agent '{args.agent}' not found in config", file=sys.stderr)
        sys.exit(1)

    print(f"[extract] {args.date} のセッションを抽出中...", file=sys.stderr)
    sessions = load_sessions_for_date(agent['sessions_dir'], args.date)
    print(f"[extract] 有効セッション: {len(sessions)}件", file=sys.stderr)

    if not sessions:
        print(f"[extract] 対象セッションなし", file=sys.stderr)
        sys.exit(0)

    conversation = format_conversation(sessions)

    total_msgs = sum(len(s['messages']) for s in sessions)
    user_msgs = sum(sum(1 for m in s['messages'] if m['role']=='user') for s in sessions)
    print(f"[extract] 総メッセージ数: {total_msgs} (userターン: {user_msgs})", file=sys.stderr)

    if args.preview:
        # プレビューは最初の3セッションのみ
        preview_sessions = sessions[:3]
        print("\n--- PREVIEW (上位3セッション) ---\n")
        print(format_conversation(preview_sessions))
    elif args.out:
        with open(args.out, 'w') as f:
            f.write(conversation)
        print(f"[extract] 出力: {args.out}", file=sys.stderr)
    else:
        print(conversation)

if __name__ == '__main__':
    main()
