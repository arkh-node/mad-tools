"""Finding data structures."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

STATUSES = ("queue", "in-progress", "reported", "disclosed", "rejected")
PLATFORMS = ("h1", "bugcrowd", "intigriti", "immunefi", "private")
SEVERITIES = ("critical", "high", "medium", "low", "info")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(slots=True)
class Finding:
    id: str
    created: str
    updated: str
    title: str
    platform: str
    program: str
    severity: str
    type: str
    status: str
    target: str
    description: str
    steps: list[str] = field(default_factory=list)
    impact: str = ""
    cvss: str | None = None
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    attachments: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Finding":
        return cls(**data)

    @classmethod
    def create(cls, **values: Any) -> "Finding":
        stamp = now_iso()
        return cls(created=stamp, updated=stamp, **values)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
