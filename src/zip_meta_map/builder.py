"""Core builder — generates META_ZIP_FRONT.md and META_ZIP_INDEX.json."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from zip_meta_map import __version__
from zip_meta_map.profiles import ALL_PROFILES, DEFAULT_PROFILE, Profile
from zip_meta_map.roles import assign_role
from zip_meta_map.scanner import ScannedFile, scan_directory, scan_zip
from zip_meta_map.schema import load_index_schema


def detect_profile(files: list[ScannedFile]) -> Profile:
    """Auto-detect a profile from the file listing."""
    paths = {f.path for f in files}

    # Check monorepo indicators first
    monorepo = ALL_PROFILES["monorepo"]
    for detect_file in monorepo.detect_files:
        if detect_file in paths:
            return monorepo

    # Check for package.json with workspaces (monorepo)
    # (would need file content inspection — skip for v0.1)

    # Check node/ts
    node = ALL_PROFILES["node_ts_tool"]
    for detect_file in node.detect_files:
        if detect_file in paths:
            return node

    # Check python
    python = ALL_PROFILES["python_cli"]
    for detect_file in python.detect_files:
        if detect_file in paths:
            return python

    return DEFAULT_PROFILE


def _find_start_here(files: list[ScannedFile], profile: Profile) -> list[str]:
    """Determine start_here files from scanned files and profile."""
    paths = {f.path for f in files}
    result: list[str] = []

    # Add entrypoints
    for f in files:
        role = assign_role(f.path, profile)
        if role == "entrypoint" and f.path not in result:
            result.append(f.path)

    # Add profile extras that exist
    for extra in profile.start_here_extras:
        if extra in paths and extra not in result:
            result.append(extra)

    return result


def build_index(files: list[ScannedFile], profile: Profile, project_name: str) -> dict:
    """Build the META_ZIP_INDEX.json content."""
    file_entries = []
    for f in files:
        entry: dict = {
            "path": f.path,
            "size_bytes": f.size_bytes,
            "sha256": f.sha256,
            "role": assign_role(f.path, profile),
        }
        file_entries.append(entry)

    plans = {name: plan.to_dict() for name, plan in profile.plans.items()}

    index = {
        "format": "zip-meta-map",
        "version": "0.1",
        "generated_by": f"zip-meta-map/{__version__}",
        "profile": profile.name,
        "start_here": _find_start_here(files, profile),
        "ignore": profile.ignore_globs,
        "files": file_entries,
        "plans": plans,
    }

    return index


def validate_index(index: dict) -> None:
    """Validate index against JSON Schema. Raises jsonschema.ValidationError on failure."""
    schema = load_index_schema()
    jsonschema.validate(instance=index, schema=schema)


def build_front(index: dict, project_name: str) -> str:
    """Build the META_ZIP_FRONT.md content."""
    file_count = len(index["files"])
    start_here = index["start_here"]
    profile = index["profile"]
    generated_by = index["generated_by"]

    start_list = "\n".join(f"- `{f}`" for f in start_here) if start_here else "- (none detected)"

    return f"""# {project_name}

> Auto-generated metadata by {generated_by}

## Summary

- **Profile**: `{profile}`
- **Files indexed**: {file_count}
- **Spec version**: {index["version"]}

## Start here

{start_list}

## Plans

{_format_plans(index["plans"])}

---

*This file is for humans. Agents should prefer `META_ZIP_INDEX.json`.*
"""


def _format_plans(plans: dict) -> str:
    parts = []
    for name, plan in plans.items():
        steps = "\n".join(f"   {i + 1}. {s}" for i, s in enumerate(plan["steps"]))
        parts.append(f"### `{name}`\n\n{plan['description']}\n\n{steps}")
    return "\n\n".join(parts)


def build(input_path: Path, output_dir: Path | None = None, profile_name: str | None = None) -> tuple[str, dict]:
    """
    Main build entry point.

    Args:
        input_path: Path to a directory or ZIP file.
        output_dir: If set, write output files here. Otherwise just return them.
        profile_name: Force a specific profile. Auto-detect if None.

    Returns:
        Tuple of (front_md, index_dict).
    """
    input_path = input_path.resolve()

    if input_path.is_dir():
        project_name = input_path.name
        # Do a preliminary scan with no ignore to detect profile
        if profile_name:
            profile = ALL_PROFILES[profile_name]
        else:
            preliminary = scan_directory(input_path, [".git/**"])
            profile = detect_profile(preliminary)
        files = scan_directory(input_path, profile.ignore_globs)
    elif input_path.suffix == ".zip":
        project_name = input_path.stem
        if profile_name:
            profile = ALL_PROFILES[profile_name]
        else:
            preliminary = scan_zip(input_path, [".git/**"])
            profile = detect_profile(preliminary)
        files = scan_zip(input_path, profile.ignore_globs)
    else:
        raise ValueError(f"Input must be a directory or .zip file, got: {input_path}")

    index = build_index(files, profile, project_name)
    validate_index(index)
    front = build_front(index, project_name)

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "META_ZIP_FRONT.md").write_text(front, encoding="utf-8")
        (output_dir / "META_ZIP_INDEX.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")

    return front, index
