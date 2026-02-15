"""Tests that the JSON Schemas themselves are valid and enforce constraints."""

import jsonschema
import pytest

from zip_meta_map.schema import load_index_schema, load_policy_schema


def test_index_schema_loads():
    schema = load_index_schema()
    assert schema["title"] == "META_ZIP_INDEX"
    assert "properties" in schema


def test_policy_schema_loads():
    schema = load_policy_schema()
    assert schema["title"] == "META_ZIP_POLICY"


def test_index_rejects_missing_format():
    schema = load_index_schema()
    bad = {
        "version": "0.1",
        "generated_by": "test",
        "profile": "test",
        "start_here": [],
        "ignore": [],
        "files": [],
        "plans": {},
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_index_rejects_bad_role():
    schema = load_index_schema()
    bad = {
        "format": "zip-meta-map",
        "version": "0.1",
        "generated_by": "test",
        "profile": "test",
        "start_here": [],
        "ignore": [],
        "files": [{"path": "a.py", "size_bytes": 10, "sha256": "a" * 64, "role": "INVALID"}],
        "plans": {},
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_index_rejects_bad_sha256():
    schema = load_index_schema()
    bad = {
        "format": "zip-meta-map",
        "version": "0.1",
        "generated_by": "test",
        "profile": "test",
        "start_here": [],
        "ignore": [],
        "files": [{"path": "a.py", "size_bytes": 10, "sha256": "tooshort", "role": "source"}],
        "plans": {},
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_index_accepts_valid_minimal():
    schema = load_index_schema()
    good = {
        "format": "zip-meta-map",
        "version": "0.1",
        "generated_by": "test/0.0.1",
        "profile": "python_cli",
        "start_here": [],
        "ignore": [],
        "files": [],
        "plans": {},
    }
    jsonschema.validate(good, schema)


def test_policy_accepts_valid():
    schema = load_policy_schema()
    good = {
        "format": "zip-meta-policy",
        "version": "0.1",
        "read_only": ["*.lock"],
        "sensitive": [".env", "*.key"],
        "notes": "Be careful with credentials.",
    }
    jsonschema.validate(good, schema)
