# Claim-to-evidence map

The local contract in [`repro/configs/live_claims.json`](../repro/configs/live_claims.json) mirrors the three paper claims. Every result below is scoped to the paper’s conjugate Bayesian linear-regression setting and its stated spherical-prior/training-distribution assumptions.

| ID | Claim | Producer path | Evidence | Limits |
| --- | --- | --- | --- | --- |
| C1 | MFVI can have smaller parameter-posterior variance but larger predictive variance than the exact posterior. | `verify_mfvi.py` → `audit_system()` → `outputs/independent_full_audit.json` | 144 synthetic spherical-prior systems and 9 UCI datasets pass; synthetic maximum MFVI-minus-exact posterior trace gap is `-0.000458023816002061`. | Finite double-precision calculations do not replace the analytical proof. |
| C2 | On training-distribution test points, MFVI’s expected predictive variance is larger. | `verify_mfvi.py` → `audit_synthetic()` and `audit_uci()` | Minimum empirical gap is `5.725297700025641e-8` on synthetic systems and `1.035265794912767e-14` across UCI. | The result uses the empirical training distribution and spherical prior; it is not a universal statement over arbitrary test distributions or priors. |
| C3 | The overestimation appears in concentrated directions. | `verify_mfvi.py` → first eigenvector of the empirical feature covariance | Minimum first-PC gap is `9.375506445419605e-7` synthetic and `4.6049666600837724e-8` UCI. | “Concentrated direction” is operationalized here as the first empirical principal direction. A nonspherical-prior control reverses the sign, so the prior scope is material. |

## Controls

- `axis_aligned_equality_control` gives exactly zero MFVI-minus-exact predictive gap, posterior-trace gap, and optimizer error.
- `nonspherical_prior_scope_control` gives first-PC gap `-0.039114482356105526`; it is a deliberate scope boundary, not a failed test.
- `reverse_kl_stationarity_error` and `optimizer_log_diagonal_error` check the analytic diagonal reverse-KL optimum against an independent BFGS calculation.
- `prepublish_gate.py` parses the official source-formatted table, checks all nine dataset names, and compares the official trace gaps with the independent audit.
- `test_prepublish_gate.py` includes a malformed-provenance failure control; `test_verify_mfvi.py` includes the axis-aligned equality and reverse-KL stationarity checks.

## Full-scale evidence path

```text
official mfvi-cpe@98604c6
  -> run_official_uci.sh
  -> official_uci_stdout.txt + official_uci_trace_table.tex + provenance
                         \
                          -> prepublish_gate.py
independent verify_mfvi.py --mode full
  -> independent_full_audit.json
                         /
Colab results archive + local_readback_gate.json
  -> evidence bundle -> publication gate
```

The archive at `outputs/colab/RG7maF4bGu-colab-results.tar.gz` is a retained output artifact. The publication gate verifies its SHA-256 and required members, but does not claim to rerun the official path in a fresh clone.
