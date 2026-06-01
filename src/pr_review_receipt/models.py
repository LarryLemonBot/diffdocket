from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Change:
    path: str
    status: str
    additions: int
    deletions: int
    category: str
    note: str = ""
    previous_path: str | None = None

    @property
    def lines_changed(self) -> int:
        return self.additions + self.deletions


@dataclass(frozen=True)
class Receipt:
    repo_name: str
    repo_path: str
    base_ref: str
    head_ref: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    changes: list[Change] = field(default_factory=list)
    categories: dict[str, int] = field(default_factory=dict)
    risk_level: str = "low"
    summary: str = ""
    review_focus: list[str] = field(default_factory=list)
    test_gaps: list[str] = field(default_factory=list)
    release_note: str = ""
    repo_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_name": self.repo_name,
            "repo_path": self.repo_path,
            "repo_url": self.repo_url,
            "base_ref": self.base_ref,
            "head_ref": self.head_ref,
            "generated_at": self.generated_at.isoformat().replace("+00:00", "Z"),
            "categories": dict(sorted(self.categories.items())),
            "risk_level": self.risk_level,
            "summary": self.summary,
            "review_focus": list(self.review_focus),
            "test_gaps": list(self.test_gaps),
            "release_note": self.release_note,
            "changes": [asdict(change) for change in self.changes],
        }

