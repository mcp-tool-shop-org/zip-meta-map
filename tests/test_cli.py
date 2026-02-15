"""Tests for the CLI entry point."""

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


def test_cli_no_command(capsys):
    code = main([])
    assert code == 0
