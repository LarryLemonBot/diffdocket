from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analysis import build_receipt
from .render import render_json, render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a PR review receipt.")
    parser.add_argument("--repo", default=".", help="Path to the git repository.")
    parser.add_argument("--base", default="HEAD~1", help="Base ref to compare against.")
    parser.add_argument("--head", default="HEAD", help="Head ref to compare against.")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional output file path. Prints to stdout if omitted.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    receipt = build_receipt(args.repo, base_ref=args.base, head_ref=args.head)
    rendered = render_markdown(receipt) if args.format == "markdown" else render_json(receipt)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)

    return 0

