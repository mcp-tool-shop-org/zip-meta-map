---
title: CLI Reference
description: All zip-meta-map commands — build, explain, diff, validate.
sidebar:
  order: 2
---

Zip Meta Map provides four commands: `build`, `explain`, `diff`, and `validate`.

## build

Generate metadata for a folder or ZIP archive:

```bash
zip-meta-map build path/to/repo -o output/
zip-meta-map build archive.zip -o output/
```

### Output options

```bash
# Include step summary and detailed report
zip-meta-map build . -o output/ --summary --report md

# JSON to stdout (for piping)
zip-meta-map build . --format json

# One JSON line per file (NDJSON)
zip-meta-map build . --format ndjson

# Skip FRONT.md, only write INDEX.json
zip-meta-map build . --manifest-only
```

### Policy overrides

Apply custom role assignments and rules:

```bash
zip-meta-map build . --policy META_ZIP_POLICY.json -o output/
```

## explain

Print what the tool detected without writing any files:

```bash
zip-meta-map explain path/to/repo
zip-meta-map explain path/to/repo --json
```

Shows the detected profile, top files to read first, and a traversal plan with byte budgets.

## diff

Compare two metadata indices — useful in CI to detect structural changes:

```bash
zip-meta-map diff old.json new.json             # human-readable
zip-meta-map diff old.json new.json --json       # JSON output
zip-meta-map diff old.json new.json --exit-code  # exit 1 if changes
```

## validate

Check an existing index file against the schema:

```bash
zip-meta-map validate META_ZIP_INDEX.json
```

## Generated files

| File | Purpose |
|------|---------|
| `META_ZIP_FRONT.md` | Human-readable orientation page |
| `META_ZIP_INDEX.json` | Machine-readable index (roles, confidence, plans, chunks, excerpts, risk flags) |
| `META_ZIP_REPORT.md` | Detailed browseable report (with `--report md`) |
