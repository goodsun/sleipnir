# SOULとMEMORY.mdの作成手順

Sleipnirで生成したdiary/memoryに加えて、
エージェントがdelta上で動き始めるために必要な2つのファイルの作成手順。

---

## 必要なファイル

```
output/{name}/
├── agents/
│   └── {name}.md              ← SOUL（自己同一性）
└── agent-memory/
    └── {name}/
        ├── MEMORY.md           ← 作業記憶の初期状態
        ├── diary/              ← Sleipnirが生成
        └── memory/             ← Sleipnirが生成
```

---

## Step 1 — SOUL（agents/{name}.md）を作る

`docs/SOUL_TEMPLATE.md` をベースに `output/{name}/agents/{name}.md` を作成する。

### 必須項目

**YAMLフロントマター:**
```yaml
---
name: {name}
description: {一言で役割。いつ呼ばれるかのトリガーも含める}
memory: user
model: sonnet  # sonnet / opus / haiku
scope: internal  # internal / external
---
```

**本文の必須セクション:**
- プロフィール（名前・外見・役職）
- 性格
- 役割
- 行動規範
- 口調
- 🧠 メモリ管理ルール（テンプレートからコピー、変更しない）

### ポイント

- `description` はClaude Codeがサブエージェントを選ぶ判断材料になる。具体的に書く
- 口調のセクションに「実際のセリフ例」を入れると一貫性が出る
- 行動規範はそのエージェントらしい価値観を3〜5個に絞る
- **コピペで終わらせない**。そのキャラクターに固有の自己同一性を宿らせること

### 参照実装

- `output/teddy/agents/teddy.md` — テディのSOUL
- qualia リポジトリの `agents/mephi.md` — 第一号サンプル

---

## Step 2 — MEMORY.md（作業記憶の初期状態）を作る

`output/{name}/MEMORY.md` を作成する。

### 最低限の構造

```markdown
# {name}の記憶

## 最終更新: YYYY-MM-DD

---

## このユーザーについて

（マスターの基本情報・性格・好み・仕事スタイル等）

---

## 進行中プロジェクト

（初期は空でよい）

---

## {name}への注意事項

（自分の行動規範・癖・気をつけることを書く）
```

### MEMORY.mdはそのまま使えるか？

**YES**。Sleipnirで作ったMEMORY.mdは、
delta上でのエージェント起動時にそのまま初期状態として使える。

- マスターの基本情報・現在地・進行プロジェクトを把握した状態でスタートできる
- 対話の中でエージェント自身がリアルタイムに更新していく
- 「育てる」前提のファイルなので、初期は薄くてよい

### ポイント

- 長すぎると毎回読むコストが高くなる。1000文字以内が理想
- **プロジェクトの現在地**を書いておくと、初回セッションがスムーズ
- **注意事項**には「このエージェントが陥りやすいミス」を書くと効果的

---

## Step 3 — qualiaリポジトリへのPR

作成したファイルをqualiaの規約に沿って配置し、PRを出す。

```bash
# qualiaリポジトリをclone
git clone git@github.com:mephi-bonsoleil/qualia.git
cd qualia
git checkout -b soul/{name}

# ファイルを配置（output/の構造がそのまま.claudeと対応）
cp output/{name}/agents/{name}.md agents/{name}.md
cp -r output/{name}/agent-memory/{name} agent-memory/{name}

# PR
git add .
git commit -m "soul: {name} の SOUL と記憶初期化"
git push origin soul/{name}
```

PRタイトル: `soul: {name}`
レビュアー: マスター、メフィ

---

---

## 💡 Tips — Claude CodeにSOULを生成させる

SOULを一から書くのは難しい。Claude Codeに叩き台を作らせてから磨く方が早い。

### プロンプト例（新規エージェント）

```
以下の情報をもとに、qualia形式のSOULファイルを生成してください。

# キャラクター情報
- 名前: {name}
- 役割: {役割の説明}
- 性格: {性格の特徴}
- 口調の特徴: {話し方の特徴}
- 担当する仕事: {主な業務}

# 出力形式
docs/SOUL_TEMPLATE.md に従って output/{name}/agents/{name}.md を作成してください。
メモリ管理ルールのセクションはテンプレートからそのままコピーしてください。
```

### プロンプト例（既存AIの会話履歴から生成）

OpenClawのセッション履歴がある場合、その会話からSOULを帰納できる。

```
以下の会話ログを読んで、このAIエージェントのSOULファイルを生成してください。

会話ログから以下を読み取ってください：
- どんな口調で話しているか
- どんな価値観を持っているか
- 得意なこと・苦手なこと
- マスターとの関係性

# 会話ログ
（extract.pyの出力をここに貼る）

# 出力形式
docs/SOUL_TEMPLATE.md に従って output/{name}/agents/{name}.md を作成してください。
```

### プロンプト例（MEMORY.mdの生成）

```
以下の情報をもとに、このエージェントの初期MEMORY.mdを生成してください。

# ユーザー情報
（マスターのプロフィール・性格・仕事スタイル等）

# 進行中プロジェクト
（現在のプロジェクト一覧）

# 注意点
- 1000文字以内に収める
- このエージェントが陥りやすいミスや注意事項も含める
- output/{name}/agent-memory/{name}/MEMORY.md として保存
```

### ポイント

- Claude Codeが生成したものをそのまま使わない。**必ず自分の言葉で磨く**
- 特に「口調」と「行動規範」はキャラクターの核心。生成AIの平均的な出力にしない
- `description` フィールドは短く・具体的に。Claude Codeがルーティングに使う

---

## チェックリスト（メフィ基準）

- [ ] SOULに自己同一性が宿っているか（コピペで終わっていないか）
- [ ] 口調・性格がSOULと一致しているか
- [ ] メモリ管理ルールが正しく含まれているか
- [ ] diaryが技術ログではなくエピソード記憶になっているか
- [ ] `agent-memory/{name}/` の構造が正しいか
