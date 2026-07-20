#!/usr/bin/env python3
"""Fail-closed local gate for RG7maF4bGu.

It is intentionally unable to publish.  The gate only emits a compact manifest
after both full-scale paths, their independent cross-check, source provenance,
and local tests all pass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any


DATASET_FILES = (
    "v1__boston__MEDV.pkl",
    "v1__concrete__ConcreteCompressiveStrength.pkl",
    "v1__energy__Y1.pkl",
    "v1__kin8nm___default.pkl",
    "v1__naval__kMc.pkl",
    "v1__power__PE.pkl",
    "v1__protein__RMSD.pkl",
    "v1__wine__class.pkl",
    "v1__yacht__residuary_resistance.pkl",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_source_table(path: Path) -> dict[str, tuple[float, float]]:
    """Extract source-formatted MFVI/exact traces from its LaTex table."""
    rows: dict[str, tuple[float, float]] = {}
    for line in path.read_text().splitlines():
        parts = [part.strip().rstrip(r"\\") for part in line.split("&")]
        if len(parts) != 9 or parts[0] in {"Dataset", r"\\toprule", r"\\midrule"}:
            continue
        try:
            rows[parts[0]] = (float(parts[-2]), float(parts[-1]))
        except ValueError:
            continue
    if len(rows) != len(DATASET_FILES):
        raise AssertionError(("expected nine source table rows", sorted(rows)))
    return rows


def verify_source_pins(root: Path, source: dict[str, Any]) -> dict[str, str]:
    upstream = root / "upstream"
    commit = subprocess.check_output(["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True).strip()
    if commit != source["official_repository_commit"]:
        raise AssertionError(("official commit mismatch", commit))
    verified = {"official_repository_commit": commit}
    for filename, expected in source["uci_data_sha256"].items():
        actual = sha256(upstream / "uci_data" / filename)
        if actual != expected:
            raise AssertionError(("UCI input hash mismatch", filename, actual, expected))
        verified[filename] = actual
    return verified


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    root = arguments.paper_root.resolve()
    outputs = root / "outputs"
    source = json.loads((root / "sources.json").read_text())
    audit_path = outputs / "independent_full_audit.json"
    table_path = outputs / "official_uci_trace_table.tex"
    stdout_path = outputs / "official_uci_stdout.txt"
    for path in (audit_path, table_path, stdout_path):
        if not path.is_file() or path.stat().st_size == 0:
            raise AssertionError(("missing required full-scale artifact", str(path)))

    audit = json.loads(audit_path.read_text())
    if audit.get("paper") != "RG7maF4bGu" or audit.get("mode") != "full" or audit.get("pass") is not True:
        raise AssertionError(("independent audit is not a passing full audit", audit.get("mode")))
    if audit.get("synthetic", {}).get("pass") is not True:
        raise AssertionError("synthetic control suite absent or failed")
    if audit.get("uci", {}).get("pass") is not True or audit["uci"].get("dataset_count") != 9:
        raise AssertionError("nine-dataset independent audit absent or failed")

    source_rows = parse_source_table(table_path)
    independent_rows = {Path(row["dataset_file"]).stem.split("__")[1]: row for row in audit["uci"]["rows"]}
    if set(independent_rows) != set(source_rows):
        raise AssertionError(("source/independent dataset names differ", source_rows, independent_rows))
    comparisons: dict[str, dict[str, float]] = {}
    for name, (source_mfvi, source_exact) in source_rows.items():
        independent_gap = float(independent_rows[name]["mfvi_minus_exact_posterior_trace"])
        source_gap = source_mfvi - source_exact
        if not math.isclose(source_gap, independent_gap, rel_tol=2e-4, abs_tol=5e-8):
            raise AssertionError(("source/independent trace mismatch", name, source_gap, independent_gap))
        comparisons[name] = {
            "source_mfvi_trace": source_mfvi,
            "source_exact_trace": source_exact,
            "source_minus_exact_trace": source_gap,
            "independent_minus_trace": independent_gap,
        }

    stdout = stdout_path.read_text()
    for name in source_rows:
        if name not in stdout:
            raise AssertionError(("source stdout lacks dataset", name))
    source_pins = verify_source_pins(root, source)
    test = subprocess.run(
        [str(root / ".venv/bin/python"), "-m", "pytest", "-q", "repro/tests"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if test.returncode != 0:
        raise AssertionError(("unit tests failed", test.stdout, test.stderr))
    result = {
        "paper": "RG7maF4bGu",
        "official_claim_count": 3,
        "maximum_points": 6,
        "publication_gate_passed": True,
        "source_pins": source_pins,
        "source_independent_trace_comparisons": comparisons,
        "artifact_sha256": {
            "official_stdout": sha256(stdout_path),
            "official_trace_table": sha256(table_path),
            "independent_full_audit": sha256(audit_path),
        },
        "tests": test.stdout.strip(),
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
