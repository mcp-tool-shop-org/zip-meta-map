# zip-meta-map Profiles — v0.1

Profiles define how zip-meta-map categorizes files and constructs traversal plans for specific project types. A profile provides:

- **Default ignore globs** — files excluded from indexing
- **Entrypoint detection** — what counts as a "start here" file
- **Default traversal plans** — named strategies for navigating the project

## Profile: `python_cli`

For Python projects with a CLI entry point (Click, argparse, Typer, etc.).

### Entrypoint detection

Files matching (in priority order):
1. `src/*/cli.py` or `src/*/main.py`
2. `src/*/__main__.py`
3. `cli.py` or `main.py` at root
4. `__main__.py` at root

Also includes: `README.md`, `pyproject.toml`

### Default ignore globs

```
__pycache__/**
*.pyc
.venv/**
venv/**
*.egg-info/**
dist/**
build/**
.git/**
.pytest_cache/**
.mypy_cache/**
.tox/**
```

### Default plans

**overview**
> Quick orientation — what is this tool and how is it structured?
1. READ `README.md`
2. READ `pyproject.toml` (dependencies, entry points)
3. READ entrypoint file
4. LIST `src/` directory structure

**debug**
> Find and fix a bug
1. READ entrypoint file
2. READ `tests/` to understand test coverage
3. SCAN `src/` for error handling patterns
4. CHECK `pyproject.toml` for dependency versions

**add_feature**
> Understand where to add new functionality
1. READ `README.md` for project context
2. READ entrypoint to understand CLI structure
3. LIST `src/` modules to find related code
4. READ `tests/` for test patterns to follow

**security_review**
> Identify security-sensitive code paths
1. SCAN for `subprocess`, `eval`, `exec`, `os.system` calls
2. CHECK for hardcoded secrets or credentials
3. REVIEW dependency list in `pyproject.toml`
4. SCAN for file I/O operations on user-supplied paths

---

## Profile: `node_ts_tool`

For Node.js/TypeScript tool projects (CLI tools, MCP servers, utilities).

### Entrypoint detection

Files matching (in priority order):
1. `src/index.ts` or `src/main.ts`
2. `src/cli.ts`
3. `index.ts` or `index.js` at root
4. `main` field in `package.json`

Also includes: `README.md`, `package.json`

### Default ignore globs

```
node_modules/**
dist/**
build/**
.git/**
coverage/**
.nyc_output/**
*.tsbuildinfo
.turbo/**
```

### Default plans

**overview**
> Quick orientation
1. READ `README.md`
2. READ `package.json` (scripts, dependencies, main/bin)
3. READ entrypoint file
4. LIST `src/` directory structure

**debug**
> Find and fix a bug
1. READ entrypoint file
2. READ `tsconfig.json` for compilation settings
3. SCAN `src/` for error handling patterns
4. READ relevant test files

**add_feature**
> Understand where to add new functionality
1. READ `README.md` for project context
2. READ entrypoint and trace imports
3. LIST `src/` for module layout
4. READ existing tests for patterns

**security_review**
> Identify security-sensitive code paths
1. SCAN for `child_process`, `eval`, dynamic `require`/`import`
2. CHECK for hardcoded secrets or tokens
3. REVIEW `package.json` dependencies
4. SCAN for file/network I/O with user-supplied input

---

## Profile: `monorepo`

For multi-package repositories with a workspace root.

### Entrypoint detection

Files matching:
1. `README.md` at root
2. Workspace config: `pnpm-workspace.yaml`, root `package.json` with `workspaces`, `lerna.json`
3. First-level `packages/*/README.md` or `packages/*/package.json`

### Default ignore globs

```
**/node_modules/**
**/__pycache__/**
**/dist/**
**/build/**
.git/**
**/*.egg-info/**
**/coverage/**
**/.venv/**
```

### Default plans

**overview**
> Understand the monorepo structure
1. READ root `README.md`
2. READ workspace config (pnpm-workspace.yaml / package.json / lerna.json)
3. LIST top-level packages/directories
4. READ `README.md` in each package (first 3)

**debug**
> Find and fix a bug across packages
1. IDENTIFY which package owns the bug
2. READ that package's entrypoint
3. TRACE cross-package dependencies
4. READ related tests

**add_feature**
> Add functionality to the right package
1. READ root README for architecture overview
2. LIST packages to identify the right target
3. READ target package entrypoint and structure
4. CHECK for shared utilities or common packages

**security_review**
> Security review across all packages
1. LIST all packages
2. SCAN each package for security-sensitive patterns
3. REVIEW all dependency manifests
4. CHECK for shared secrets or credential handling
