"""Role assignment for scanned files."""

from __future__ import annotations

from fnmatch import fnmatch
from pathlib import PurePosixPath

from zip_meta_map.profiles import Profile

# Extension-based role mapping (low priority, used as fallback)
_EXT_ROLES: dict[str, str] = {
    ".md": "doc",
    ".rst": "doc",
    ".txt": "doc",
    ".json": "data",
    ".yaml": "data",
    ".yml": "data",
    ".toml": "config",
    ".cfg": "config",
    ".ini": "config",
}

# Filename-based role mapping (higher priority)
_NAME_ROLES: dict[str, str] = {
    "README.md": "doc",
    "README.rst": "doc",
    "README.txt": "doc",
    "LICENSE": "doc",
    "LICENSE.md": "doc",
    "CHANGELOG.md": "doc",
    "CHANGES.md": "doc",
    "pyproject.toml": "config",
    "setup.py": "config",
    "setup.cfg": "config",
    "package.json": "config",
    "tsconfig.json": "config",
    "Cargo.toml": "config",
    ".gitignore": "config",
    ".editorconfig": "config",
    "Makefile": "build",
    "Dockerfile": "build",
    "docker-compose.yml": "build",
    "docker-compose.yaml": "build",
    "Justfile": "build",
    "Taskfile.yml": "build",
    "pnpm-workspace.yaml": "config",
    "lerna.json": "config",
}

# Path pattern-based role mapping
_PATTERN_ROLES: list[tuple[str, str]] = [
    ("tests/**", "test"),
    ("test/**", "test"),
    ("**/test_*.py", "test"),
    ("**/*_test.py", "test"),
    ("**/*.test.ts", "test"),
    ("**/*.test.js", "test"),
    ("**/*.spec.ts", "test"),
    ("**/*.spec.js", "test"),
    (".github/**", "build"),
    (".circleci/**", "build"),
    ("**/*.schema.json", "schema"),
    ("**/schema/**", "schema"),
]

# Source code extensions
_SOURCE_EXTS = {
    ".py",
    ".ts",
    ".js",
    ".tsx",
    ".jsx",
    ".rs",
    ".go",
    ".java",
    ".cs",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".rb",
    ".php",
    ".swift",
    ".kt",
    ".scala",
    ".clj",
    ".ex",
    ".exs",
    ".zig",
    ".nim",
    ".lua",
    ".sh",
    ".bash",
    ".zsh",
    ".ps1",
    ".psm1",
}


def assign_role(path: str, profile: Profile) -> str:
    """Assign a role to a file path based on the profile and heuristics."""
    posix = PurePosixPath(path)
    name = posix.name

    # Check if it's an entrypoint
    for pattern in profile.entrypoint_patterns:
        if fnmatch(path, pattern):
            return "entrypoint"

    # Check filename-based roles
    if name in _NAME_ROLES:
        return _NAME_ROLES[name]

    # Check pattern-based roles
    for pattern, role in _PATTERN_ROLES:
        if fnmatch(path, pattern):
            return role

    # Check extension-based roles
    ext = posix.suffix.lower()
    if ext in _EXT_ROLES:
        return _EXT_ROLES[ext]

    # Source code detection
    if ext in _SOURCE_EXTS:
        return "source"

    return "unknown"
