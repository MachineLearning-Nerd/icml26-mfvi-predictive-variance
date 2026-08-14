# Source audit

## Paper artifacts

| Artifact | Value |
| --- | --- |
| Paper | *Gaussian Mean Field Variational Inference can Overestimate Predictive Variance* |
| Authors | James Odgers; Ben Riegler; Siddharth Swaroop; Vincent Fortuin |
| arXiv | [2606.25745](https://arxiv.org/abs/2606.25745), v1 |
| OpenReview | [RG7maF4bGu](https://openreview.net/forum?id=RG7maF4bGu) |
| PDF | `docs/primary.pdf`, 22 pages |
| PDF SHA-256 | `5347414ef5e950966cc90ef9567da99aaa89276b8946259b717af3639a7cab59` |
| Source archive SHA-256 | `5a5e8ba755d451526420170011c78e278fa472afc4325acbdc98858c420ef157` |
| Extracted source files | 30 |
| Main TeX | `source/arxiv/main.tex`, SHA-256 `2dfae2872507edad0b225121891ec1f24d76d4bf10a5ab6c1cdb63eeb490b1da` |
| Appendix TeX | `source/arxiv/app_proofs.tex`, SHA-256 `ca1d1d9546159520cb3337ca61b04b42d14516fedeeaa4a7ac21dde6081c57e9` |
| Source package | TeX, bibliography, styles, and paper figures; no executable author files |
| Record license | CC BY 4.0 as listed by the OpenReview record |

## Official implementation and data pins

The full-scale official path is externally pinned rather than copied into this repository:

- repository: `https://github.com/jamesacodgers/mfvi-cpe.git`
- commit: `98604c6e558127fb756529a2c9339c77ca1a9965`
- entry point: `upstream/uci_tr_inequ.py`
- entry-point SHA-256: `4c0968b190e69064e663732c76d1669b48404fd47bddfa633b0a510eaeb2ac4a`
- nine cached UCI input hashes: `sources.json`

The independent verifier does not import the official posterior implementation. The official implementation/data boundary is why the strict status remains `NOT_READY` even though the full-scale outputs are retained and cross-checked.

## Retained archive

`outputs/colab/RG7maF4bGu-colab-results.tar.gz` has SHA-256 `52a199c2c2bce9b84d312849e088cf44cdeaecd5812503286d33aba5065406b9`. Its required output members are listed in `sources.json`; the extracted copies in `outputs/` are independently hash-checked by the gate.
