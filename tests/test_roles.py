"""Tests for role assignment."""

from zip_meta_map.profiles import NODE_TS_TOOL, PYTHON_CLI
from zip_meta_map.roles import assign_role


def test_entrypoint_detection():
    assert assign_role("src/myapp/main.py", PYTHON_CLI) == "entrypoint"
    assert assign_role("src/myapp/cli.py", PYTHON_CLI) == "entrypoint"


def test_config_detection():
    assert assign_role("pyproject.toml", PYTHON_CLI) == "config"
    assert assign_role("package.json", NODE_TS_TOOL) == "config"


def test_doc_detection():
    assert assign_role("README.md", PYTHON_CLI) == "doc"
    assert assign_role("LICENSE", PYTHON_CLI) == "doc"


def test_test_detection():
    assert assign_role("tests/test_main.py", PYTHON_CLI) == "test"
    assert assign_role("tests/test_scanner.py", PYTHON_CLI) == "test"


def test_source_detection():
    assert assign_role("src/myapp/utils.py", PYTHON_CLI) == "source"


def test_build_detection():
    assert assign_role(".github/workflows/ci.yml", PYTHON_CLI) == "build"
    assert assign_role("Makefile", PYTHON_CLI) == "build"


def test_schema_detection():
    assert assign_role("schema/meta.schema.json", PYTHON_CLI) == "schema"


def test_unknown_fallback():
    assert assign_role("random.bin", PYTHON_CLI) == "unknown"


def test_node_entrypoint():
    assert assign_role("src/index.ts", NODE_TS_TOOL) == "entrypoint"
    assert assign_role("src/cli.ts", NODE_TS_TOOL) == "entrypoint"
