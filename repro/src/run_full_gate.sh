#!/usr/bin/env bash
# The only full-scale command to capture in Trackio once CPU capacity is free.
set -euo pipefail

paper_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$paper_root"

bash repro/src/run_official_uci.sh
bash repro/src/run_independent_uci.sh
.venv/bin/python repro/src/prepublish_gate.py --output outputs/prepublish_gate.json
