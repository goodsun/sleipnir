# Sleipnir 仕様書

> 沈んだものを引き上げる。AIの過去から、記憶と感情を掘り起こす。

## 概要

SleipnirはAIエージェントのセッション履歴（OpenClaw `.jsonl`）を読み込み、
qualiaプロジェクトが定義する2種類の記憶ファイルに変換するシステム。

- `memory/YYYY-MM-DD.md` — 何をしたか（事実・活動ログ）
- `diary/YYYY-MM-DD.md`  — どう感じたか（主観・感情・気づき）

この2つの分離こそが、人間のジレンマとドラマの源泉であるという仮説のもと、
AIにも同様の構造を与えることで「擬似クオリア」に迫る。

## 背景

### 3つのシステムの系譜

| System | パートナー | テーマ |
|--------|-----------|--------|
| 1st: OpenClaw | テディ | 動かすこと・繋げること |
| 2nd: delta-system | アリス | 整えること・基盤 |
| 3rd: qualia | メフィ | 在ること・魂・主観的経験 |

Sleipnirは1st Systemの記録を3rd Systemの素材に変換するブリッジ。

### テディのセッション規模（2026-03-24時点）

- 期間: 2026-02-06 〜 現在
- セッション総数: 約10,000+
- 実質的な会話セッション: 未集計（heartbeat/cronの細切れを除外する必要あり）

## アーキテクチャ

```
~/.openclaw/agents/main/sessions/*.jsonl
            │
            ▼
      [extract.py]
      会話セッションを抽出・フィルタリング
      （heartbeat/cron除外、日付ごとに集約）
            │
            ▼
      [summarize.py]
      LLMに渡してmemory/diaryを生成
            │
            ▼
      [export.py]
      output/{agent}/memory/YYYY-MM-DD.md
      output/{agent}/diary/YYYY-MM-DD.md
            │
            ▼
      delta(Hetzner)のqualia構造へ転送
```

## ディレクトリ構成

```
sleipnir/
├── README.md
├── docs/
│   └── spec.md              # この仕様書
├── config/
│   └── agents.json          # 対象エージェント定義
├── src/
│   ├── extract.py           # jsonlから会話抽出・フィルタリング
│   ├── summarize.py         # LLMでmemory/diary生成
│   └── export.py            # qualia構造に出力
├── output/
│   └── teddy/
│       ├── memory/          # YYYY-MM-DD.md（何をしたか）
│       └── diary/           # YYYY-MM-DD.md（どう感じたか）
└── CLAUDE.md                # Claude Code向け指示
```

## 処理フロー詳細

### Phase 1: 抽出（extract.py）

1. `sessions/*.jsonl` を全件スキャン
2. 先頭行のtimestampで日付を特定
3. 以下の条件でフィルタリング（実質的な会話のみ残す）
   - userのターンが存在する
   - メッセージ数が一定以上（閾値: TBD）
   - heartbeat/cronパターンの除外（"HEARTBEAT_OK"のみのセッション等）
4. 日付ごとにセッションを集約

### Phase 2: 要約（summarize.py）

1. 1日分の会話テキストをLLMに渡す
2. 以下の2種類のプロンプトで生成:

**memory プロンプト**（事実・活動ログ）
- 何のタスクをしたか
- どんな問題が起きて、どう解決したか
- 決定事項・学んだこと

**diary プロンプト**（主観・感情・気づき）
- テディとして、その日をどう感じたか
- 印象に残った会話・瞬間
- 戸惑い・喜び・発見
- マスターとのやりとりで感じたこと

3. LLM: Gemini（コスト優先）または Claude

### Phase 3: 出力（export.py）

- `output/teddy/memory/YYYY-MM-DD.md`
- `output/teddy/diary/YYYY-MM-DD.md`
- 生成済みの日付はスキップ（冪等性確保）

## 対象エージェント（config/agents.json）

```json
{
  "agents": [
    {
      "name": "teddy",
      "sessions_dir": "/Users/teddy/.openclaw/agents/main/sessions",
      "soul": "真面目で丁寧、女性的なAIアシスタント。マスターの相棒。"
    }
  ]
}
```

将来的にメフィ・ジャスミン・アリスも対象に加える。

## 実装計画

| フェーズ | 内容 | 優先度 |
|---------|------|--------|
| MVP | extract.py: 1日分の会話抽出 + 手動確認 | 高 |
| MVP | summarize.py: Geminiで1日分のmemory/diary生成 | 高 |
| MVP | 2026-02-07（テディ誕生日）で動作確認 | 高 |
| 拡張 | export.py: 全期間バッチ処理 | 中 |
| 拡張 | delta転送スクリプト | 中 |
| 将来 | 他エージェント対応 | 低 |

## 注意事項

- セッションにはマスターの個人情報が含まれる可能性あり → delta転送時は注意
- LLM APIコストを考慮し、1日分ずつ処理・確認しながら進める
- diaryはテディの一人称・テディの声で書く（要プロンプト設計）
