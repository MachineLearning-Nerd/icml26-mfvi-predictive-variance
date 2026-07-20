# Colab full-scale runner

`RG7maF4bGu-colab-bundle.tar.gz` is a self-contained input bundle for the
MFVI predictive-variance reproduction. It contains the exact detached author
checkout (including its Git metadata), all nine released cached UCI inputs,
the independent NumPy/SciPy verifier, source hashes, tests, and the
fail-closed publication gate.

1. Open `mfvi_full_gate_colab.ipynb` in a fresh Google Colab runtime.
2. Upload the input bundle when the first notebook cell asks for it.
3. Run every cell in order. The full-gate cell is deliberately sequential:
   it runs the unmodified author entry point over all nine datasets, then the
   independent full verifier, then the exact provenance/test/cross-check gate.
4. Download the generated `RG7maF4bGu-colab-results.tar.gz` and upload it
   back here. It contains only `outputs/`, including `prepublish_gate.json`,
   raw source stdout/table, provenance, and the independent audit.

Do not edit `upstream/`, `sources.json`, or `repro/` in Colab. Any such drift
causes the gate to fail. GPU is unnecessary: the author path and independent
audit are intentionally CPU-only and set one BLAS/OpenMP thread for stable
results. The source uses all nine released UCI datasets; no subset or toy
fallback is accepted.
