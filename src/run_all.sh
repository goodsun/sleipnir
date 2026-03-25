#!/bin/bash
# run_all.sh - 全期間（または指定期間）のmemory/diaryを一括生成
#
# Usage:
#   bash src/run_all.sh                          # 全期間
#   bash src/run_all.sh --from 2026-02-07        # 開始日指定
#   bash src/run_all.sh --from 2026-02-07 --to 2026-02-28  # 期間指定
#   bash src/run_all.sh --agent mephi            # エージェント指定
#   bash src/run_all.sh --skip-existing          # 生成済みをスキップ

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AGENT="teddy"
FROM_DATE=""
TO_DATE=""
SKIP_EXISTING=false

# 引数パース
while [[ $# -gt 0 ]]; do
  case $1 in
    --agent) AGENT="$2"; shift 2 ;;
    --from)  FROM_DATE="$2"; shift 2 ;;
    --to)    TO_DATE="$2"; shift 2 ;;
    --skip-existing) SKIP_EXISTING=true; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# セッションディレクトリから存在する日付一覧を取得
SESSIONS_DIR=$(python3 -c "
import json
config = json.load(open('$SCRIPT_DIR/config/agents.json'))
agent = next(a for a in config['agents'] if a['name'] == '$AGENT')
print(agent['sessions_dir'])
")

echo "[run_all] エージェント: $AGENT"
echo "[run_all] セッションディレクトリ: $SESSIONS_DIR"

DATES=$(python3 - <<PYEOF
import os, json
from collections import defaultdict

sessions_dir = "$SESSIONS_DIR"
dates = set()
for fname in os.listdir(sessions_dir):
    if not (fname.endswith('.jsonl') or '.jsonl.' in fname):
        continue
    if fname.endswith('.lock') or fname.endswith('.tmp'):
        continue
    try:
        with open(os.path.join(sessions_dir, fname)) as f:
            for line in f:
                try:
                    d = json.loads(line.strip())
                except:
                    continue
                if d.get('type') == 'message':
                    ts = d.get('timestamp', '')
                    if ts:
                        dates.add(ts[:10])
    except:
        pass

for d in sorted(dates):
    print(d)
PYEOF
)

# 期間フィルタ
TOTAL=0
DONE=0
SKIPPED=0
FAILED=0
TOTAL_TIME=0

echo "[run_all] 処理開始"
echo ""

for date in $DATES; do
  # 期間フィルタ
  [[ -n "$FROM_DATE" && "$date" < "$FROM_DATE" ]] && continue
  [[ -n "$TO_DATE"   && "$date" > "$TO_DATE"   ]] && continue

  TOTAL=$((TOTAL + 1))

  # スキップ判定
  DIARY_PATH="$SCRIPT_DIR/output/$AGENT/agent-memory/$AGENT/diary/${date}.md"
  if $SKIP_EXISTING && [[ -f "$DIARY_PATH" ]]; then
    echo "[$date] スキップ（生成済み）"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # 生成
  START=$(date +%s)
  python3 "$SCRIPT_DIR/src/summarize.py" --date "$date" --agent "$AGENT" > /dev/null 2>&1
  EXIT_CODE=$?
  END=$(date +%s)
  ELAPSED=$((END - START))
  TOTAL_TIME=$((TOTAL_TIME + ELAPSED))

  if [[ $EXIT_CODE -eq 0 ]]; then
    echo "[$date] ✅ ${ELAPSED}秒"
    DONE=$((DONE + 1))
  else
    echo "[$date] ❌ 失敗"
    FAILED=$((FAILED + 1))
  fi
done

echo ""
echo "=== 完了 ==="
echo "処理: $TOTAL日 | 生成: $DONE | スキップ: $SKIPPED | 失敗: $FAILED"
echo "合計時間: ${TOTAL_TIME}秒"
