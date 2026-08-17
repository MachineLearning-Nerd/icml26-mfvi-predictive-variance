# Source and provenance audit

## Paper and repository identity

- Paper: **Gaussian Mean Field Variational Inference can Overestimate Predictive Variance**
- Authors: James Odgers, Ben Riegler, Siddharth Swaroop, and Vincent Fortuin
- arXiv: [2606.25745v1](https://arxiv.org/abs/2606.25745)
- OpenReview: [RG7maF4bGu](https://openreview.net/forum?id=RG7maF4bGu)
- Former repository: <code>icml26-repro-RG7maF4bGu-mfvi-predictive-variance</code>
- Current repository: <code>icml26-mfvi-predictive-variance</code>
- Canonical URL: [MachineLearning-Nerd/icml26-mfvi-predictive-variance](https://github.com/MachineLearning-Nerd/icml26-mfvi-predictive-variance)

## Paper and source pins

- PDF: <code>docs/primary.pdf</code>, SHA-256
  <code>5347414ef5e950966cc90ef9567da99aaa89276b8946259b717af3639a7cab59</code>
- arXiv source archive: SHA-256
  <code>5a5e8ba755d451526420170011c78e278fa472afc4325acbdc98858c420ef157</code>
- Extracted source files: 30
- Main TeX: <code>source/arxiv/main.tex</code>, SHA-256
  <code>2dfae2872507edad0b225121891ec1f24d76d4bf10a5ab6c1cdb63eeb490b1da</code>
- Appendix TeX: <code>source/arxiv/app_proofs.tex</code>, SHA-256
  <code>ca1d1d9546159520cb3337ca61b04b42d14516fedeeaa4a7ac21dde6081c57e9</code>
- Challenge contract: <code>repro/configs/live_claims.json</code>, SHA-256
  <code>6b644fa280ddebeac75d0888e13134933ee7fe26366c34cb328b28c381b0cb5b</code>

## External implementation and data provenance

The official implementation is externally pinned at
<code>jamesacodgers/mfvi-cpe@98604c6e558127fb756529a2c9339c77ca1a9965</code>.
Its UCI entry point is hash-pinned at
<code>4c0968b190e69064e663732c76d1669b48404fd47bddfa633b0a510eaeb2ac4a</code>.
The nine cached UCI inputs are individually hash-bound in
<code>sources.json</code> but are not checked into this GitHub repository.

The local <code>repro/src/verify_mfvi.py</code> implementation is independent
NumPy/SciPy code and does not import the author's posterior implementation.
The retained Colab archive, official stdout/table, and independent audit are
read back and cross-checked by the publication gate.

## Boundary

Formal proof checking, bitwise recreation of the Colab/author environment,
and a new nine-dataset run from this clone are out of scope. The committed
full-scale result is retained evidence with explicit provenance, not a claim
that missing external inputs or the official checkout have been recreated.
