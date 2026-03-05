---
title: Reference
description: Quick reference for Zip Meta Map commands and output files.
sidebar:
  order: 5
---

## Commands

| Command | Description |
|---------|-------------|
| `zip-meta-map build <path> -o <dir>` | Generate metadata for a folder or ZIP |
| `zip-meta-map explain <path>` | Print detected profile and top files |
| `zip-meta-map diff <old> <new>` | Compare two indices |
| `zip-meta-map validate <index>` | Validate an index against the schema |

## Build flags

| Flag | Description |
|------|-------------|
| `-o <dir>` | Output directory |
| `--summary` | Include step summary |
| `--report md` | Generate detailed report |
| `--format json` | JSON to stdout |
| `--format ndjson` | One JSON line per file |
| `--manifest-only` | Skip FRONT.md |
| `--policy <file>` | Apply policy overrides |

## Output files

| File | Format | Purpose |
|------|--------|---------|
| `META_ZIP_FRONT.md` | Markdown | Human-readable orientation |
| `META_ZIP_INDEX.json` | JSON | Machine-readable index |
| `META_ZIP_REPORT.md` | Markdown | Detailed browseable report |

## GitHub Action

```yaml
- name: Generate metadata map
  uses: mcp-tool-shop-org/zip-meta-map@v0
  with:
    path: .
```

Outputs: `index-path`, `front-path`, `profile`, `file-count`, `warnings-count`. Set `pr-comment: 'true'` for PR summaries.

## Links

- [GitHub Repository](https://github.com/mcp-tool-shop-org/zip-meta-map)
- [PyPI Package](https://pypi.org/project/zip-meta-map/)
- [Specification (v0.2)](https://github.com/mcp-tool-shop-org/zip-meta-map/blob/main/docs/SPEC.md)
