# Scoped reproduction report

## Verdict

| Claim | Verdict | Meaning |
| --- | --- | --- |
| C1 | <code>VERIFIED_SCOPED_SPHERICAL_PRIOR</code> | Independent calculations support the predictive-variance reversal across 144 synthetic systems and 9 retained UCI datasets under the paper's spherical-prior setup. |
| C2 | <code>VERIFIED_SCOPED_EMPIRICAL_TRAINING_DISTRIBUTION</code> | MFVI exceeds exact predictive variance on the declared training-distribution audit, with positive minimum gaps in synthetic and UCI records. |
| C3 | <code>VERIFIED_SCOPED_FIRST_PRINCIPAL_DIRECTION</code> | The first principal direction shows the stated overestimation in the declared scope; the nonspherical-prior control reverses it. |

The publication gate is <code>SCOPED_PASS</code> with overall status
<code>VERIFIED_SCOPED_WITH_FULL_SCALE_RETAINED_ARTIFACTS</code>. The strict
status is <code>NOT_READY</code>. No external score or author endorsement is
claimed.

## Established by the committed evidence

- 144 rotated non-axis-aligned spherical-prior synthetic systems pass.
- All 9 retained UCI datasets pass the independent audit and source-trace
  comparison.
- Minimum synthetic empirical gap:
  <code>5.725297700025641e-8</code>.
- Minimum UCI empirical gap:
  <code>1.035265794912767e-14</code>.
- Minimum synthetic first-PC gap:
  <code>9.375506445419605e-7</code>.
- Minimum UCI first-PC gap:
  <code>4.6049666600837724e-8</code>.
- The nonspherical-prior first-PC control is
  <code>-0.039114482356105526</code>.

## Not established

The finite and retained records do not machine-check the analytical proofs,
recreate the official checkout and UCI inputs inside this clone, or establish
the result under nonspherical priors or outside the empirical training
distribution.
