"""CLI entry point for zip-meta-map."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from zip_meta_map import __version__
from zip_meta_map.builder import build, validate_index
from zip_meta_map.profiles import ALL_PROFILES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="zip-meta-map",
        description="Generate machine-readable metadata manifests for ZIP archives and project directories.",
    )
    parser.add_argument("--version", action="version", version=f"zip-meta-map {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    # build command
    build_parser = subparsers.add_parser("build", help="Scan input and generate metadata files")
    build_parser.add_argument("input", type=Path, help="Path to a directory or .zip file")
    build_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output directory for generated files (default: print to stdout)",
    )
    build_parser.add_argument(
        "-p",
        "--profile",
        choices=list(ALL_PROFILES.keys()),
        default=None,
        help="Force a specific profile (default: auto-detect)",
    )
    build_parser.add_argument(
        "--policy",
        type=Path,
        default=None,
        help="Path to a META_ZIP_POLICY.json file",
    )

    # explain command
    explain_parser = subparsers.add_parser("explain", help="Show detected profile and top files to read")
    explain_parser.add_argument("input", type=Path, help="Path to a directory or .zip file")
    explain_parser.add_argument(
        "-p",
        "--profile",
        choices=list(ALL_PROFILES.keys()),
        default=None,
        help="Force a specific profile (default: auto-detect)",
    )
    explain_parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output explain results as JSON",
    )

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a META_ZIP_INDEX.json file against the schema")
    validate_parser.add_argument("input", type=Path, help="Path to a META_ZIP_INDEX.json file")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "build":
        return _cmd_build(args)

    if args.command == "explain":
        return _cmd_explain(args)

    if args.command == "validate":
        return _cmd_validate(args)

    return 0


def _cmd_build(args: argparse.Namespace) -> int:
    input_path: Path = args.input
    if not input_path.exists():
        print(f"Error: {input_path} does not exist", file=sys.stderr)
        return 1

    policy_path: Path | None = args.policy
    if policy_path and not policy_path.exists():
        print(f"Error: policy file {policy_path} does not exist", file=sys.stderr)
        return 1

    try:
        front, index = build(input_path, output_dir=args.output, profile_name=args.profile, policy_path=policy_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.output:
        # Print build summary
        file_count = len(index["files"])
        profile = index["profile"]
        modules = index.get("modules", [])
        warnings = index.get("warnings", [])
        chunked = sum(1 for f in index["files"] if f.get("chunks"))
        flagged = sum(1 for f in index["files"] if f.get("risk_flags"))

        print(f"Wrote META_ZIP_FRONT.md and META_ZIP_INDEX.json to {args.output}/")
        print(f"  Profile:  {profile}")
        print(f"  Files:    {file_count}")
        if modules:
            print(f"  Modules:  {len(modules)}")
        if chunked:
            print(f"  Chunked:  {chunked} file(s)")
        if flagged:
            print(f"  Flagged:  {flagged} file(s) with risk flags")
        if warnings:
            print(f"  Warnings: {len(warnings)}")
    else:
        print("--- META_ZIP_FRONT.md ---")
        print(front)
        print("--- META_ZIP_INDEX.json ---")
        print(json.dumps(index, indent=2))

    return 0


def _cmd_explain(args: argparse.Namespace) -> int:
    input_path: Path = args.input
    if not input_path.exists():
        print(f"Error: {input_path} does not exist", file=sys.stderr)
        return 1

    try:
        _, index = build(input_path, profile_name=args.profile)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.json_output:
        explain_data = _build_explain_data(index)
        print(json.dumps(explain_data, indent=2))
        return 0

    profile = index["profile"]
    start_here = index["start_here"]
    files = index["files"]
    plans = index["plans"]

    print(f"Profile:  {profile}")
    print(f"Files:    {len(files)}")
    print()

    # Role distribution
    role_counts: dict[str, int] = {}
    for f in files:
        role_counts[f["role"]] = role_counts.get(f["role"], 0) + 1
    print("Roles:")
    for role, count in sorted(role_counts.items(), key=lambda x: -x[1]):
        print(f"  {role:20s} {count}")
    print()

    # Top 10 "read first" files
    file_map = {f["path"]: f for f in files}
    print("Top files to read first:")
    shown = 0
    for path in start_here:
        if shown >= 10:
            break
        entry = file_map.get(path, {})
        role = entry.get("role", "?")
        conf = entry.get("confidence", 0)
        reason = entry.get("reason", "")
        print(f"  {path:40s}  [{role}]  conf={conf:.2f}  {reason}")
        shown += 1
    print()

    # Modules
    modules = index.get("modules", [])
    if modules:
        print(f"Modules ({len(modules)}):")
        for mod in modules[:10]:
            summary = mod.get("summary", "")
            print(f"  {mod['path']:40s}  {mod['file_count']} files  {summary}")
        print()

    # Overview plan
    if "overview" in plans:
        plan = plans["overview"]
        print("Overview plan:")
        print(f"  {plan['description']}")
        for i, step in enumerate(plan["steps"], 1):
            print(f"  {i}. {step}")
        if plan.get("max_total_bytes"):
            print(f"  Budget: ~{plan['max_total_bytes'] // 1024} KB")
    print()

    # Safety warnings
    warnings = index.get("warnings", [])
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
        print()

    # Low-confidence warnings
    low_conf = [(f["path"], f["confidence"], f.get("reason", "")) for f in files if f["confidence"] < 0.5]
    if low_conf:
        print(f"Low confidence ({len(low_conf)} files):")
        for path, conf, reason in low_conf[:5]:
            print(f"  {path:40s}  conf={conf:.2f}  {reason}")
        if len(low_conf) > 5:
            print(f"  ... and {len(low_conf) - 5} more")

    return 0


def _build_explain_data(index: dict) -> dict:
    """Build a structured explain object for --json output."""
    files = index["files"]

    role_counts: dict[str, int] = {}
    for f in files:
        role_counts[f["role"]] = role_counts.get(f["role"], 0) + 1

    return {
        "profile": index["profile"],
        "file_count": len(files),
        "roles": role_counts,
        "start_here": index["start_here"],
        "modules": index.get("modules", []),
        "plans": index["plans"],
        "warnings": index.get("warnings", []),
        "low_confidence_count": sum(1 for f in files if f["confidence"] < 0.5),
    }


def _cmd_validate(args: argparse.Namespace) -> int:
    input_path: Path = args.input
    if not input_path.exists():
        print(f"Error: {input_path} does not exist", file=sys.stderr)
        return 1

    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error: could not read JSON: {e}", file=sys.stderr)
        return 1

    try:
        validate_index(data)
    except Exception as e:
        print(f"Validation failed: {e}", file=sys.stderr)
        return 1

    file_count = len(data.get("files", []))
    print(f"Valid META_ZIP_INDEX.json ({file_count} files, version {data.get('version', '?')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
