"""CLI entry point for zip-meta-map."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from zip_meta_map import __version__
from zip_meta_map.builder import build
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

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "build":
        input_path: Path = args.input
        if not input_path.exists():
            print(f"Error: {input_path} does not exist", file=sys.stderr)
            return 1

        try:
            front, index = build(input_path, output_dir=args.output, profile_name=args.profile)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        if args.output:
            print(f"Wrote META_ZIP_FRONT.md and META_ZIP_INDEX.json to {args.output}/")
        else:
            print("--- META_ZIP_FRONT.md ---")
            print(front)
            print("--- META_ZIP_INDEX.json ---")
            print(json.dumps(index, indent=2))

        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
