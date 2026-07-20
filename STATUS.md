# Status — RG7maF4bGu

## Current state

Claimed on 2026-07-20 after a fresh live-contract, ownership, source-pin, and
full-scale feasibility audit. The paper has three jury claims and six possible
points.

Another owner is currently running a three-core full-scale sweep on this
four-core host. Until that completes, this paper may only perform source,
provenance, scaffold, and other cheap deterministic work.

## Next action

The source pin is verified: `upstream/` is detached at
`98604c6e558127fb756529a2c9339c77ca1a9965`; the arXiv `2606.25745` source
tar, primary TeX, appendix TeX, and all nine cached UCI inputs are SHA-256
bound in `sources.json`. The released full-scale entry point is
`upstream/uci_tr_inequ.py`; it uses all nine cached datasets.

The source entry point itself is pinned at SHA-256
`4c0968b190e69064e663732c76d1669b48404fd47bddfa633b0a510eaeb2ac4a`.
The official wrapper records that hash and the detached commit beside its
outputs; the publication gate now rejects missing, malformed, stale, or
source-drifted run provenance before it can emit a manifest. The hardened
gate and verifier test suite passes 4/4; a fresh premature-gate control still
fails closed without writing a manifest.

The independent NumPy/SciPy synthetic gate has passed twice byte-for-byte.
It covers 144 non-axis-aligned spherical-prior BLR systems (dimensions 2--64),
with minimum empirical predictive-variance gap `5.7253e-8`, minimum first-PC
gap `9.3755e-7`, and no posterior-trace or conserved-precision-trace failure.
The independent BFGS reverse-KL optimum agrees with the diagonal-precision
formula; an axis-aligned design gives exact equality. A deterministic
nonspherical-prior control reverses the first-PC gap to `-0.0391145`, so that
scope cannot be silently broadened. Script SHA-256:
`f6c3d99b75f7061b9f5a3012001c5c900d87bbeabd9cca7b85eca070073e2b32`;
result SHA-256:
`a31a2f07f7ee5732418666f94f792bba2a6a6094bf90d66728fd1bced22d2322`.

Next, once CPU capacity is available, run the official nine-dataset entry
point and the separate NumPy verifier at the same full scale. Do not launch
either nine-dataset computation while the other owner's three-core sweep is
active.

The source environment is ready at `.venv` (Python 3.12, Torch
`2.5.1+cu121`, pandas `2.3.3`, Matplotlib `3.11.1`). Import validation confirms
that CUDA is disabled and that the released `uci_tr_inequ.py` path imports
cleanly. `repro/src/run_official_uci.sh` checks the detached source commit,
forces one CPU thread, executes that unmodified entry point, and snapshots its
stdout/table hashes for the future gate.

Trackio is initialized locally with required challenge tags and distinct Index,
Claim 1--3, Methods, Negative controls, and Conclusion pages. The Conclusion
is explicitly pending and unpinned. A fresh verifier pass confirms the official
commit plus all nine cached UCI data hashes before computation.

The full local gate is prepared but intentionally cannot pass without real
full-scale evidence. `repro/src/run_full_gate.sh` runs the source entry point,
the independent all-nine-dataset audit, and `prepublish_gate.py`; the latter
requires all three output artifacts, exact input/commit pins, a passing full
independent audit, agreement between source-formatted and independent trace
gaps for every dataset, and the local test suite. Three gate/unit tests pass.
A real premature-gate control was run: it rejected the absent
`outputs/independent_full_audit.json` and emitted no manifest.

## Publication state

The returned Colab evidence archive SHA-256 is
`52a199c2c2bce9b84d312849e088cf44cdeaecd5812503286d33aba5065406b9`.
Its complete nine-dataset source outputs and independent audit were extracted
without overwriting any local full-scale result. The local fail-closed readback
recomputed every artifact hash, source/data pin, source/independent trace
comparison, and test suite; it passed 4/4 tests. The final publication gate
also passes: 11 hash-bound evidence records (bundle SHA-256
`136bbe69d1ad591b8c3702d6b6a228e1504c7e9754d666b3a253d6c49e2a482d`),
required Trackio tags, a single pinned conclusion marker, and hygiene checks.

Gate-complete but not yet queued. Next: public GitHub push, then canonical
shared-backlog insertion. Do not start a publisher directly.

## External full-scale runner

The user may run the required full-scale gate in Google Colab using the
repository's `colab/mfvi_full_gate_colab.ipynb` and the separately generated
`../../colab-artifacts/RG7maF4bGu-colab-bundle.tar.gz`. That bundle includes
the detached author checkout (with Git metadata), all nine cached UCI inputs,
the source/entry-point hash pins, and the independent gate. It excludes local
virtual environments, Trackio state, cached results, and unrelated upstream
figures. The notebook returns an outputs-only archive; accept it only if its
included `prepublish_gate.json` passes every exact provenance, test, and
source-versus-independent check again locally.
