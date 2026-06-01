from __future__ import annotations

import subprocess
from pathlib import Path

from pr_review_receipt.analysis import build_receipt_from_changes, classify_path, collect_changes
from pr_review_receipt.models import Change


def test_classify_path_covers_core_categories() -> None:
    cases = {
        ".github/workflows/ci.yml": "workflow",
        "action.yml": "workflow",
        "SECURITY.md": "security",
        "pyproject.toml": "dependency",
        "requirements.txt": "dependency",
        "tests/test_cli.py": "tests",
        "src/pr_review_receipt/analysis.py": "source",
        "docs/ROADMAP.md": "docs",
        "README.md": "docs",
        "config/settings.json": "config",
        "notes/custom.txt": "other",
    }
    for path, expected in cases.items():
        assert classify_path(path) == expected


def test_build_receipt_flags_missing_tests_for_source_changes() -> None:
    receipt = build_receipt_from_changes(
        repo_name="diffdocket",
        repo_path="/tmp/diffdocket",
        base_ref="HEAD~1",
        head_ref="HEAD",
        changes=[
            Change(
                path="src/pr_review_receipt/analysis.py",
                status="M",
                additions=14,
                deletions=3,
                category="source",
            ),
            Change(
                path="README.md",
                status="M",
                additions=4,
                deletions=0,
                category="docs",
            ),
        ],
    )

    assert receipt.risk_level == "medium"
    assert "No test files changed" in receipt.test_gaps[0]
    assert any("Review the changed source paths" in item for item in receipt.review_focus)


def test_collect_changes_from_git(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True, capture_output=True)

    src_dir = repo / "src"
    tests_dir = repo / "tests"
    src_dir.mkdir()
    tests_dir.mkdir()
    (src_dir / "app.py").write_text("def hello():\n    return 'hello'\n", encoding="utf-8")
    (tests_dir / "test_app.py").write_text(
        "def test_placeholder():\n    assert 1 == 1\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True, capture_output=True)

    (src_dir / "app.py").write_text("def hello():\n    return 'hello world'\n", encoding="utf-8")
    (tests_dir / "test_app.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "update"], cwd=repo, check=True, capture_output=True)

    changes = collect_changes(str(repo), "HEAD~1", "HEAD")

    assert len(changes) == 2
    assert {change.category for change in changes} == {"source", "tests"}
