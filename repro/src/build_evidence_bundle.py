#!/usr/bin/env python3
"""Create a portable hash index for the MFVI audit evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "outputs" / "evidence_bundle.jsonl"
FILES = (
    "sources.json",
    "repro/configs/live_claims.json",
    "docs/primary.pdf",
    "source/arxiv/main.tex",
    "source/arxiv/app_proofs.tex",
    "docs/CLAIM_EVIDENCE.md",
    "outputs/colab/RG7maF4bGu-colab-results.tar.gz",
    "outputs/colab_synthetic_preflight.json",
    "outputs/independent_full_audit.json",
    "outputs/independent_full_audit_sha256.txt",
    "outputs/official_uci_provenance.txt",
    "outputs/official_uci_trace_table.tex",
    "outputs/official_uci_stdout.txt",
    "outputs/official_uci_sha256.txt",
    "outputs/prepublish_gate.json",
    "outputs/local_readback_gate.json",
    "repro/src/verify_mfvi.py",
    "repro/src/prepublish_gate.py",
    "repro/src/publication_gate.py",
    "repro/tests/test_verify_mfvi.py",
    "repro/tests/test_prepublish_gate.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    records = []
    for relative in FILES:
        path = ROOT / relative
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"required evidence is missing: {relative}")
        record = {"path": relative, "bytes": path.stat().st_size, "sha256": sha256(path)}
        if path.suffix == ".json":
            record["payload"] = json.loads(path.read_text())
        records.append(record)
    OUTPUT.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records))
    print(json.dumps({"paper": "RG7maF4bGu", "records": len(records), "bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
