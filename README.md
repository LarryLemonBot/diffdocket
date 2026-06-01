# DiffDocket

[![CI](https://github.com/LarryLemonBot/diffdocket/actions/workflows/ci.yml/badge.svg)](https://github.com/LarryLemonBot/diffdocket/actions/workflows/ci.yml)
[![CodeQL](https://github.com/LarryLemonBot/diffdocket/actions/workflows/codeql.yml/badge.svg)](https://github.com/LarryLemonBot/diffdocket/actions/workflows/codeql.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/LarryLemonBot/diffdocket/badge)](https://securityscorecards.dev/viewer/?uri=github.com/LarryLemonBot/diffdocket)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

`DiffDocket` turns a pull request into a deterministic maintainer packet.
It summarizes changed files, classifies risk, flags test gaps, and drafts a release note
without sending code to an external service.

Hosted project page: https://diffdocket.vercel.app

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

Example receipt:

```markdown
# DiffDocket Receipt

- Repository: `example-project`
- Base: `origin/main`
- Head: `HEAD`
- Risk level: **medium**

## Summary

3 file(s) changed, 82 insertions(+), 12 deletions(-).

## Review Focus

- Review the changed source paths for regressions.
- No test files changed in this patch; add or update tests if behavior changed.

## Release Note Draft

Source file(s) updated; documentation updated. Risk level: medium.
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
      - uses: actions/checkout@v6
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

## Security posture

- Local-first analysis by default.
- No external model calls in the core CLI.
- CI, CodeQL, Dependabot, and OpenSSF Scorecard are enabled for reviewer hygiene.
