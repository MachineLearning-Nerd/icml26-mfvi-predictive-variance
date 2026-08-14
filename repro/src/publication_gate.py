#!/usr/bin/env python3
"""Validate the committed MFVI evidence without rerunning the full UCI job."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs"
PAPER = "RG7maF4bGu"
ARXIV = "2606.25745"
CONTRACT_SHA256 = "6b644fa280ddebeac75d0888e13134933ee7fe26366c34cb328b28c381b0cb5b"
PDF_SHA256 = "5347414ef5e950966cc90ef9567da99aaa89276b8946259b717af3639a7cab59"
SOURCE_SHA256 = "5a5e8ba755d451526420170011c78e278fa472afc4325acbdc98858c420ef157"
MAIN_TEX_SHA256 = "2dfae2872507edad0b225121891ec1f24d76d4bf10a5ab6c1cdb63eeb490b1da"
APPENDIX_TEX_SHA256 = "ca1d1d9546159520cb3337ca61b04b42d14516fedeeaa4a7ac21dde6081c57e9"
ARCHIVE_SHA256 = "52a199c2c2bce9b84d312849e088cf44cdeaecd5812503286d33aba5065406b9"
BUNDLE_PATHS = (
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
ARCHIVE_MEMBERS = {
    "outputs/independent_full_audit.json",
    "outputs/official_uci_stdout.txt",
    "outputs/official_uci_trace_table.tex",
    "outputs/prepublish_gate.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_source() -> dict:
    source = json.loads((ROOT / "sources.json").read_text())
    paper = source["paper"]
    challenge = source["challenge_contract"]
    arxiv = source["arxiv_source"]
    artifact = source["source_artifact"]
    assert paper["openreview_id"] == PAPER and paper["arxiv_id"] == ARXIV
    contract = ROOT / challenge["local_path"]
    assert challenge["local_sha256"] == CONTRACT_SHA256 and sha256(contract) == CONTRACT_SHA256
    source_root = ROOT / arxiv["local_root"]
    source_files = [path for path in source_root.rglob("*") if path.is_file()]
    assert len(source_files) == arxiv["file_count"] == 30
    assert sha256(ROOT / arxiv["main_tex"]) == MAIN_TEX_SHA256
    assert sha256(ROOT / arxiv["appendix_tex"]) == APPENDIX_TEX_SHA256
    pdf = ROOT / artifact["path"]
    assert artifact["pages"] == 22 and sha256(pdf) == PDF_SHA256
    executable = [path.relative_to(source_root).as_posix() for path in source_files if path.suffix in {".py", ".ipynb", ".sh", ".R", ".jl"}]
    assert executable == []
    assert source["official_repository_commit"] == "98604c6e558127fb756529a2c9339c77ca1a9965"
    assert source["official_uci_script_sha256"] == "4c0968b190e69064e663732c76d1669b48404fd47bddfa633b0a510eaeb2ac4a"
    return {
        "arxiv": ARXIV,
        "source_files": len(source_files),
        "source_sha256": SOURCE_SHA256,
        "main_tex_sha256": MAIN_TEX_SHA256,
        "appendix_tex_sha256": APPENDIX_TEX_SHA256,
        "pdf_sha256": PDF_SHA256,
        "official_repository_commit": source["official_repository_commit"],
        "official_uci_script_sha256": source["official_uci_script_sha256"],
    }


def parse_provenance(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text().splitlines():
        key, separator, value = line.partition("=")
        assert separator and key and value and key not in values
        values[key] = value
    return values


def parse_trace_table(path: Path) -> dict[str, tuple[float, float]]:
    rows = {}
    for line in path.read_text().splitlines():
        parts = [part.strip().rstrip("\\") for part in line.split("&")]
        if len(parts) != 9 or parts[0] in {"Dataset", "\\toprule", "\\midrule"}:
            continue
        try:
            rows[parts[0]] = (float(parts[-2]), float(parts[-1]))
        except ValueError:
            continue
    assert len(rows) == 9
    return rows


def verify_full_scale() -> dict:
    source = json.loads((ROOT / "sources.json").read_text())
    audit = json.loads((OUTPUTS / "independent_full_audit.json").read_text())
    assert audit["paper"] == PAPER and audit["mode"] == "full" and audit["pass"]
    synthetic = audit["synthetic"]
    assert synthetic["pass"] and synthetic["system_count"] == 144
    assert synthetic["minimum_empirical_gap"] == 5.725297700025641e-8
    assert synthetic["minimum_first_pc_gap"] == 9.375506445419605e-7
    assert synthetic["maximum_trace_gap"] == -0.000458023816002061
    assert synthetic["axis_aligned_equality_control"]["empirical_mfvi_minus_exact_predictive_variance"] == 0.0
    assert synthetic["nonspherical_prior_scope_control"]["first_pc_mfvi_minus_exact_predictive_variance"] < -0.039
    uci = audit["uci"]
    assert uci["pass"] and uci["dataset_count"] == 9
    assert uci["minimum_empirical_gap"] == 1.035265794912767e-14
    assert uci["minimum_first_pc_gap"] == 4.6049666600837724e-8
    assert uci["maximum_trace_gap"] == -8.480897643170174e-9
    assert all(row["empirical_mfvi_minus_exact_predictive_variance"] >= 0 for row in uci["rows"])
    assert all(row["first_pc_mfvi_minus_exact_predictive_variance"] >= 0 for row in uci["rows"])
    assert all(row["mfvi_minus_exact_posterior_trace"] <= 0 for row in uci["rows"])

    provenance = parse_provenance(OUTPUTS / "official_uci_provenance.txt")
    assert provenance == {
        "official_repository_commit": source["official_repository_commit"],
        "uci_tr_inequ_sha256": source["official_uci_script_sha256"],
    }
    table = parse_trace_table(OUTPUTS / "official_uci_trace_table.tex")
    independent_rows = {Path(row["dataset_file"]).stem.split("__")[1]: row for row in uci["rows"]}
    assert set(table) == set(independent_rows)
    comparisons = {}
    for name, (mfvi_trace, exact_trace) in table.items():
        source_gap = mfvi_trace - exact_trace
        independent_gap = float(independent_rows[name]["mfvi_minus_exact_posterior_trace"])
        assert abs(source_gap - independent_gap) <= max(5e-8, 2e-4 * abs(independent_gap))
        comparisons[name] = {"source_gap": source_gap, "independent_gap": independent_gap}
    stdout = (OUTPUTS / "official_uci_stdout.txt").read_text()
    assert all(name in stdout for name in table)

    for path in (OUTPUTS / "prepublish_gate.json", OUTPUTS / "local_readback_gate.json"):
        record = json.loads(path.read_text())
        assert record["paper"] == PAPER and record["publication_gate_passed"]
        assert record["official_claim_count"] == 3 and record["maximum_points"] == 6
    prepublish = json.loads((OUTPUTS / "prepublish_gate.json").read_text())
    readback = json.loads((OUTPUTS / "local_readback_gate.json").read_text())
    assert prepublish["artifact_sha256"] == readback["artifact_sha256"]

    archive = ROOT / source["retained_artifacts"]["colab_archive"]["path"]
    assert sha256(archive) == ARCHIVE_SHA256
    with tarfile.open(archive, "r:gz") as handle:
        members = {member.name for member in handle.getmembers()}
    assert ARCHIVE_MEMBERS <= members
    return {
        "synthetic_systems": synthetic["system_count"],
        "uci_datasets": uci["dataset_count"],
        "minimum_synthetic_empirical_gap": synthetic["minimum_empirical_gap"],
        "minimum_synthetic_first_pc_gap": synthetic["minimum_first_pc_gap"],
        "minimum_uci_empirical_gap": uci["minimum_empirical_gap"],
        "minimum_uci_first_pc_gap": uci["minimum_first_pc_gap"],
        "trace_comparisons": comparisons,
        "independent_full_audit_sha256": sha256(OUTPUTS / "independent_full_audit.json"),
        "colab_archive_sha256": sha256(archive),
        "prepublish_gate_sha256": sha256(OUTPUTS / "prepublish_gate.json"),
        "local_readback_gate_sha256": sha256(OUTPUTS / "local_readback_gate.json"),
    }


def verify_bundle() -> dict:
    bundle = OUTPUTS / "evidence_bundle.jsonl"
    records = [json.loads(line) for line in bundle.read_text().splitlines() if line]
    assert len(records) == len(BUNDLE_PATHS)
    assert tuple(record["path"] for record in records) == BUNDLE_PATHS
    for record in records:
        path = ROOT / record["path"]
        assert path.is_file() and path.stat().st_size == record["bytes"]
        assert sha256(path) == record["sha256"]
        if "payload" in record:
            assert json.loads(path.read_text()) == record["payload"]
    return {"records": len(records), "bytes": bundle.stat().st_size, "sha256": sha256(bundle)}


def verify_manifest() -> dict:
    manifest_path = OUTPUTS / "artifact_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    records = manifest["files"]
    assert len(records) >= 60
    seen = set()
    for record in records:
        assert record["path"] not in seen
        seen.add(record["path"])
        path = ROOT / record["path"]
        assert path.is_file() and path.stat().st_size == record["bytes"]
        assert sha256(path) == record["sha256"]
    assert "source/arxiv/main.tex" in seen and "docs/primary.pdf" in seen
    assert not any(".trackio" in path or path.startswith("upstream/") for path in seen)
    return {"files": len(records), "sha256": sha256(manifest_path)}


def hygiene() -> dict:
    secret = re.compile(r"(?i)(hf_[a-z0-9]{20,}|github_pat_[a-z0-9_]{20,}|api[_-]?key\s*[:=]\s*['\"][^'\"]+)")
    private_path = "/" + "home" + "/dineshai/"
    forbidden = {"Dinesh" + "AI/", "trackio"}
    gate_paths = {
        "publication_gate.json",
        "outputs/publication_gate.json",
        "outputs/PUBLICATION_GATE_PASSED.json",
        "outputs/CUMULATIVE_SCIENCE_GATE.json",
    }
    policy_paths = {
        "repro/src/publication_gate.py",
        "repro/src/artifact_manifest.py",
    }
    bad = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT).as_posix()
        if not path.is_file() or relative in gate_paths or relative in policy_paths or any(part in {".git", ".venv", ".pytest_cache", "upstream", "__pycache__"} for part in path.parts):
            continue
        if path.suffix.lower() not in {".py", ".sh", ".json", ".jsonl", ".md", ".txt", ".toml", ".yaml", ".yml"}:
            continue
        text = path.read_text(errors="replace")
        if secret.search(text) or private_path in text or any(fragment.lower() in text.lower() for fragment in forbidden):
            bad.append(relative)
    assert not bad, bad
    return {"passed": True}


def main() -> None:
    environment = {**os.environ, "PYTHONPATH": str(ROOT / "repro" / "src")}
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "repro/tests"], cwd=ROOT, env=environment, text=True, capture_output=True)
    if tests.returncode:
        raise RuntimeError(tests.stdout + tests.stderr)
    source = verify_source()
    full_scale = verify_full_scale()
    run("repro/src/build_evidence_bundle.py")
    run("repro/src/artifact_manifest.py")
    gate = {
        "gate_version": "publication-v2",
        "paper": PAPER,
        "arxiv": ARXIV,
        "status": "SCOPED_PASS",
        "overall_status": "VERIFIED_SCOPED_WITH_FULL_SCALE_RETAINED_ARTIFACTS",
        "strict_status": "NOT_READY",
        "publication_gate_passed": True,
        "official_claim_count": 3,
        "local_claim_units": 3,
        "claim_outcomes": [
            "VERIFIED_SCOPED_SPHERICAL_PRIOR",
            "VERIFIED_SCOPED_EMPIRICAL_TRAINING_DISTRIBUTION",
            "VERIFIED_SCOPED_FIRST_PRINCIPAL_DIRECTION",
        ],
        "source": source,
        "full_scale_evidence": full_scale,
        "evidence_bundle": verify_bundle(),
        "artifact_manifest": verify_manifest(),
        "hygiene": hygiene(),
        "tests_passed": True,
        "tests": "python -m pytest -q repro/tests: passed",
        "limitations": [
            "The finite independent calculations are evidence for, not machine-checked replacements of, the paper's proofs.",
            "The official implementation and nine cached UCI inputs are externally pinned and are not checked into this clone.",
            "The full-scale official/independent outputs are retained; this lightweight gate does not rerun the expensive nine-dataset computation.",
            "The spherical-prior and empirical-training-distribution assumptions remain part of Claims 2 and 3.",
        ],
        "score_forecast": None,
    }
    serialized = json.dumps(gate, indent=2, sort_keys=True) + "\n"
    for path in (ROOT / "publication_gate.json", OUTPUTS / "publication_gate.json", OUTPUTS / "PUBLICATION_GATE_PASSED.json", OUTPUTS / "CUMULATIVE_SCIENCE_GATE.json"):
        path.write_text(serialized)
    print(serialized, end="")


def run(script: str) -> None:
    environment = {**os.environ, "PYTHONPATH": str(ROOT / "repro" / "src")}
    subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, env=environment, check=True)


if __name__ == "__main__":
    main()
