#!/usr/bin/env bash
# Run from the paper root.  This is intentionally the unmodified source entry
# point, with only CPU-thread and provenance guards around it.
set -euo pipefail

paper_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
upstream="$paper_root/upstream"
python_bin=${PYTHON_BIN:-"$paper_root/.venv/bin/python"}
expected_commit=98604c6e558127fb756529a2c9339c77ca1a9965
actual_commit=$(git -C "$upstream" rev-parse HEAD)
expected_script_sha=4c0968b190e69064e663732c76d1669b48404fd47bddfa633b0a510eaeb2ac4a
actual_script_sha=$(sha256sum "$upstream/uci_tr_inequ.py" | awk '{print $1}')

if [[ "$actual_commit" != "$expected_commit" ]]; then
  echo "official source commit mismatch: $actual_commit" >&2
  exit 2
fi
if [[ "$actual_script_sha" != "$expected_script_sha" ]]; then
  echo "official entry-point hash mismatch: $actual_script_sha" >&2
  exit 2
fi
if [[ ! -x "$python_bin" ]]; then
  echo "Python interpreter is not executable: $python_bin" >&2
  exit 2
fi

mkdir -p "$paper_root/outputs"
{
  printf 'official_repository_commit=%s\n' "$actual_commit"
  printf 'uci_tr_inequ_sha256=%s\n' "$actual_script_sha"
} > "$paper_root/outputs/official_uci_provenance.txt"
cd "$upstream"
export CUDA_VISIBLE_DEVICES=""
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export MPLBACKEND=Agg

"$python_bin" uci_tr_inequ.py \
  | tee "$paper_root/outputs/official_uci_stdout.txt"

cp figs/uci/tr_inequ_table.txt "$paper_root/outputs/official_uci_trace_table.tex"
sha256sum "$paper_root/outputs/official_uci_stdout.txt" \
  "$paper_root/outputs/official_uci_trace_table.tex" \
  "$paper_root/outputs/official_uci_provenance.txt" \
  > "$paper_root/outputs/official_uci_sha256.txt"
