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


def test_cli_explain_missing_input(tmp_path, capsys):
    missing = tmp_path / "nope"
    code = main(["explain", str(missing)])
    assert code == 1


def test_cli_no_command(capsys):
    code = main([])
    assert code == 0
