# Publication gate

## Lightweight committed-evidence gate

Run from the repository root:

```bash
uv venv --python 3.12 .venv
uv pip install -r repro/requirements.txt
.venv/bin/python repro/src/publication_gate.py
```

The gate performs focused, deterministic checks:

1. Verify the local claim contract, pinned PDF, 30-file arXiv source tree, main/appendix hashes, and official source metadata.
2. Verify the retained full independent audit, synthetic preflight, official provenance, nine-row official trace table, official stdout, and Colab output archive hash/members.
3. Recompute the source/independent trace comparison from the retained outputs without launching the full nine-dataset run.
4. Run the four focused tests.
5. Rebuild and verify the evidence bundle and all-artifact manifest.
6. Check public-file hygiene and ensure no hidden experiment-state dependency is required.
7. Write byte-identical records to `publication_gate.json`, `outputs/publication_gate.json`, `outputs/PUBLICATION_GATE_PASSED.json`, and `outputs/CUMULATIVE_SCIENCE_GATE.json`.

The gate result is `SCOPED_PASS`, overall `VERIFIED_SCOPED_WITH_FULL_SCALE_RETAINED_ARTIFACTS`, strict `NOT_READY`.

## Full regeneration gate

When the externally pinned official checkout and UCI inputs are available, run:

```bash
bash repro/src/run_official_uci.sh
bash repro/src/run_independent_uci.sh
.venv/bin/python repro/src/prepublish_gate.py --output outputs/prepublish_gate.json
```

This is the expensive path. `prepublish_gate.py` fails closed on source drift, missing inputs, malformed provenance, missing datasets, source/independent trace disagreement, or test failure. Its output is retained as evidence; the lightweight publication gate deliberately does not rerun it.
