#!/usr/bin/env bash
# Run from the paper root.  This is intentionally the unmodified source entry
# point, with only CPU-thread and provenance guards around it.
set -euo pipefail

paper_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
upstream="$paper_root/upstream"
expected_commit=98604c6e558127fb756529a2c9339c77ca1a9965
actual_commit=$(git -C "$upstream" rev-parse HEAD)

if [[ "$actual_commit" != "$expected_commit" ]]; then
  echo "official source commit mismatch: $actual_commit" >&2
  exit 2
fi

mkdir -p "$paper_root/outputs"
cd "$upstream"
export CUDA_VISIBLE_DEVICES=""
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export MPLBACKEND=Agg

"$paper_root/.venv/bin/python" uci_tr_inequ.py \
  | tee "$paper_root/outputs/official_uci_stdout.txt"

cp figs/uci/tr_inequ_table.txt "$paper_root/outputs/official_uci_trace_table.tex"
sha256sum "$paper_root/outputs/official_uci_stdout.txt" \
  "$paper_root/outputs/official_uci_trace_table.tex" \
  > "$paper_root/outputs/official_uci_sha256.txt"
