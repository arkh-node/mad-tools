"""Scope snapshot logic."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from .config import load_secrets
from .store import get_program, load_latest, previous_snapshot, program_dir, write_snapshot


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_entry(value: str) -> dict[str, str]:
    return {"type": "url", "value": value.strip(), "severity": "unknown"}


def _from_text(text: str) -> tuple[list[dict[str, str]], list[str]]:
    in_scope: list[dict[str, str]] = []
    out_of_scope: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        lower = line.lower()
        if lower.startswith("out:") or "out of scope" in lower:
            value = line.split(":", 1)[-1].strip()
            if value:
                out_of_scope.append(value)
            continue
        if line.startswith(("*", "http", ".")) or "." in line:
            in_scope.append(_normalize_entry(line.lstrip("-* ").strip()))
    return in_scope, out_of_scope


def _snapshot_from_file(path: str) -> dict[str, Any]:
    text = Path(path).expanduser().read_text(encoding="utf-8")
    in_scope, out_of_scope = _from_text(text)
    return {"in_scope": in_scope, "out_of_scope": out_of_scope, "notes": ""}


def _snapshot_from_url(url: str) -> dict[str, Any]:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    text = re.sub(r"<[^>]+>", "\n", resp.text)
    in_scope, out_of_scope = _from_text(text)
    return {"in_scope": in_scope, "out_of_scope": out_of_scope, "notes": f"Fetched from {url}"}


def _snapshot_from_h1(handle: str) -> dict[str, Any]:
    load_secrets()
    import os

    token = os.getenv("H1_API_TOKEN", "").strip()
    username = os.getenv("H1_USERNAME", "").strip()
    if not token or not username:
        raise RuntimeError("missing H1_API_TOKEN or H1_USERNAME in ~/.config/mad/secrets.env")
    resp = requests.get(
        f"https://api.hackerone.com/v1/hackers/programs/{handle}/policy",
        headers={"Accept": "application/json"},
        auth=(username, token),
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    attributes = data.get("data", {}).get("attributes", {})
    text = "\n".join(
        [
            attributes.get("structured_scopes", ""),
            attributes.get("submission_guidelines", ""),
            attributes.get("eligible_for_bounty", ""),
        ]
    )
    in_scope, out_of_scope = _from_text(text)
    return {"in_scope": in_scope, "out_of_scope": out_of_scope, "notes": f"H1 policy for {handle}"}


def take_snapshot(name: str) -> Path:
    program = get_program(name)
    source = program["source"]
    source_type = program["source_type"]
    if source_type == "file":
        data = _snapshot_from_file(source)
    elif source_type == "url":
        data = _snapshot_from_url(source)
    elif source_type == "h1":
        data = _snapshot_from_h1(source)
    else:
        raise RuntimeError(f"unsupported source type: {source_type}")

    snapshot = {
        "program": name,
        "timestamp": _now(),
        "in_scope": data["in_scope"],
        "out_of_scope": data["out_of_scope"],
        "notes": data.get("notes", ""),
    }
    return write_snapshot(name, snapshot)


def diff_snapshot(name: str) -> tuple[str, Path]:
    latest = load_latest(name)
    if latest is None:
        raise FileNotFoundError(f"no snapshot for program: {name}")
    previous = previous_snapshot(name)
    if previous is None:
        text = f"# Scope Diff — {name}\n\nno changes\n"
        path = program_dir(name) / f"diff_{latest['timestamp'].replace(':', '-')}.md"
        path.write_text(text, encoding="utf-8")
        return text, path
    latest_values = {item["value"] for item in latest.get("in_scope", [])}
    previous_values = {item["value"] for item in (previous or {}).get("in_scope", [])}
    added = sorted(latest_values - previous_values)
    removed = sorted(previous_values - latest_values)
    lines = [f"# Scope Diff — {name}", ""]
    if not added and not removed:
        lines.append("no changes")
    if added:
        lines.append("## Added")
        lines.extend(f"- {item}" for item in added)
    if removed:
        lines.append("## Removed")
        lines.extend(f"- {item}" for item in removed)
    text = "\n".join(lines) + "\n"
    path = program_dir(name) / f"diff_{latest['timestamp'].replace(':', '-')}.md"
    path.write_text(text, encoding="utf-8")
    return text, path
