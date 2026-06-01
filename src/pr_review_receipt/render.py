from __future__ import annotations

import json

from .models import Receipt


def render_markdown(receipt: Receipt) -> str:
    lines: list[str] = []
    lines.append("# DiffDocket Receipt")
    lines.append("")
    lines.append(f"- Repository: `{receipt.repo_name}`")
    lines.append(f"- Base: `{receipt.base_ref}`")
    lines.append(f"- Head: `{receipt.head_ref}`")
    if receipt.repo_url:
        lines.append(f"- Repository URL: {receipt.repo_url}")
    lines.append(f"- Generated: `{receipt.generated_at.isoformat().replace('+00:00', 'Z')}`")
    lines.append(f"- Risk level: **{receipt.risk_level}**")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(receipt.summary)
    lines.append("")
    lines.append("## Changed Files")
    lines.append("")
    lines.append("| Path | Category | Status | + | - | Notes |")
    lines.append("| --- | --- | --- | ---: | ---: | --- |")
    for change in receipt.changes:
        note = change.note or ""
        lines.append(
            f"| `{change.path}` | {change.category} | {change.status} | {change.additions} | {change.deletions} | {note} |"
        )
    if not receipt.changes:
        lines.append("| _No file changes detected_ | - | - | -: | -: | - |")
    lines.append("")
    lines.append("## Review Focus")
    lines.append("")
    for item in receipt.review_focus:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Test Gaps")
    lines.append("")
    if receipt.test_gaps:
        for item in receipt.test_gaps:
            lines.append(f"- {item}")
    else:
        lines.append("- No obvious test gaps detected.")
    lines.append("")
    lines.append("## Release Note Draft")
    lines.append("")
    lines.append(receipt.release_note)
    return "\n".join(lines).rstrip() + "\n"


def render_json(receipt: Receipt) -> str:
    return json.dumps(receipt.to_dict(), indent=2, sort_keys=True) + "\n"
