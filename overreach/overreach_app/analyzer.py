from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from mcpx_app.probe import probe_server

PATTERNS = [
    ("critical", 10, ("shell", "exec", "run", "eval", "sudo", "root")),
    ("high", 8, ("delete", "remove", "drop", "fetch", "http", "file", "write")),
    ("medium", 5, ("email", "smtp", "request")),
]


def score_tool(tool: dict[str, Any]) -> dict[str, Any]:
    name = str(tool.get("name", ""))
    desc = str(tool.get("description", ""))
    schema = tool.get("inputSchema") or tool.get("input_schema") or {}
    text = (name + " " + desc + " " + json.dumps(schema, ensure_ascii=False)).lower()
    score = 0
    notes = []
    for label, points, markers in PATTERNS:
        if any(marker in text for marker in markers):
            score = max(score, points)
            notes.append(label)
    if schema == {}:
        score = max(score, 5)
        notes.append("wide-schema")
    return {"name": name, "score": min(score, 10), "notes": ",".join(notes) or "low"}


async def scan_url(url: str) -> dict[str, Any]:
    data = await probe_server(url)
    tools = [score_tool(tool) for tool in data.get("tools", [])]
    total = round(sum(item["score"] for item in tools) / len(tools), 2) if tools else 0
    return {"url": url, "tools": tools, "total_risk": total}


def write_report(data: dict[str, Any]) -> Path:
    out = Path.home() / ".local" / "share" / "mad" / "overreach"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "report.html"
    rows = "".join(f"<tr><td>{item['name']}</td><td>{item['score']}</td><td>{item['notes']}</td></tr>" for item in data["tools"])
    path.write_text(f"<html><body><h1>Overreach {data['url']}</h1><table>{rows}</table></body></html>", encoding="utf-8")
    return path
