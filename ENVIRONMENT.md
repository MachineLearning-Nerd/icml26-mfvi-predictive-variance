# Environment and verification boundary

## Recorded publication gate

The lightweight gate is run with the pinned requirements:

~~~sh
uv venv --python 3.12 .venv
uv pip install -r repro/requirements.txt
.venv/bin/python repro/src/publication_gate.py
~~~

It validates the committed source/PDF pins, independent synthetic and
full-scale result records, official provenance, source/independent trace
comparisons, evidence bundle, artifact manifest, focused tests, and public
file hygiene. It does not rerun all nine official datasets.

## Lightweight final-state check

After publication, run:

~~~sh
python3 verify_final.py
~~~

This verifier checks the live GitHub branch, canonical commit attribution,
paper and external-code pins, retained full-scale hashes, claim outcomes,
negative controls, nested artifact hashes, and the collection dossier. It
does not download external code or data and does not start a long computation.

## Full regeneration boundary

Full regeneration requires the separately pinned official checkout and all
nine cached UCI inputs. The exact bootstrap and provenance-guarded scripts
are documented in the repository README and <code>docs/PUBLICATION_GATE.md</code>.
