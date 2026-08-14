# Gaussian Mean Field Variational Inference can Overestimate Predictive Variance

Clean-room audit and retained full-scale reproduction evidence for the ICML 2026 paper **Gaussian Mean Field Variational Inference can Overestimate Predictive Variance** by James Odgers, Ben Riegler, Siddharth Swaroop, and Vincent Fortuin.

The paper studies conjugate Bayesian linear regression. Its central message is that mean-field variational inference (MFVI) can underestimate posterior variance in parameter space while overestimating predictive variance, especially along directions emphasized by the training data. It also connects this effect to the cold posterior effect and validates the theory on synthetic and real-world regression tasks.

## Paper and source

- Paper: [arXiv:2606.25745](https://arxiv.org/abs/2606.25745)
- OpenReview: [RG7maF4bGu](https://openreview.net/forum?id=RG7maF4bGu)
- Pinned PDF: [`docs/primary.pdf`](docs/primary.pdf)
- Pinned TeX source: [`source/arxiv/`](source/arxiv/)
- Pinned official implementation: [`jamesacodgers/mfvi-cpe`](https://github.com/jamesacodgers/mfvi-cpe) at commit `98604c6e558127fb756529a2c9339c77ca1a9965`
- Provenance and SHA-256 values: [`sources.json`](sources.json) and [`docs/SOURCE_AUDIT.md`](docs/SOURCE_AUDIT.md)

## Audit result

The repository has a `SCOPED_PASS` publication gate. The full nine-dataset official output and independent NumPy/SciPy audit are retained, cross-checked, and hash-bound. The lightweight gate does not rerun the expensive official computation; a fresh full run still requires the separately pinned official checkout and UCI inputs.

| ID | Paper claim | Result | Evidence |
| --- | --- | --- | --- |
| C1 | MFVI can underestimate posterior variance while overestimating predictive variance. | `VERIFIED_SCOPED_SPHERICAL_PRIOR`; 144 synthetic systems and 9 UCI datasets pass the independent comparison; posterior-trace gaps are negative. | [`outputs/independent_full_audit.json`](outputs/independent_full_audit.json), `verify_mfvi.py` |
| C2 | Expected predictive variance is larger for MFVI on the training distribution. | `VERIFIED_SCOPED_EMPIRICAL_TRAINING_DISTRIBUTION`; minimum synthetic empirical gap `5.725297700025641e-8`, minimum UCI gap `1.035265794912767e-14`. | independent synthetic/UCI audit and the official nine-dataset trace table |
| C3 | The overestimation appears in concentrated directions. | `VERIFIED_SCOPED_FIRST_PRINCIPAL_DIRECTION`; minimum synthetic first-PC gap `9.375506445419605e-7`, minimum UCI first-PC gap `4.6049666600837724e-8`. | independent synthetic/UCI audit |

The audit also records the scope controls that keep these claims precise:

- an axis-aligned design is an exact equality case;
- a deterministic nonspherical-prior control reverses the first-PC gap to `-0.039114482356105526`, so the spherical-prior assumption is not optional;
- the independent reverse-KL optimizer agrees with the diagonal-precision formula;
- source-formatted traces and independent posterior-trace gaps agree for all nine UCI datasets.

The overall status is `VERIFIED_SCOPED_WITH_FULL_SCALE_RETAINED_ARTIFACTS`; strict status is `NOT_READY` because the external official checkout, cached inputs, and exact runtime are pinned but not reproduced inside this GitHub clone. No external competition score is claimed.

## How the claims are produced

1. `repro/src/verify_mfvi.py` independently computes the exact Gaussian posterior, the reverse-KL diagonal MFVI optimum, predictive-variance differences, principal directions, posterior traces, and negative controls using NumPy/SciPy. It does not import the author’s posterior implementation.
2. Its synthetic mode checks 144 rotated, non-axis-aligned spherical-prior systems across dimensions 2–64, an axis-aligned equality control, and a nonspherical-prior scope counterexample.
3. Its full mode checks all nine released UCI inputs after the source’s standardization convention and produces `outputs/independent_full_audit.json`.
4. `repro/src/run_official_uci.sh` is the provenance-guarded wrapper around the unmodified official `upstream/uci_tr_inequ.py` entry point. Its retained stdout/table/provenance files are cross-checked by `repro/src/prepublish_gate.py`.
5. `outputs/colab/RG7maF4bGu-colab-results.tar.gz` preserves the returned full-scale output archive. The publication gate verifies its hash and required members but does not silently treat the archive as a fresh run.
6. `repro/src/build_evidence_bundle.py` binds the source, PDF, claim contract, retained result files, and verifier code. `repro/src/artifact_manifest.py` binds every published artifact except self-referential gate files.
7. `repro/src/publication_gate.py` verifies the pinned paper/source artifacts, retained full-scale results, evidence bundle, manifest, focused tests, and public-file hygiene, then writes identical gate files at the root and under `outputs/`.

The detailed claim-to-evidence path is in [`docs/CLAIM_EVIDENCE.md`](docs/CLAIM_EVIDENCE.md).

## Reproduce the lightweight publication gate

```bash
uv venv --python 3.12 .venv
uv pip install -r repro/requirements.txt
.venv/bin/python repro/src/publication_gate.py
```

This command is intentionally lightweight and network-free after the committed artifacts are present. It validates the retained full-scale evidence; it does not run all nine official datasets.

## Re-run the full experiment

To regenerate the official path, obtain the external implementation and its cached UCI inputs, then pin them exactly as in [`sources.json`](sources.json):

```bash
git clone https://github.com/jamesacodgers/mfvi-cpe.git upstream
git -C upstream checkout --detach 98604c6e558127fb756529a2c9339c77ca1a9965
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python --index-url https://download.pytorch.org/whl/cu121 'torch==2.5.1+cu121'
uv pip install --python .venv/bin/python -r repro/requirements.txt
bash repro/src/run_official_uci.sh
bash repro/src/run_independent_uci.sh
.venv/bin/python repro/src/prepublish_gate.py --output outputs/prepublish_gate.json
```

The UCI input hashes, official entry-point hash, thread controls, and source/independent comparison are all fail-closed. `upstream/` is intentionally ignored and is not part of the published artifact set.

## Branches

The final repository has one branch: `main`. The original repository also had only `main`; no branch carried a distinct implementation or result. See [`docs/BRANCH_AUDIT.md`](docs/BRANCH_AUDIT.md).

## Citation

```bibtex
@article{odgers2026gaussian,
  title   = {Gaussian Mean Field Variational Inference can Overestimate Predictive Variance},
  author  = {Odgers, James and Riegler, Ben and Swaroop, Siddharth and Fortuin, Vincent},
  journal = {arXiv preprint arXiv:2606.25745},
  year    = {2026},
  url     = {https://arxiv.org/abs/2606.25745}
}
```

## Thank you

Thank you to James Odgers, Ben Riegler, Siddharth Swaroop, and Vincent Fortuin for making this careful analysis and its experimental artifacts available for independent study. This repository is an audit and reproduction record, not an official implementation or endorsement by the authors.

## Reproduction boundary

- The independent calculations are evidence for the paper’s claims, not machine-checked proofs.
- The arXiv source package is pinned locally and contains paper TeX/figures, not the complete executable experiment pipeline.
- The official implementation and nine UCI inputs are identified by exact commit and SHA-256 values but remain external to this clone.
- The Colab archive is retained and read back; the lightweight publication gate does not claim to regenerate its runtime or hardware state.
- Claims C2 and C3 retain the paper’s spherical-prior and empirical-training-distribution assumptions.
