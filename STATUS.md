# Audit status — Gaussian Mean Field Variational Inference can Overestimate Predictive Variance

Updated 2026-08-14 for OpenReview `RG7maF4bGu` / arXiv `2606.25745`.

## Current state

- Publication gate: `SCOPED_PASS`
- Overall status: `VERIFIED_SCOPED_WITH_FULL_SCALE_RETAINED_ARTIFACTS`
- Strict status: `NOT_READY`
- Official paper claims: 3
- Local claim units: 3
- External score: not claimed
- Final branch: `main`

The repository now contains the pinned arXiv source/PDF, a local claim contract, the independent audit code, the retained official nine-UCI output, the independent nine-UCI audit, and a deterministic readback gate. The gate validates the committed results without rerunning the full-scale computation.

## Evidence summary

| Measure | Result |
| --- | --- |
| Synthetic systems | 144 rotated non-axis-aligned spherical-prior systems |
| Synthetic empirical predictive-variance gap | minimum `5.725297700025641e-8` |
| Synthetic first-PC gap | minimum `9.375506445419605e-7` |
| Synthetic posterior-trace gap | maximum `-0.000458023816002061` |
| UCI datasets | 9, all pass independent checks |
| UCI empirical predictive-variance gap | minimum `1.035265794912767e-14` |
| UCI first-PC gap | minimum `4.6049666600837724e-8` |
| Scope control | nonspherical first-PC gap `-0.039114482356105526` |
| Official/independent agreement | all nine source trace gaps pass the declared tolerance |

## Reproduction boundary

The official implementation is pinned to commit `98604c6e558127fb756529a2c9339c77ca1a9965`, and every released UCI input is hash-bound in `sources.json`. Those external inputs are not checked into this repository. The committed Colab output archive and independent result are retained, so the publication gate is an evidence readback gate rather than a new nine-dataset run.

## Commands

Lightweight verification:

```bash
.venv/bin/python repro/src/publication_gate.py
```

Full regeneration, when the external checkout and inputs are available, is documented in [`README.md`](README.md) and [`docs/PUBLICATION_GATE.md`](docs/PUBLICATION_GATE.md).
