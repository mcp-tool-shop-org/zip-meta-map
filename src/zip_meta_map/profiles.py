"""Built-in profiles for project type detection and categorization."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Plan:
    description: str
    steps: list[str]
    budget_bytes: int | None = None
    stop_after: list[str] | None = None
    max_total_bytes: int | None = None

    def to_dict(self) -> dict:
        d: dict = {"description": self.description, "steps": self.steps}
        if self.budget_bytes is not None:
            d["budget_bytes"] = self.budget_bytes
        if self.stop_after is not None:
            d["stop_after"] = self.stop_after
        if self.max_total_bytes is not None:
            d["max_total_bytes"] = self.max_total_bytes
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
            description="Quick orientation \u2014 what is this tool and how is it structured?",
            steps=[
                "READ README.md for project purpose and usage",
                "READ pyproject.toml for dependencies and entry points",
                "READ entrypoint file to understand CLI structure",
                "LIST src/ directory structure for module layout",
            ],
            budget_bytes=8192,
            stop_after=["README.md", "pyproject.toml", "src/*/cli.py", "src/*/main.py"],
            max_total_bytes=32768,
        ),
        "debug": Plan(
            description="Find and fix a bug",
            steps=[
                "READ entrypoint file for control flow",
                "LIST tests/ to understand coverage",
                "SCAN src/ for error handling patterns (try/except, raise)",
                "CHECK pyproject.toml for dependency versions",
            ],
            budget_bytes=16384,
            max_total_bytes=65536,
        ),
        "add_feature": Plan(
            description="Understand where to add new functionality",
            steps=[
                "READ README.md for project context",
                "READ entrypoint to understand CLI structure and subcommands",
                "LIST src/ modules to find related code",
                "READ tests/ for test patterns to follow",
            ],
            budget_bytes=12288,
            max_total_bytes=49152,
        ),
        "security_review": Plan(
            description="Identify security-sensitive code paths",
            steps=[
                "SCAN for subprocess, eval, exec, os.system, shlex calls",
                "CHECK for hardcoded secrets, tokens, or credentials",
                "REVIEW dependency list in pyproject.toml for known-vulnerable packages",
                "SCAN for file I/O operations on user-supplied paths (path traversal)",
            ],
            budget_bytes=16384,
            max_total_bytes=65536,
        ),
        "deep_dive": Plan(
            description="Read all source modules to understand full implementation",
            steps=[
                "READ start_here files for orientation",
                "READ each source module in dependency order (imports first)",
                "READ tests to understand expected behavior",
                "SUMMARIZE_THEN_CHOOSE_NEXT: after each chunk, decide if more detail is needed",
            ],
            budget_bytes=32768,
            max_total_bytes=131072,
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
                "READ README.md for project purpose",
                "READ package.json for scripts, dependencies, main/bin fields",
                "READ entrypoint file for module structure",
                "LIST src/ directory structure",
            ],
            budget_bytes=8192,
            stop_after=["README.md", "package.json", "src/index.ts", "src/cli.ts"],
            max_total_bytes=32768,
        ),
        "debug": Plan(
            description="Find and fix a bug",
            steps=[
                "READ entrypoint file",
                "READ tsconfig.json for compilation settings",
                "SCAN src/ for error handling patterns (try/catch, throw)",
                "READ relevant test files",
            ],
            budget_bytes=16384,
            max_total_bytes=65536,
        ),
        "add_feature": Plan(
            description="Understand where to add new functionality",
            steps=[
                "READ README.md for project context",
                "READ entrypoint and trace imports for module graph",
                "LIST src/ for module layout",
                "READ existing tests for patterns",
            ],
            budget_bytes=12288,
            max_total_bytes=49152,
        ),
        "security_review": Plan(
            description="Identify security-sensitive code paths",
            steps=[
                "SCAN for child_process, eval, Function(), dynamic require/import",
                "CHECK for hardcoded secrets, tokens, or API keys",
                "REVIEW package.json dependencies for known vulnerabilities",
                "SCAN for file/network I/O with user-supplied input",
            ],
            budget_bytes=16384,
            max_total_bytes=65536,
        ),
        "deep_dive": Plan(
            description="Read all source modules to understand full implementation",
            steps=[
                "READ start_here files for orientation",
                "READ each source module in dependency order (imports first)",
                "READ tests to understand expected behavior",
                "SUMMARIZE_THEN_CHOOSE_NEXT: after each chunk, decide if more detail is needed",
            ],
            budget_bytes=32768,
            max_total_bytes=131072,
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
                "READ root README.md for project purpose",
                "READ workspace config (pnpm-workspace.yaml / package.json / lerna.json)",
                "LIST top-level packages/directories",
                "READ README.md in each package (first 3 by name)",
            ],
            budget_bytes=8192,
            stop_after=["README.md", "pnpm-workspace.yaml", "lerna.json"],
            max_total_bytes=49152,
        ),
        "debug": Plan(
            description="Find and fix a bug across packages",
            steps=[
                "IDENTIFY which package owns the bug by listing packages",
                "READ that package's entrypoint and package.json/pyproject.toml",
                "TRACE cross-package dependencies via workspace config",
                "READ related tests",
            ],
            budget_bytes=16384,
            max_total_bytes=81920,
        ),
        "add_feature": Plan(
            description="Add functionality to the right package",
            steps=[
                "READ root README for architecture overview",
                "LIST packages to identify the right target",
                "READ target package entrypoint and structure",
                "CHECK for shared utilities or common packages",
            ],
            budget_bytes=12288,
            max_total_bytes=65536,
        ),
        "security_review": Plan(
            description="Security review across all packages",
            steps=[
                "LIST all packages and their dependency manifests",
                "SCAN each package for security-sensitive patterns",
                "REVIEW all dependency manifests for known vulnerabilities",
                "CHECK for shared secrets or credential handling",
            ],
            budget_bytes=16384,
            max_total_bytes=131072,
        ),
        "deep_dive": Plan(
            description="Read all packages to understand full monorepo implementation",
            steps=[
                "READ start_here files and workspace config for orientation",
                "LIST all packages and their entrypoints",
                "READ each package's primary source in dependency order",
                "SUMMARIZE_THEN_CHOOSE_NEXT: after each package, decide which to explore deeper",
            ],
            budget_bytes=32768,
            max_total_bytes=262144,
        ),
    },
)

ALL_PROFILES: dict[str, Profile] = {
    "python_cli": PYTHON_CLI,
    "node_ts_tool": NODE_TS_TOOL,
    "monorepo": MONOREPO,
}

DEFAULT_PROFILE = PYTHON_CLI
