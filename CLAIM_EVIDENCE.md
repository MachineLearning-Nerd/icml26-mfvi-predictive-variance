# Claim-to-evidence audit

The repository has three official paper claims. Each claim is checked by an
independent NumPy/SciPy implementation and compared with the retained
official nine-dataset output where applicable.

| Claim | Paper statement | Producer and evidence | Result | Boundary |
| --- | --- | --- | --- | --- |
| C1 | MFVI can underestimate posterior variance while overestimating predictive variance. | <code>repro/src/verify_mfvi.py</code> computes the exact Gaussian posterior, reverse-KL diagonal MFVI optimum, predictive variances, and posterior traces. <code>outputs/independent_full_audit.json</code> records 144 synthetic systems and 9 UCI datasets. | <code>VERIFIED_SCOPED_SPHERICAL_PRIOR</code> | The result is scoped to the paper's spherical-prior setup; the nonspherical control reverses the first-PC gap. |
| C2 | Expected predictive variance is larger for MFVI on the training distribution. | The independent synthetic/UCI audit compares training-distribution predictive variance on all retained datasets; source trace tables are cross-checked by <code>outputs/local_readback_gate.json</code>. | <code>VERIFIED_SCOPED_EMPIRICAL_TRAINING_DISTRIBUTION</code> | The empirical-training-distribution assumption remains part of the claim, and the official inputs are external pins rather than checked-in data. |
| C3 | The overestimation appears in concentrated directions. | The same independent audit computes the first principal direction of the design covariance and checks the retained UCI traces against the official source table. | <code>VERIFIED_SCOPED_FIRST_PRINCIPAL_DIRECTION</code> | This is not a claim about every prior or every direction; the nonspherical-prior negative control is retained. |

## Production order

~~~text
pinned paper/source and external provenance
  -> verify_mfvi.py synthetic audit
  -> verify_mfvi.py full UCI audit
  -> retained official/Colab artifact readback
  -> source/independent trace comparison
  -> focused pytest
  -> evidence bundle and artifact manifest
  -> lightweight publication gate
~~~

The publication gate is a retained-artifact gate. It validates the committed
full-scale results and their provenance, but does not silently rerun the
external official checkout or nine UCI computations.
