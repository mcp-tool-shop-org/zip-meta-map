"""Tests for the core builder."""

import json
import zipfile
from pathlib import Path

import pytest

from zip_meta_map.builder import build, build_index, detect_profile, validate_index
from zip_meta_map.profiles import PYTHON_CLI
from zip_meta_map.scanner import scan_directory

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "tiny_python_cli"


def test_detect_profile_python():
    files = scan_directory(FIXTURE_DIR, [".git/**"])
    profile = detect_profile(files)
    assert profile.name == "python_cli"


def test_build_index_valid_schema():
    files = scan_directory(FIXTURE_DIR, PYTHON_CLI.ignore_globs)
    index = build_index(files, PYTHON_CLI, "tiny_python_cli")
    # Should not raise
    validate_index(index)


def test_build_index_required_fields():
    files = scan_directory(FIXTURE_DIR, PYTHON_CLI.ignore_globs)
    index = build_index(files, PYTHON_CLI, "tiny_python_cli")
    assert index["format"] == "zip-meta-map"
    assert index["version"] == "0.1"
    assert index["profile"] == "python_cli"
    assert isinstance(index["files"], list)
    assert isinstance(index["plans"], dict)
    assert "overview" in index["plans"]


def test_build_index_files_have_hashes():
    files = scan_directory(FIXTURE_DIR, PYTHON_CLI.ignore_globs)
    index = build_index(files, PYTHON_CLI, "tiny_python_cli")
    for entry in index["files"]:
        assert len(entry["sha256"]) == 64
        assert entry["size_bytes"] >= 0
        assert entry["role"] in [
            "entrypoint",
            "config",
            "source",
            "test",
            "doc",
            "schema",
            "data",
            "build",
            "unknown",
        ]


def test_build_start_here():
    files = scan_directory(FIXTURE_DIR, PYTHON_CLI.ignore_globs)
    index = build_index(files, PYTHON_CLI, "tiny_python_cli")
    assert "README.md" in index["start_here"]
    assert "pyproject.toml" in index["start_here"]


def test_build_full_directory(tmp_path):
    front, index = build(FIXTURE_DIR)
    assert "tiny_python_cli" in front
    assert index["format"] == "zip-meta-map"
    validate_index(index)


def test_build_writes_output(tmp_path):
    build(FIXTURE_DIR, output_dir=tmp_path)
    assert (tmp_path / "META_ZIP_FRONT.md").exists()
    assert (tmp_path / "META_ZIP_INDEX.json").exists()

    index = json.loads((tmp_path / "META_ZIP_INDEX.json").read_text())
    validate_index(index)


def test_build_zip(tmp_path):
    # Create a zip from the fixture
    zip_path = tmp_path / "fixture.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for fpath in sorted(FIXTURE_DIR.rglob("*")):
            if fpath.is_file():
                arcname = str(fpath.relative_to(FIXTURE_DIR))
                zf.write(fpath, arcname)

    front, index = build(zip_path)
    assert index["format"] == "zip-meta-map"
    validate_index(index)


def test_build_invalid_input(tmp_path):
    bad = tmp_path / "not_a_zip.txt"
    bad.write_text("hello")
    with pytest.raises(ValueError, match="directory or .zip"):
        build(bad)


def test_build_forced_profile():
    front, index = build(FIXTURE_DIR, profile_name="node_ts_tool")
    assert index["profile"] == "node_ts_tool"
    validate_index(index)
