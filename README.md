# zip-meta-map

zip-meta-map turns a ZIP (or folder) into a guided, LLM-friendly bundle by embedding a small metadata layer that answers:

- **What's in here?**
- **What matters first?**
- **How should an agent/LLM traverse this without drowning in context?**

It does this by generating a deterministic "front page" plus a structured index with roles, confidence, reasons, and traversal plans with byte budgets.

This repo is currently alpha (v0.1.0-alpha.0). The format and schemas are intentionally strict so downstream tools can rely on them.

## Why this exists

Raw archives are hostile to context-limited systems:

- Reading everything is wasteful (and often impossible).
- Sampling randomly misses critical entrypoints and contracts.
- "Just search" doesn't teach the model how the repo is shaped.

zip-meta-map ships the missing piece: a **map + a route + guardrails**, inside the archive itself.

## What it generates

When you run `zip-meta-map build`, it writes two files into the output:

- **`META_ZIP_FRONT.md`** A compact orientation page: what this is, where to start, module structure, guardrails, and a role summary.
- **`META_ZIP_INDEX.json`** A machine-readable index of every file, including:
  - role + tags
  - confidence (0.0-1.0) and a reason string
  - start\_here ordering with excerpts
  - chunk maps for large files
  - module (folder-level) summaries
  - risk flags and safety warnings
  - traversal plans with budget\_bytes, max\_total\_bytes, and stop semantics

Schemas are included and enforced in CI and at runtime:

- `meta_zip_index.schema.json`
- `meta_zip_policy.schema.json`

An optional **`META_ZIP_POLICY.json`** input lets you tune ignore rules and plan budgets safely.

## Install

From source (recommended for alpha):

```bash
git clone https://github.com/mcp-tool-shop-org/zip-meta-map
cd zip-meta-map
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quickstart

### Build metadata for a folder

```bash
zip-meta-map build path/to/repo -o output/
```

### Build metadata for an existing ZIP

```bash
zip-meta-map build path/to/archive.zip -o output/
```

### Explain what the tool detected

```bash
zip-meta-map explain path/to/repo
```

The explain output highlights:

- detected profile
- role distribution
- module summaries
- top-10 recommended files
- the "overview" traversal plan
- safety warnings
- low-confidence warnings

### Machine-readable explain

```bash
zip-meta-map explain path/to/repo --json
```

### Validate an existing index

```bash
zip-meta-map validate META_ZIP_INDEX.json
```

### Advanced mode (policy overrides)

Provide a policy file to tune ignore globs and plan budgets:

```bash
zip-meta-map build path/to/repo --policy META_ZIP_POLICY.json -o output/
```

The tool validates policy input against schema and records whether policy was applied in the output index.

## Profiles

zip-meta-map categorizes differently depending on the detected repo "shape." Current built-ins:

- `python_cli`
- `node_ts_tool`
- `monorepo`

Profiles define:

- default ignore patterns (generated/vendor directories, caches)
- role/entrypoint heuristics
- traversal plans and budgets (overview, debug, add\_feature, security\_review, deep\_dive)

See [docs/PROFILES.md](docs/PROFILES.md).

## Roles, confidence, and reasons

Every file entry includes:

- **role** (bounded vocabulary, stable)
- **tags** (extensible)
- **confidence** (0.0-1.0)
- **reason** (why the tool labeled it that way)

Confidence bands:

| Band | Range | Meaning |
|------|-------|---------|
| High | >= 0.9 | Strong structural signal (filename match, profile entrypoint) |
| Good | >= 0.7 | Pattern match (directory convention, extension + location) |
| Fair | >= 0.5 | Extension-only or weak positional signal |
| Low  | < 0.5 | Assigned `unknown`; reason explains the ambiguity |

This is deliberate: the index is useful *and* debuggable.

## Progressive disclosure (v0.2)

For files larger than 32 KB, the index includes a **chunk map** with stable IDs, line ranges, and headings. This lets agents read large files in bounded pieces without losing their place.

**Module summaries** group files by directory, showing role distribution, key files, and a heuristic description of what each folder contains.

**Excerpts** give agents the first few lines of high-value files without reading the full content.

**Risk flags** detect heuristic signals per file: shell execution, credential patterns, network I/O, path traversal, and binary masquerading as text.

## Determinism and safety

zip-meta-map is designed to be:

- **Deterministic**: same input -> same output (stable ordering, stable heuristics)
- **Strict**: outputs are validated against JSON Schema before writing
- **Conservative**: generated/vendor directories are flagged and discouraged from ingestion
- **Auditable**: reasons and confidence make the classification inspectable
- **Safe**: risk flags and warnings surface security concerns proactively

The index is guidance, not gospel. Consumers should still validate archive contents independently.

## Repo structure

```
src/zip_meta_map/
  cli.py        # argparse CLI (build, explain, validate)
  builder.py    # scan -> index -> validate -> write
  scanner.py    # directory + ZIP scanning with SHA-256, incremental cache
  roles.py      # role assignment heuristics + confidence
  profiles.py   # built-in profiles + traversal plans
  chunker.py    # deterministic text chunking (headings + lines)
  modules.py    # folder-level module summaries
  safety.py     # risk flag detection + warning generation
  schema/       # JSON Schemas and loaders
docs/
  SPEC.md       # v0.2 contract (format semantics)
  PROFILES.md   # profile behaviors + plans
tests/
  fixtures/     # tiny fixture repos
```

## Contributing

This project is small on purpose. If you contribute:

- keep heuristics deterministic
- keep roles bounded, push nuance into tags
- add tests for any new heuristic
- don't loosen schemas without updating docs/SPEC.md and goldens

Run locally:

```bash
pytest
```

## Documentation

- [Specification (v0.2)](docs/SPEC.md) - the contract for all generated files
- [Profiles](docs/PROFILES.md) - built-in project type profiles

## License

MIT. See [LICENSE](LICENSE).
