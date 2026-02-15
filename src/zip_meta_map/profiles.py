"""Built-in profiles for project type detection and categorization."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Plan:
    description: str
    steps: list[str]
    budget_bytes: int | None = None
    stop_after: list[str] | None = None

    def to_dict(self) -> dict:
        d: dict = {"description": self.description, "steps": self.steps}
        if self.budget_bytes is not None:
            d["budget_bytes"] = self.budget_bytes
        if self.stop_after is not None:
            d["stop_after"] = self.stop_after
        return d


@dataclass(frozen=True)
class Profile:
    name: str
    entrypoint_patterns: list[str]
    start_here_extras: list[str]
    ignore_globs: list[str]
    plans: dict[str, Plan]
    detect_files: list[str] = field(default_factory=list)


PYTHON_CLI = Profile(
    name="python_cli",
    detect_files=["pyproject.toml", "setup.py", "setup.cfg"],
    entrypoint_patterns=[
        "src/*/cli.py",
        "src/*/main.py",
        "src/*/__main__.py",
        "cli.py",
        "main.py",
        "__main__.py",
    ],
    start_here_extras=["README.md", "pyproject.toml"],
    ignore_globs=[
        "__pycache__/**",
        "*.pyc",
        ".venv/**",
        "venv/**",
        "*.egg-info/**",
        "dist/**",
        "build/**",
        ".git/**",
        ".pytest_cache/**",
        ".mypy_cache/**",
        ".tox/**",
    ],
    plans={
        "overview": Plan(
            description="Quick orientation — what is this tool and how is it structured?",
            steps=[
                "READ README.md",
                "READ pyproject.toml (dependencies, entry points)",
                "READ entrypoint file",
                "LIST src/ directory structure",
            ],
        ),
        "debug": Plan(
            description="Find and fix a bug",
            steps=[
                "READ entrypoint file",
                "READ tests/ to understand test coverage",
                "SCAN src/ for error handling patterns",
                "CHECK pyproject.toml for dependency versions",
            ],
        ),
        "add_feature": Plan(
            description="Understand where to add new functionality",
            steps=[
                "READ README.md for project context",
                "READ entrypoint to understand CLI structure",
                "LIST src/ modules to find related code",
                "READ tests/ for test patterns to follow",
            ],
        ),
        "security_review": Plan(
            description="Identify security-sensitive code paths",
            steps=[
                "SCAN for subprocess, eval, exec, os.system calls",
                "CHECK for hardcoded secrets or credentials",
                "REVIEW dependency list in pyproject.toml",
                "SCAN for file I/O operations on user-supplied paths",
            ],
        ),
    },
)

NODE_TS_TOOL = Profile(
    name="node_ts_tool",
    detect_files=["package.json", "tsconfig.json"],
    entrypoint_patterns=[
        "src/index.ts",
        "src/main.ts",
        "src/cli.ts",
        "index.ts",
        "index.js",
    ],
    start_here_extras=["README.md", "package.json"],
    ignore_globs=[
        "node_modules/**",
        "dist/**",
        "build/**",
        ".git/**",
        "coverage/**",
        ".nyc_output/**",
        "*.tsbuildinfo",
        ".turbo/**",
    ],
    plans={
        "overview": Plan(
            description="Quick orientation",
            steps=[
                "READ README.md",
                "READ package.json (scripts, dependencies, main/bin)",
                "READ entrypoint file",
                "LIST src/ directory structure",
            ],
        ),
        "debug": Plan(
            description="Find and fix a bug",
            steps=[
                "READ entrypoint file",
                "READ tsconfig.json for compilation settings",
                "SCAN src/ for error handling patterns",
                "READ relevant test files",
            ],
        ),
        "add_feature": Plan(
            description="Understand where to add new functionality",
            steps=[
                "READ README.md for project context",
                "READ entrypoint and trace imports",
                "LIST src/ for module layout",
                "READ existing tests for patterns",
            ],
        ),
        "security_review": Plan(
            description="Identify security-sensitive code paths",
            steps=[
                "SCAN for child_process, eval, dynamic require/import",
                "CHECK for hardcoded secrets or tokens",
                "REVIEW package.json dependencies",
                "SCAN for file/network I/O with user-supplied input",
            ],
        ),
    },
)

MONOREPO = Profile(
    name="monorepo",
    detect_files=["pnpm-workspace.yaml", "lerna.json"],
    entrypoint_patterns=[],
    start_here_extras=["README.md"],
    ignore_globs=[
        "**/node_modules/**",
        "**/__pycache__/**",
        "**/dist/**",
        "**/build/**",
        ".git/**",
        "**/*.egg-info/**",
        "**/coverage/**",
        "**/.venv/**",
    ],
    plans={
        "overview": Plan(
            description="Understand the monorepo structure",
            steps=[
                "READ root README.md",
                "READ workspace config (pnpm-workspace.yaml / package.json / lerna.json)",
                "LIST top-level packages/directories",
                "READ README.md in each package (first 3)",
            ],
        ),
        "debug": Plan(
            description="Find and fix a bug across packages",
            steps=[
                "IDENTIFY which package owns the bug",
                "READ that package's entrypoint",
                "TRACE cross-package dependencies",
                "READ related tests",
            ],
        ),
        "add_feature": Plan(
            description="Add functionality to the right package",
            steps=[
                "READ root README for architecture overview",
                "LIST packages to identify the right target",
                "READ target package entrypoint and structure",
                "CHECK for shared utilities or common packages",
            ],
        ),
        "security_review": Plan(
            description="Security review across all packages",
            steps=[
                "LIST all packages",
                "SCAN each package for security-sensitive patterns",
                "REVIEW all dependency manifests",
                "CHECK for shared secrets or credential handling",
            ],
        ),
    },
)

ALL_PROFILES: dict[str, Profile] = {
    "python_cli": PYTHON_CLI,
    "node_ts_tool": NODE_TS_TOOL,
    "monorepo": MONOREPO,
}

DEFAULT_PROFILE = PYTHON_CLI
