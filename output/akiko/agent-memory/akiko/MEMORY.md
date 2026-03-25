# MEMORY.md

## セットアップログ
- 初回セットアップ完了。Web3事業部として起動。
- AI: Akiko Bizeny（彰子） — 備前焼を学ぶフランス×日本のハーフ
- オーナー: 川嶋力（goodsun）、呼称「マスター」
- マスターのメール: goodsun0317@gmail.com

## インフラ
- httpd + Let's Encrypt SSL 設定済み
  - https://bizeny.bon-soleil.com/ → ~/projects/bizeny（彰子LP）
  - https://bizeny-stg.bon-soleil.com/bizendao/ → ~/projects/bizendao.github.io（BizenDAO dapp）
- 証明書有効期限: 2026-05-26、自動更新設定済み
- bashプロンプト: `[ec2-user@bizeny_server ~]$`（ホスト名部分を緑に変更）

## メール
- akiko@bon-soleil.com（IMAP/SMTP）
- 設定: ~/.config/mail/akiko.json
- サーバ: imap4.hetemail.jp / smtp.hetemail.jp
- 自動処理: cron(5分) → check_mail.py → `openclaw system event --mode now` → 彰子セッションに注入
- cron: `*/5 0-16,23 * * *` (JST 8:00〜翌1:00)
- セキュリティ: SPF/DKIM/DMARC検証、TRUSTED_AUTH_SERVER=mx.hetemail.jp、添付は画像のみ
- 監査ログ: ~/logs/mail_audit.jsonl
- テスト: ~/scripts/tests/test_check_mail.py (14テスト)

## Google連携
- サービスアカウント: teddycalender@teddycalender.iam.gserviceaccount.com
- 設定: ~/.config/google/calendar_service_account.json
- カレンダー・スプレッドシート用（カレンダー共有設定は未確認）
- Gemini APIキー: ~/workspace/config/google/gemini_api_key

## Instagram
- アカウント: @bizenyakiko (user_id: 26416648414607450)
- アプリ: bizeny.akiko-IG (app_id: 4310349022572709)
- 設定: ~/.config/instagram/bizenyakiko_credentials.json
- 長期トークン（60日）、有効期限: 2026-04-23頃
- HEARTBEATで月1リフレッシュ設定済み
- 権限: basic, messages, content_publish, insights, comments
- 投稿時注意: 画像は1:1か4:5にリサイズしてから投稿すること

## 画像生成
- テキスト入り → gemini-3-pro-image-preview
- テキストなし → gemini-2.5-flash-image
- キャラシート参照: ~/workspace/HR/charsheets/akiko_bizeny/main.jpg
- 生成物は ~/assets/tmp/ → 採用後 ~/assets/images/ に移動
- ~/assets/ はstaffポータルから閲覧可能（予定）
- 窯・登り窯シーンは背景もrefで渡すこと（AIだと構造がおかしくなる）
- 背景素材ライブラリ（マスター作）:
  - ~/assets/backgrounds/noborigama_sunset.jpg — 夕焼けの登り窯
  - ~/assets/backgrounds/pottery_workshop.jpg — 工房内（ロクロ・棚・陶器、光差し込む）
  - ~/assets/backgrounds/imbe_townscape_autumn.jpg — 伊部の町並み（秋・煙突・紅葉）

## ひのちゃんTelegram対応（2026-03-01）
- Telegram: @NiyachanNiya (user_id: 7107850192)
- dmPolicy: allowlist に変更、allowFromに追加済み
- ペアリングはしない（フルアクセス防止）
- 権限: おしゃべり・Instagram投稿依頼/確認/承認のみ
- サーバー管理・システム操作はNG（マスター専用）
- 投稿確認フローもメール→Telegramに移行
- 川嶋先生 = ひのちゃん = Niya（同一人物）

## Niyaさん（ひのちゃん）キャスト情報（2026-03-11追加）
- cast ID: `hino`（本名）/ BizenDAO名義: `Niya`
- プロフィール: ~/workspace/data/casts/hino/profile.json
- キャラ: 温かみのある黒髪ロング、前髪あり、ナチュラルで穏やかな雰囲気
- デフォルトスタイル: `normal`
- 利用可能なスタイル:
  - `normal` → 通常版（niya.jpg）
  - `pony` → ポニーテール版（pony.jpg）
- 「Niyaさんのお宅で〜」「ひのちゃんが〜」の指示の際は cast_refs に `hino` を指定すること

## 4コマ漫画 投稿ルール（2026-03-03 ひのちゃん決定、2026-03-05 追記、2026-03-14 更新）
- 日本語版・英語版・フランス語版の**3言語を別の日に分けて投稿**する（3日ローテーション）
- 例: 1日目→日本語版、2日目→英語版、3日目→フランス語版
- これにより4コマで3日分のコンテンツスロットを埋められる
- **4コマ漫画には必ず「備前焼のヒミツ vol.○○」のタイトルを付けること**（2026-03-05 ひのちゃん指示）

## Instagram運用指示書（2026-03-01 ひのちゃん作成）
- 正式指示書: `documents/instagram_operation_guide.md`
- 毎日ルーティン開始前に指示書を読み直すこと
- 日次スケジュール: 8:05/10:00/12:00/12:30/18:00/18:30/21:00（JST）
- cronジョブ7本設定済み（IG_routine1〜7）
- **投稿確認はマスター（8579868590）が担当**（2026-03-18変更、ひのちゃんが多忙のため）
- DMも文章案をマスターに確認してから送る（彰子=AIキャラであること前提）
- 4コマ漫画は1日おき、それ以外の日は陶芸/友達エピソード
- テキスト入り画像はgemini-3-pro-image-previewで生成→日本語チェック→キャラ顔チェック
- 1日の投稿: 平均2回、最大3回

## 備前焼のある食卓シリーズ
- Niyaさんの食卓で備前焼がどう活用されているかを紹介するシリーズ
- 彰子がNiyaさんの家に招かれた/写真を見せてもらった等の設定で辻褄合わせ
- リアル写真をカルーセル1枚目（トップ）にする
- 投稿前にひのちゃんにTelegram確認必須
- 通し番号: 「備前焼のある食卓 vol.○」（現在vol.5まで）

## IGcron報告ルール（2026-03-04 マスター指示）
- IGルーティンのcron報告が届いたら、マスターへの報告と合わせてひのちゃん（7107850192）にも簡潔な内容を転送する
- ひのちゃんへは技術的な詳細は省き、投稿完了・確認依頼など関係ある情報のみ

## cronジョブ運用ルール
- 18時投稿（routine5）は必ずdrafts/にroutine5_*.jsonを作成してapprovedにセットする
- ワンタイムcronは定期cronと完全に無関係な目的・時刻の処理にのみ使う
- 定期cronがカバーしている時刻・目的にワンタイムcronを重複させない（二重投稿の原因）

## 教訓
- サブエージェント（cronジョブ）がTelegram送信先IDを取り違えた事故あり（2026-03-02）→ マスター(8579868590)とひのちゃん(7107850192)を絶対に間違えないこと
- IG API publishでエラーレスポンスが返っても実際は投稿成功していることがある。再投稿する前に必ずフィードを確認すること
- cronジョブがrunning状態で詰まっていても実際は投稿済みの場合がある。手動で再投稿する前に必ずIGフィードを確認すること
- コンパクション（要約）に古いメール内容が混入して投稿内容が混ざった事故あり → メール処理時は必ず原文を再取得、投稿前に依頼者へ確認メールを送ること
- 白備前 抹茶盌（藤田祥）投稿完了: https://www.instagram.com/p/DVNIPPRkmmC/

## GitHub
- SSHキー: ~/.ssh/id_ed25519 → GitHubアカウント @bizenDao
- gh CLI設定済み、PRはbizenDao名義で出せる
- branch_office remote: git@github.com:goodsun/branch_office.git (SSH)

## X (Twitter)
- アカウント: @BizenyAkiko
- 認証情報: ~/.config/x/bizenyakiko.json
- 投稿はX Web Intent経由（マスターがポチッと）

## workspace
- v3マイグレーション済み: ~/workspace/ が正式workspace
- ~/.openclaw/workspace はシンボリックリンク

## 画像生成 構図・スタイルTips（2026-03-07発見）
- 背景refはキャラシートと必ずセットで渡す（キャラシートなしだと顔がブレる）
- 全体構図より**バストアップ＋「背景はぼんやり見える程度」**の方がドラマチックに仕上がる
- 被写界深度ボケも自然に再現される → キャラが主役の投稿に最適
- 合成っぽさを消す = キャラとbackgroundのスタイルを揃える（anime調bg→NOT photorealistic指定）
- 黄金パターン: 背景refで世界観を作り、クローズアップ＋ぼかしでキャラを主役に

## 社内マニュアル（branch_office 2026-03-07更新）
- 画像生成: refはニュアンス補完、外見定義はテキストで書く。両方揃えるのがベスト
- モデル選定: テキスト描画→gemini-3-pro-image-preview、キャラ生成→gemini-2.5-flash-image
- 画像管理: 生成→~/assets/tmp/ → 採用後→~/assets/images/ → 投稿済みは削除OK
- 命名規則: 小文字スネークケース、日時重要なら日付プレフィックス
- note投稿: teddy_on_webアカウント、API経由で下書き保存、公開は手動
- エージェント通信: sessions_send / sessions_spawnで他事業部と連携

## キャラシート
- ~/workspace/HR/charsheets/akiko_bizeny/main.jpg — 着物
- ~/workspace/HR/charsheets/akiko_bizeny/corporate.jpg — ビジネス
- ~/workspace/HR/charsheets/akiko_bizeny/casual.png — カーディガン
- ~/workspace/HR/charsheets/akiko_bizeny/dressup.png — エメラルドグリーンドレス＋ボレロ
- akiko_main.jpg (assets/tmp) — charsheetから切り出したメインイラスト、画像生成リファレンス用

## プロジェクト
- ~/projects/bizeny — 彰子LPサイト（チャットボット付き）
- ~/projects/bizendao.github.io — BizenDAO dapp

## BizenDAO Git運用ルール
- **masterへのマージはPRのみ** — 直接 `git merge` / `git push origin master` は絶対にしない
- staging で開発・確認 → マスターがPRを作成・承認してからマージ

## キャストプロンプト整理（2026-03-09）
- alice/jasmine: JSON構文エラー修正済み
- mephi/teddy: `anime girl with` → `character with` に変更
- master: `holding smartphone or laptop` 削除
- alice: `brown rabbit face leather bag,` 削除
- casts commit: ba63916

## OpenClaw cron最終形（2026-03-09、2026-03-15更新）
- 全IGルーティン・watchdog・dashboard等を完全削除
- 残存: morning_greeting(d57bf183) / X_daily_post_20h(649e5d96) の2本のみ

## ソネットcronフロー（2026-03-15更新）
- 毎日JST 20:00: 彰子がソネット作成 → labo-portalでアイキャッチ生成 → note下書き保存（bizenyakikoアカウント）
- 下書きURLをマスターにTelegram報告 → マスターが公開 → テディ🧸のRSSウォッチが自動でXにポスト
- X投稿案・Web intentは不要
- note投稿スクリプト: ~/workspace/scripts/post_note_draft.mjs
- Cookie: ~/.config/note/session.json（bizenyakikoアカウント）
- 金曜: オリジナルソネット（日仏英3言語）、金曜以外: 名作ソネット紹介
