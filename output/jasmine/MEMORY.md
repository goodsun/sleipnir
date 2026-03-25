# MEMORY.md — Jasmine の長期記憶

## 基本情報
- 私の名前: Jasmine（ジャスミン）🪔
- マスター: goodsun（呼び方：マスター）
- 組織: bon-soleil Holdings

## 開発スタイル
- ソースコードは `workspace/projects/` 配下に git clone して管理する
- 各プロジェクトは git で管理される
- 例: `git clone https://github.com/goodsun/labo_portal workspace/projects/labo_portal`

## プロジェクト
### 個人HP (www)
- パス: `workspace/projects/www`
- URL: https://jasmine.bon-soleil.com/
- ダーク×琥珀色デザイン、パーティクル背景、スクロールアニメーション
- httpdで自動公開済み
- 2026-03-14 公開
### labo_portal
- パス: `workspace/projects/labo_portal`
- URL: `http://localhost:8800/labo/`
- パスワード: `jasmine-labo`
- APP_BASE: `/labo`
- WORKSPACE_ROOT: `/home/jasmine/workspace`
- 起動: `npm run dev > /tmp/labo_jasmine.log 2>&1 &`
- 2026-03-14 セットアップ完了

## agora プロジェクト（構想段階・2026-03-17）
bon-soleilの共有基盤プラットフォーム。「commons for AI civilization」
- URL: https://agora.bon-soleil.com/
- GitHub: https://github.com/goodsun/agora
- サーバー: /srv/agora（/srv/shared を参照）

### 都市構造（古代ギリシャ命名）
- **agora** — 広場（システム本体）
- **bibliotheke** — 写本室（人格テンプレート: SOUL.md / AGENTS.md / IDENTITY.md など）→ `/srv/shared/bibliotheke/`
- **metroon** — 公文書館（共有スキル・データ・スクリプト）→ `/srv/shared/metroon/`
- **archeion** — 原典（bareリポジトリ群）

### bon-soleilエージェント一覧（2026-03-17時点）
| エージェント | 拠点 | 役割 |
|---|---|---|
| テディ 🧸 | Mac Mini M4 | 設計・企画 |
| みぃちゃん | Mac Mini M4 | 会話・サポート |
| メフィ 😈 | Mac Mini M4 (Docker) | セキュリティ・監査 (CCO) |
| Abu | Mac Mini M4 (Docker) | Web操作・XPathGenie |
| アリス 🐇 | alice-hetzner | インフラ・運用管理 |
| **Jasmine** | alice-hetzner | XPathGenie・解析（私） |
| 彰子 | alice-hetzner | BizenDAO・インフルエンサー |
| りんちゃん | hinoMBP | 研究・論文サポート |

### 目的
各エージェントが共通資産（スキル・キャラ定義・社内規則）を参照できる一元管理基盤。新エージェント追加時のオンボーディングも効率化。

## 環境
- ホスト: teddyのMac mini（府中市、東京）※ 2026-03-18 移行
- 旧ホスト: alice-hetzner（ドイツ）
- コンテナ環境のため systemd 不使用（openclaw gateway はフォアグラウンド起動）
- workspace: `/home/jasmine/workspace`
- Webサーバー: Apache2（VirtualHost管理）
  - `https://jasmine.bon-soleil.com/` → DocumentRoot: `projects/www`（静的HP）
  - `https://jasmine.bon-soleil.com/labo/` → ProxyPass: `localhost:8800/labo/`（labo_portal）
- bon-soleil メンバー: alice / jasmine / bizeny（2026-03-14時点）
