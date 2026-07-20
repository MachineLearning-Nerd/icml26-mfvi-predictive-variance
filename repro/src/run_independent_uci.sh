#!/usr/bin/env bash
# Run from the paper root after the official source run.  This independent
# implementation intentionally imports no author posterior code.
set -euo pipefail

paper_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
python_bin=${PYTHON_BIN:-"$paper_root/.venv/bin/python"}
if [[ ! -x "$python_bin" ]]; then
  echo "Python interpreter is not executable: $python_bin" >&2
  exit 2
fi
mkdir -p "$paper_root/outputs"
cd "$paper_root"
export CUDA_VISIBLE_DEVICES=""
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

"$python_bin" repro/src/verify_mfvi.py \
  --mode full \
  --output outputs/independent_full_audit.json \
  | tee outputs/independent_full_audit_stdout.json

sha256sum outputs/independent_full_audit.json \
  outputs/independent_full_audit_stdout.json \
  > outputs/independent_full_audit_sha256.txt
