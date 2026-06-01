from __future__ import annotations

from pr_review_receipt.analysis import build_receipt_from_changes
from pr_review_receipt.models import Change
from pr_review_receipt.render import render_json, render_markdown


def _receipt():
    return build_receipt_from_changes(
        repo_name="diffdocket",
        repo_path="/tmp/diffdocket",
        base_ref="HEAD~1",
        head_ref="HEAD",
        changes=[
            Change(path="src/pr_review_receipt/cli.py", status="M", additions=8, deletions=2, category="source"),
            Change(path="tests/test_cli.py", status="A", additions=18, deletions=0, category="tests"),
        ],
    )


def test_render_markdown_includes_key_sections() -> None:
    rendered = render_markdown(_receipt())

    assert "# DiffDocket Receipt" in rendered
    assert "## Changed Files" in rendered
    assert "src/pr_review_receipt/cli.py" in rendered
    assert "Risk level" in rendered


def test_render_json_is_valid_and_sorted() -> None:
    rendered = render_json(_receipt())

    assert '"repo_name": "diffdocket"' in rendered
    assert '"changes"' in rendered
