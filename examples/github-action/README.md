# zip-meta-map GitHub Action Example

Add this workflow to any repo to generate metadata on every push.

## Basic usage

```yaml
# .github/workflows/metadata.yml
name: Generate metadata map

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  metadata:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate metadata map
        uses: mcp-tool-shop-org/zip-meta-map@v0
        with:
          path: .

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: metadata
          path: .zip-meta-map/
```

## With report and custom output

```yaml
      - name: Generate metadata map
        uses: mcp-tool-shop-org/zip-meta-map@v0
        id: zmm
        with:
          path: .
          report: 'true'
          output-dir: metadata-output

      - name: Show results
        run: |
          echo "Profile: ${{ steps.zmm.outputs.profile }}"
          echo "Files: ${{ steps.zmm.outputs.file-count }}"
          echo "Warnings: ${{ steps.zmm.outputs.warnings-count }}"
```

## Outputs

| Output | Description |
|--------|-------------|
| `index-path` | Path to `META_ZIP_INDEX.json` |
| `front-path` | Path to `META_ZIP_FRONT.md` |
| `report-path` | Path to `META_ZIP_REPORT.md` (if `report: true`) |
| `profile` | Detected profile name |
| `file-count` | Number of files indexed |
| `warnings-count` | Number of warnings |
