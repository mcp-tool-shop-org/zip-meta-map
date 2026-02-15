"""Tests for the CLI entry point."""

import json
from pathlib import Path

import pytest

from zip_meta_map.cli import main

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "tiny_python_cli"


def test_cli_help():
    with pytest.raises(SystemExit, match="0"):
        main(["--help"])


def test_cli_version(capsys):
    with pytest.raises(SystemExit, match="0"):
        main(["--version"])
    captured = capsys.readouterr()
    assert "zip-meta-map" in captured.out


def test_cli_build_stdout(capsys):
    code = main(["build", str(FIXTURE_DIR)])
    assert code == 0
    captured = capsys.readouterr()
    assert "META_ZIP_FRONT.md" in captured.out
    assert "META_ZIP_INDEX.json" in captured.out


def test_cli_build_output_dir(tmp_path, capsys):
    out = tmp_path / "output"
    code = main(["build", str(FIXTURE_DIR), "-o", str(out)])
    assert code == 0
    assert (out / "META_ZIP_FRONT.md").exists()
    assert (out / "META_ZIP_INDEX.json").exists()


def test_cli_build_summary(tmp_path, capsys):
    """Build with output dir should print a build summary."""
    out = tmp_path / "output"
    code = main(["build", str(FIXTURE_DIR), "-o", str(out)])
    assert code == 0
    captured = capsys.readouterr()
    assert "Profile:" in captured.out
    assert "Files:" in captured.out


def test_cli_build_missing_input(tmp_path, capsys):
    missing = tmp_path / "definitely_does_not_exist"
    code = main(["build", str(missing)])
    assert code == 1
    captured = capsys.readouterr()
    assert "does not exist" in captured.err


def test_cli_build_with_policy(tmp_path, capsys):
    policy = {"format": "zip-meta-policy", "version": "0.1", "plan_budgets": {"overview": 5000}}
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(policy))

    out = tmp_path / "output"
    code = main(["build", str(FIXTURE_DIR), "-o", str(out), "--policy", str(policy_path)])
    assert code == 0

    index = json.loads((out / "META_ZIP_INDEX.json").read_text())
    assert index["policy_applied"] is True


def test_cli_build_missing_policy(tmp_path, capsys):
    code = main(["build", str(FIXTURE_DIR), "--policy", str(tmp_path / "nope.json")])
    assert code == 1
    captured = capsys.readouterr()
    assert "does not exist" in captured.err


def test_cli_explain(capsys):
    code = main(["explain", str(FIXTURE_DIR)])
    assert code == 0
    captured = capsys.readouterr()
    assert "Profile:" in captured.out
    assert "python_cli" in captured.out
    assert "Top files to read first:" in captured.out
    assert "Overview plan:" in captured.out


def test_cli_explain_json(capsys):
    """--json flag should produce valid JSON output."""
    code = main(["explain", str(FIXTURE_DIR), "--json"])
    assert code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["profile"] == "python_cli"
    assert isinstance(data["file_count"], int)
    assert isinstance(data["roles"], dict)
    assert isinstance(data["start_here"], list)
    assert isinstance(data["plans"], dict)


def test_cli_explain_missing_input(tmp_path, capsys):
    missing = tmp_path / "nope"
    code = main(["explain", str(missing)])
    assert code == 1


def test_cli_validate_valid(tmp_path, capsys):
    """validate command should accept a valid index."""
    index = {
        "format": "zip-meta-map",
        "version": "0.2",
        "generated_by": "test/0.1.0",
        "profile": "python_cli",
        "start_here": [],
        "ignore": [],
        "files": [],
        "plans": {},
    }
    index_path = tmp_path / "META_ZIP_INDEX.json"
    index_path.write_text(json.dumps(index))

    code = main(["validate", str(index_path)])
    assert code == 0
    captured = capsys.readouterr()
    assert "Valid" in captured.out


def test_cli_validate_invalid(tmp_path, capsys):
    """validate command should reject an invalid index."""
    bad_index = {"format": "wrong"}
    index_path = tmp_path / "bad.json"
    index_path.write_text(json.dumps(bad_index))

    code = main(["validate", str(index_path)])
    assert code == 1
    captured = capsys.readouterr()
    assert "failed" in captured.err.lower() or "Validation" in captured.err


def test_cli_validate_missing_file(tmp_path, capsys):
    code = main(["validate", str(tmp_path / "nonexistent.json")])
    assert code == 1
    captured = capsys.readouterr()
    assert "does not exist" in captured.err


def test_cli_validate_bad_json(tmp_path, capsys):
    bad = tmp_path / "corrupt.json"
    bad.write_text("not json {{{")
    code = main(["validate", str(bad)])
    assert code == 1


def test_cli_no_command(capsys):
    code = main([])
    assert code == 0
