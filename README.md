# DiffDocket

`DiffDocket` turns a pull request into a deterministic maintainer packet.
It summarizes changed files, classifies risk, flags test gaps, and drafts a release note
without sending code to an external service.

## Why this exists

Maintainers need a fast way to answer:

- What changed?
- What is risky?
- What tests moved with the change?
- What should go into the release note?

This tool gives a clean, repeatable answer in Markdown or JSON.

## Features

- File-level change inventory
- Basic risk classification
- Test gap detection
- Release note draft generation
- Markdown and JSON output
- GitHub Action support

## Install

```bash
python -m pip install -e .[dev]
```

## Use

Run against the current repository:

```bash
diffdocket --repo . --base origin/main --head HEAD
```

Write Markdown to a file:

```bash
diffdocket --repo . --base origin/main --head HEAD --output receipt.md
```

Emit JSON:

```bash
diffdocket --repo . --base origin/main --head HEAD --format json
```

## GitHub Action

```yaml
name: PR Receipt
on:
  pull_request:

jobs:
  receipt:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: LarryLemonBot/diffdocket@main
        with:
          repo-path: .
          base: origin/main
          head: ${{ github.event.pull_request.head.sha }}
          output: pr-receipt.md
```

## Project layout

- `src/pr_review_receipt/` - package code
- `tests/` - unit and integration tests
- `docs/` - roadmap and application notes
- `.github/workflows/` - CI

## Status

This repo is intentionally small, public, and easy to audit. It is designed to be a
credible OSS maintainer tool rather than a generic chatbot wrapper.
