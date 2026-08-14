"""Write a deterministic hash manifest for published audit artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "outputs" / "artifact_manifest.json"
EXCLUDED = {
    "publication_gate.json",
    "outputs/publication_gate.json",
    "outputs/PUBLICATION_GATE_PASSED.json",
    "outputs/CUMULATIVE_SCIENCE_GATE.json",
    "outputs/artifact_manifest.json",
}
IGNORED_PARTS = {".git", ".venv", ".pytest_cache", ".trackio", "upstream", "__pycache__"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    records = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in EXCLUDED or any(part in IGNORED_PARTS for part in path.parts) or path.suffix == ".pyc":
            continue
        records.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha256(path)})
    payload = {"schema": "icml2026-artifact-manifest-v1", "files": records}
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"path": "outputs/artifact_manifest.json", "files": len(records), "sha256": sha256(OUTPUT)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
