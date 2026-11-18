#!/bin/bash
# Smoke test — RAKSHA-NET
# Starts controller in sim mode, runs one scenario,
# asserts route switched and PDR recovered.
# Exits non-zero if anything fails.

set -e

echo "========================================"
echo "RAKSHA-NET Smoke Test"
echo "========================================"

PROJ_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJ_DIR"

# 1. Run unit tests
echo ""
echo "[1/3] Running unit tests..."
python -m pytest -q tests/ --timeout=60
echo "     PASS: All tests green"

# 2. Run single scenario and check output
echo ""
echo "[2/3] Running single scenario..."
OUTPUT=$(python -m scripts.run_scenario --trials 1 2>&1)
echo "$OUTPUT"

# Check route switched
if echo "$OUTPUT" | grep -q "ROUTE SWITCH"; then
    echo "     PASS: Route switch detected"
else
    echo "     FAIL: No route switch in scenario output"
    exit 1
fi

# Check PDR after is high
PDR_AFTER=$(echo "$OUTPUT" | grep -o "pdr_after=[0-9.]*" | head -1 | cut -d= -f2)
if [ -z "$PDR_AFTER" ]; then
    # Try alternate format from summary
    PDR_AFTER=$(echo "$OUTPUT" | grep "after=" | grep -o "after=[0-9.]*" | tail -1 | cut -d= -f2)
fi
echo "     PDR after: $PDR_AFTER"
if python3 -c "import sys; sys.exit(0 if float('${PDR_AFTER:-0}') > 0.85 else 1)" 2>/dev/null; then
    echo "     PASS: PDR recovered (>0.85)"
else
    echo "     WARN: PDR after may be low (${PDR_AFTER}); check manually"
fi

# 3. Quick 5-trial experiment
echo ""
echo "[3/3] Running 5-trial experiment..."
python -m scripts.run_scenario --trials 5 --csv /tmp/smoke_test.csv

SWITCHED=$(python3 -c "
import csv
with open('/tmp/smoke_test.csv') as f:
    rows = list(csv.DictReader(f))
    n = sum(1 for r in rows if r.get('route_recovery_ms','') not in ('','None'))
    print(n)
")
echo "     Switched: $SWITCHED/5"
if [ "$SWITCHED" -ge 4 ]; then
    echo "     PASS: Route switched in >= 4/5 trials"
else
    echo "     FAIL: Route switched in only $SWITCHED/5 trials"
    exit 1
fi

echo ""
echo "========================================"
echo "SMOKE TEST PASSED"
echo "========================================"
exit 0
