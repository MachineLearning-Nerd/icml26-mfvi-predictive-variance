# Gaussian Mean Field Variational Inference can Overestimate Predictive Variance

Reproduction target for OpenReview `RG7maF4bGu`.

## Live jury contract

1. MFVI can underestimate posterior variance while overestimating predictive
   variance relative to the exact posterior.
2. For test points drawn from the training distribution, MFVI's expected
   predictive variance exceeds the exact posterior's.
3. The overestimation occurs in directions where the training data
   concentrates.

The contract was refreshed from the official challenge `claims.json` on
2026-07-20; its SHA-256 is
`af5ab2d62f786ae36861957cbd08b4188f6d4c86e67152becc661a9c5bbb9d57`.

## Scope

The reproduction will pin the official `jamesacodgers/mfvi-cpe` source at
`98604c6e558127fb756529a2c9339c77ca1a9965`, execute its complete cached-UCI
path, and independently verify the Bayesian-linear-regression identities.
Claims 2 and 3 must retain their spherical-prior and empirical-training-point
assumptions. Axis-aligned and anisotropic-prior controls are mandatory.

No claim is publishable until the complete local gate, independent checks,
Trackio evidence bundle, public GitHub push, and shared-queue publication have
all succeeded.

## Reproducible full-scale commands

The source execution needs only Torch, pandas, and Matplotlib. Bootstrap a
Python 3.12 environment with the same CPU-compatible source path used here:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python --index-url https://download.pytorch.org/whl/cu121 'torch==2.5.1+cu121'
uv pip install --python .venv/bin/python -r repro/requirements.txt
```

After verifying the pinned `upstream/` checkout and cached input hashes, the
two required full-scale commands are deliberately separate:

```bash
bash repro/src/run_official_uci.sh
uv run repro/src/verify_mfvi.py --mode uci --output outputs/independent_uci_audit.json
```

The first runs the official nine-dataset trace-inequality entry point. The
second independently recomputes all three jury mechanisms with NumPy/SciPy.
Both must pass, together with the final negative controls, before queueing.
