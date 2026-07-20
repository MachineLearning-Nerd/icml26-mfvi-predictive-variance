from pathlib import Path
import importlib.util


MODULE = Path(__file__).parents[1] / "src" / "prepublish_gate.py"
SPEC = importlib.util.spec_from_file_location("prepublish_gate", MODULE)
assert SPEC and SPEC.loader
prepublish_gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepublish_gate)


def test_parse_source_table_extracts_all_nine_rows(tmp_path: Path) -> None:
    rows = "\n".join(
        f"name{i} & 1 & 2 & 0 & 0 & 0 & 0 & {i + 0.1} & {i + 0.2} \\\\\\"
        for i in range(9)
    )
    table = tmp_path / "table.tex"
    table.write_text(rows + "\n")
    parsed = prepublish_gate.parse_source_table(table)
    assert len(parsed) == 9
    assert parsed["name3"] == (3.1, 3.2)


def test_official_run_provenance_rejects_source_drift(tmp_path: Path) -> None:
    source = {
        "official_repository_commit": "a" * 40,
        "official_uci_script_sha256": "b" * 64,
    }
    provenance = tmp_path / "official_uci_provenance.txt"
    provenance.write_text(
        "official_repository_commit=" + source["official_repository_commit"] + "\n"
        "uci_tr_inequ_sha256=" + source["official_uci_script_sha256"] + "\n"
    )
    assert prepublish_gate.verify_official_run_provenance(provenance, source)["uci_tr_inequ_sha256"] == "b" * 64
    provenance.write_text("official_repository_commit=" + source["official_repository_commit"] + "\n")
    try:
        prepublish_gate.verify_official_run_provenance(provenance, source)
    except AssertionError:
        pass
    else:
        raise AssertionError("incomplete provenance must fail closed")
