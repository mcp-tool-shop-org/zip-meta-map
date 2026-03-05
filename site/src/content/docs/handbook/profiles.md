---
title: Profiles
description: Auto-detected project types and role classification.
sidebar:
  order: 3
---

Zip Meta Map auto-detects the project type from its file structure and assigns roles to every file.

## Built-in profiles

| Profile | Detected by | Plans |
|---------|------------|-------|
| `python_cli` | `pyproject.toml`, `setup.py` | overview, debug, add_feature, security_review, deep_dive |
| `node_ts_tool` | `package.json`, `tsconfig.json` | overview, debug, add_feature, security_review, deep_dive |
| `monorepo` | `pnpm-workspace.yaml`, `lerna.json` | overview, debug, add_feature, security_review, deep_dive |

Each profile defines traversal plans with byte budgets — so an AI agent knows how to navigate the codebase without reading everything.

## Roles

Every file entry includes a **role** from a bounded vocabulary (entrypoint, config, doc, test, etc.), a **confidence** score (0.0–1.0), and a **reason** explaining the classification.

### Confidence bands

| Band | Range | Meaning |
|------|-------|---------|
| High | >= 0.9 | Strong structural signal (filename match, profile entrypoint) |
| Good | >= 0.7 | Pattern match (directory convention, extension + location) |
| Fair | >= 0.5 | Extension-only or weak positional signal |
| Low | < 0.5 | Assigned `unknown`; reason explains the ambiguity |

## Deterministic classification

Role assignment is purely rule-based — same input always produces the same output. No AI inference, no probabilistic models. This makes diffs meaningful and results reproducible across environments.
