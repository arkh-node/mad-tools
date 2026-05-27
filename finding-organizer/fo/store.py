"""Filesystem store for findings."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Finding, now_iso

DATA_DIR = Path.home() / ".local" / "share" / "mad" / "findings"


def ensure_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def _finding_path(finding_id: str) -> Path:
    return ensure_data_dir() / f"{finding_id}.json"


def next_id() -> str:
    ensure_data_dir()
    ids = []
    for path in DATA_DIR.glob("F-*.json"):
        try:
            ids.append(int(path.stem.split("-", 1)[1]))
        except (IndexError, ValueError):
            continue
    return f"F-{(max(ids, default=0) + 1):03d}"


def save_finding(finding: Finding) -> Path:
    path = _finding_path(finding.id)
    finding.updated = now_iso()
    path.write_text(json.dumps(finding.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def load_finding(finding_id: str) -> Finding:
    path = _finding_path(finding_id)
    if not path.exists():
        raise FileNotFoundError(f"finding not found: {finding_id}")
    return Finding.from_dict(json.loads(path.read_text(encoding="utf-8")))


def list_findings(status: str | None = None) -> list[Finding]:
    ensure_data_dir()
    items = []
    for path in sorted(DATA_DIR.glob("F-*.json")):
        items.append(Finding.from_dict(json.loads(path.read_text(encoding="utf-8"))))
    if status:
        items = [item for item in items if item.status == status]
    return sorted(items, key=lambda item: item.id)


def update_status(finding_id: str, new_status: str) -> Finding:
    finding = load_finding(finding_id)
    finding.status = new_status
    save_finding(finding)
    return finding
