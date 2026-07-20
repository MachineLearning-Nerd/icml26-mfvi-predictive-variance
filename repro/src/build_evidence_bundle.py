#!/usr/bin/env python3
"""Create a hash-bound evidence index for the RG7 full-scale reproduction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "outputs/evidence_bundle.jsonl"
FILES = (
    "sources.json",
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
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    records = []
    for relative in FILES:
        path = ROOT / relative
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"required evidence is missing: {relative}")
        record: dict[str, object] = {
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        if path.suffix == ".json":
            record["payload"] = json.loads(path.read_text())
        records.append(record)
    OUTPUT.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records))
    result = {
        "paper": "RG7maF4bGu",
        "records": len(records),
        "bytes": OUTPUT.stat().st_size,
        "sha256": sha256(OUTPUT),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
