from __future__ import annotations

import subprocess
from pathlib import Path

from pr_review_receipt.cli import main


def test_cli_writes_markdown_output(tmp_path: Path) -> None:
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
    (tests_dir / "test_app.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True, capture_output=True)

    (src_dir / "app.py").write_text("def hello():\n    return 'hello again'\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "update"], cwd=repo, check=True, capture_output=True)

    output = tmp_path / "receipt.md"
    exit_code = main(["--repo", str(repo), "--base", "HEAD~1", "--head", "HEAD", "--output", str(output)])

    assert exit_code == 0
    assert output.exists()
    assert "# DiffDocket Receipt" in output.read_text(encoding="utf-8")
