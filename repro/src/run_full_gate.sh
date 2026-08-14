#!/usr/bin/env bash
# The full-scale regeneration command; it does not run as part of the
# lightweight committed-evidence publication gate.
set -euo pipefail

paper_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
python_bin=${PYTHON_BIN:-"$paper_root/.venv/bin/python"}
cd "$paper_root"

bash repro/src/run_official_uci.sh
bash repro/src/run_independent_uci.sh
"$python_bin" repro/src/prepublish_gate.py --output outputs/prepublish_gate.json
