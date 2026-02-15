# zip-meta-map

Generate machine-readable metadata manifests for ZIP archives and project directories.

`zip-meta-map` scans a folder or ZIP file and produces a set of metadata files that help AI agents, code reviewers, and automation tools understand the archive's contents without extracting and reading every file.

## What it produces

| File | Purpose |
|------|---------|
| `META_ZIP_FRONT.md` | Human-readable summary (title, description, quick-start) |
| `META_ZIP_INDEX.json` | Full file inventory with roles, tags, hashes, and traversal plans |
| `META_ZIP_POLICY.json` | Optional — controls what agents should/shouldn't touch |

## Quick start

```bash
pip install zip-meta-map

# Scan a directory
zip-meta-map build ./my-project

# Scan a ZIP file
zip-meta-map build archive.zip

# Output goes to stdout by default; use -o to write files
zip-meta-map build ./my-project -o ./output/
```

## Example output

Running `zip-meta-map build` on a small Python CLI project produces a `META_ZIP_INDEX.json` like:

```json
{
  "format": "zip-meta-map",
  "version": "0.1",
  "generated_by": "zip-meta-map/0.1.0-alpha.0",
  "profile": "python_cli",
  "start_here": ["src/main.py", "README.md"],
  "files": [
    {
      "path": "src/main.py",
      "role": "entrypoint",
      "tags": ["cli"],
      "size_bytes": 1024,
      "sha256": "abc123..."
    }
  ],
  "plans": {
    "overview": {
      "description": "Quick orientation",
      "steps": ["READ start_here files", "SCAN src/ for structure"]
    }
  }
}
```

## Documentation

- [Specification (v0.1)](docs/SPEC.md) — the contract for all generated files
- [Profiles](docs/PROFILES.md) — built-in project type profiles

## License

MIT
