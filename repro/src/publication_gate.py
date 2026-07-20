#!/usr/bin/env python3
"""Final local gate before GitHub push and canonical HF queue insertion."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PAPER = "RG7maF4bGu"
BUNDLE = ROOT / "outputs/evidence_bundle.jsonl"
PREPUBLISH = ROOT / "outputs/prepublish_gate.json"
READBACK = ROOT / "outputs/local_readback_gate.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_bundle() -> dict[str, Any]:
    records = [json.loads(line) for line in BUNDLE.read_text().splitlines() if line]
    if len(records) != 11:
        raise RuntimeError(f"expected 11 evidence records, found {len(records)}")
    for record in records:
        path = ROOT / record["path"]
        if not path.is_file() or path.stat().st_size != record["bytes"]:
            raise RuntimeError(f"bundle size mismatch: {record['path']}")
        if sha256(path) != record["sha256"]:
            raise RuntimeError(f"bundle hash mismatch: {record['path']}")
        if "payload" in record and json.loads(path.read_text()) != record["payload"]:
            raise RuntimeError(f"bundle JSON payload mismatch: {record['path']}")
    return {"records": len(records), "bytes": BUNDLE.stat().st_size, "sha256": sha256(BUNDLE)}


def verify_results() -> dict[str, Any]:
    remote = json.loads(PREPUBLISH.read_text())
    local = json.loads(READBACK.read_text())
    for result in (remote, local):
        if result.get("paper") != PAPER or result.get("publication_gate_passed") is not True:
            raise RuntimeError("full-scale prepublication gate is not passing")
        if result.get("official_claim_count") != 3 or result.get("maximum_points") != 6:
            raise RuntimeError("wrong live contract in prepublication gate")
    if remote["artifact_sha256"] != local["artifact_sha256"]:
        raise RuntimeError("Colab and local readback artifact hashes differ")
    return {
        "colab_gate_sha256": sha256(PREPUBLISH),
        "local_readback_gate_sha256": sha256(READBACK),
        "artifact_sha256": remote["artifact_sha256"],
    }


def verify_trackio() -> dict[str, Any]:
    metadata = json.loads((ROOT / ".trackio/metadata.json").read_text())
    expected_space = f"DineshAI/{PAPER}"
    if metadata.get("space_id") != expected_space:
        raise RuntimeError("incorrect Trackio Space target")
    if set(metadata.get("tags", [])) != {"icml2026-repro", f"paper-{PAPER}"}:
        raise RuntimeError("required Trackio tags missing")
    matches = [
        row
        for row in metadata.get("local_path_artifacts", [])
        if row.get("path") == "outputs/evidence_bundle.jsonl"
    ]
    if len(matches) != 1 or matches[0].get("size") != BUNDLE.stat().st_size:
        raise RuntimeError("evidence bundle is not registered exactly once")
    conclusion = ROOT / ".trackio/logbook/pages/conclusion/page.md"
    marker = f"FULL_GATE_READY: {PAPER}"
    text = conclusion.read_text()
    if marker not in text:
        raise RuntimeError("pinned conclusion marker missing")
    cells = [json.loads(line) for line in text.splitlines() if line.startswith("{")]
    if sum(bool(cell.get("pinned")) for cell in cells) != 1:
        raise RuntimeError("Conclusion must contain exactly one pinned cell")
    return {"space_id": expected_space, "artifact_bytes": BUNDLE.stat().st_size, "pinned_conclusion_cells": 1}


def hygiene() -> dict[str, Any]:
    secret = re.compile(r"(?i)(hf_[a-z0-9]{20,}|github_pat_[a-z0-9_]{20,}|api[_-]?key\\s*[:=]\\s*['\"][^'\"]+)")
    suffixes = {".py", ".sh", ".json", ".jsonl", ".md", ".txt", ".toml", ".yaml", ".yml"}
    absolute_prefix = "/" + "home" + "/dineshai/"
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", ".venv", ".trackio", "upstream", "__pycache__"} for part in path.parts):
            continue
        if path.suffix.lower() in suffixes:
            text = path.read_text(errors="replace")
            if secret.search(text) or absolute_prefix in text:
                hits.append(path.relative_to(ROOT).as_posix())
    if hits:
        raise RuntimeError(f"hygiene failure: {hits}")
    return {"passed": True, "text_files_scanned": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/PUBLICATION_GATE_PASSED.json")
    arguments = parser.parse_args()
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "repro/tests"], cwd=ROOT, text=True, capture_output=True)
    if tests.returncode:
        raise RuntimeError(tests.stdout + tests.stderr)
    result = {
        "paper": PAPER,
        "official_claim_count": 3,
        "maximum_points": 6,
        "tests_passed": True,
        "publication_gate_passed": True,
        "results": verify_results(),
        "bundle": verify_bundle(),
        "trackio": verify_trackio(),
        "hygiene": hygiene(),
        "tests": tests.stdout.strip(),
    }
    arguments.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
