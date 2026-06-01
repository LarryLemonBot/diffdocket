from __future__ import annotations

import subprocess
from collections import Counter
from pathlib import Path

from .models import Change, Receipt

DEPENDENCY_FILES = {
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "requirements.txt",
    "requirements-dev.txt",
    "Pipfile",
    "Pipfile.lock",
    "Cargo.toml",
    "Cargo.lock",
    "go.mod",
    "go.sum",
}

DOC_FILES = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
}


def _run_git(repo_path: str, *args: str) -> list[str]:
    completed = subprocess.run(
        ["git", "-C", repo_path, *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in completed.stdout.splitlines() if line.strip()]


def _parse_num(value: str) -> int:
    return 0 if value == "-" else int(value)


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def classify_path(path: str) -> str:
    normalized = _normalize_path(path)
    if normalized == "action.yml" or normalized.startswith(".github/workflows/"):
        return "workflow"
    if normalized == "SECURITY.md" or normalized.endswith("/SECURITY.md"):
        return "security"
    if normalized in DEPENDENCY_FILES:
        return "dependency"
    if normalized.startswith("tests/") or normalized.startswith("test/"):
        return "tests"
    if "/tests/" in normalized or normalized.endswith("_test.py") or normalized.endswith(
        ".test.js"
    ):
        return "tests"
    if normalized in DOC_FILES or normalized.startswith("docs/") or normalized.endswith(".md"):
        return "docs"
    if normalized.startswith("src/") or normalized.startswith("app/") or normalized.startswith(
        "lib/"
    ):
        return "source"
    if normalized.endswith((".py", ".js", ".ts", ".tsx", ".jsx")):
        return "source"
    if normalized.endswith((".yml", ".yaml", ".json", ".toml", ".ini", ".cfg")):
        return "config"
    return "other"


def collect_changes(repo_path: str, base_ref: str, head_ref: str) -> list[Change]:
    name_status = _run_git(repo_path, "diff", "--name-status", f"{base_ref}..{head_ref}")
    numstat = _run_git(repo_path, "diff", "--numstat", f"{base_ref}..{head_ref}")

    if len(name_status) != len(numstat):
        raise RuntimeError("git diff output mismatch between name-status and numstat")

    changes: list[Change] = []
    for status_line, numstat_line in zip(name_status, numstat):
        status_parts = status_line.split("\t")
        numstat_parts = numstat_line.split("\t")
        status = status_parts[0]
        if len(numstat_parts) != 3:
            raise RuntimeError(f"unexpected numstat line: {numstat_line}")

        additions = _parse_num(numstat_parts[0])
        deletions = _parse_num(numstat_parts[1])

        previous_path = None
        if status.startswith("R") and len(status_parts) >= 3:
            previous_path = status_parts[1]
            path = status_parts[2]
            note = f"renamed from {previous_path}"
        else:
            path = status_parts[-1]
            note = ""

        changes.append(
            Change(
                path=path,
                status=status,
                additions=additions,
                deletions=deletions,
                category=classify_path(path),
                note=note,
                previous_path=previous_path,
            )
        )

    return changes


def _get_repo_url(repo_path: str) -> str | None:
    try:
        remote = _run_git(repo_path, "remote", "get-url", "origin")[0]
    except Exception:
        return None

    if remote.startswith("git@github.com:"):
        owner_repo = remote.removeprefix("git@github.com:").removesuffix(".git")
        return f"https://github.com/{owner_repo}"
    if remote.startswith("https://github.com/"):
        return remote.removesuffix(".git")
    return remote


def _risk_level(categories: Counter[str], has_test_changes: bool, file_count: int, line_count: int) -> str:
    score = 0
    score += categories.get("security", 0) * 5
    score += categories.get("workflow", 0) * 4
    score += categories.get("dependency", 0) * 4
    score += categories.get("source", 0) * 3
    score += categories.get("config", 0) * 2
    score -= categories.get("tests", 0)

    if not has_test_changes and (categories.get("source", 0) or categories.get("dependency", 0) or categories.get("workflow", 0)):
        score += 2

    if file_count >= 8:
        score += 1
    if line_count > 300:
        score += 1

    if score <= 3:
        return "low"
    if score <= 7:
        return "medium"
    return "high"


def _review_focus(changes: list[Change], categories: Counter[str], has_test_changes: bool) -> list[str]:
    focus: list[str] = []
    if categories.get("security"):
        focus.append("Inspect security-sensitive changes before merge.")
    if categories.get("workflow"):
        focus.append("Verify CI or action changes with a clean test run.")
    if categories.get("dependency"):
        focus.append("Check dependency changes for runtime and lockfile impact.")
    if categories.get("source"):
        focus.append("Review the changed source paths for regressions.")
    if categories.get("config"):
        focus.append("Confirm configuration changes match the intended runtime behavior.")
    if categories.get("docs") and not (categories.get("source") or categories.get("dependency")):
        focus.append("Docs changed without code, so verify the docs still match current behavior.")
    if not has_test_changes and (categories.get("source") or categories.get("dependency") or categories.get("workflow")):
        focus.append("No test files changed in this patch; add or update tests if behavior changed.")
    if not focus:
        focus.append("This patch is low complexity; a quick smoke review should be enough.")
    return focus


def _test_gaps(changes: list[Change], categories: Counter[str]) -> list[str]:
    gaps: list[str] = []
    if categories.get("source") or categories.get("dependency") or categories.get("workflow"):
        if not any(change.category == "tests" for change in changes):
            gaps.append("No test files changed alongside code, dependency, or workflow updates.")
    if categories.get("security"):
        gaps.append("Security-sensitive paths changed; add a targeted verification step if possible.")
    return gaps


def _release_note(categories: Counter[str], changes: list[Change], risk_level: str) -> str:
    sections: list[str] = []
    if categories.get("source"):
        sections.append(f"{categories['source']} source file(s) updated")
    if categories.get("tests"):
        sections.append(f"{categories['tests']} test file(s) updated")
    if categories.get("dependency"):
        sections.append("dependency metadata updated")
    if categories.get("workflow"):
        sections.append("CI or action logic updated")
    if categories.get("docs"):
        sections.append("documentation updated")
    if categories.get("security"):
        sections.append("security-sensitive files updated")
    if not sections:
        sections.append("repository metadata updated")

    return f"{'; '.join(sections).capitalize()}. Risk level: {risk_level}."


def build_receipt_from_changes(
    repo_name: str,
    repo_path: str,
    base_ref: str,
    head_ref: str,
    changes: list[Change],
    repo_url: str | None = None,
) -> Receipt:
    category_counts = Counter(change.category for change in changes)
    file_count = len(changes)
    line_count = sum(change.lines_changed for change in changes)
    has_test_changes = any(change.category == "tests" for change in changes)
    risk_level = _risk_level(category_counts, has_test_changes, file_count, line_count)
    summary = f"{file_count} file(s) changed, {sum(change.additions for change in changes)} insertions(+), {sum(change.deletions for change in changes)} deletions(-)."

    return Receipt(
        repo_name=repo_name,
        repo_path=repo_path,
        repo_url=repo_url,
        base_ref=base_ref,
        head_ref=head_ref,
        changes=changes,
        categories=dict(sorted(category_counts.items())),
        risk_level=risk_level,
        summary=summary,
        review_focus=_review_focus(changes, category_counts, has_test_changes),
        test_gaps=_test_gaps(changes, category_counts),
        release_note=_release_note(category_counts, changes, risk_level),
    )


def build_receipt(repo_path: str, base_ref: str = "HEAD~1", head_ref: str = "HEAD") -> Receipt:
    repo_root = Path(repo_path).resolve()
    repo_name = repo_root.name
    repo_url = _get_repo_url(str(repo_root))
    changes = collect_changes(str(repo_root), base_ref, head_ref)
    return build_receipt_from_changes(
        repo_name=repo_name,
        repo_path=str(repo_root),
        base_ref=base_ref,
        head_ref=head_ref,
        changes=changes,
        repo_url=repo_url,
    )

