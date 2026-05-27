from __future__ import annotations

import json
from typing import Any

import httpx

CHAOS = ["text", 0, -1, True, False, None, [], {}, {"nested": ["boom"]}]
BOUNDARY = ["", "A" * 10000, "../../../etc/passwd", {"$gt": ""}, "<script>alert(1)</script>", "; ls -la", 0, -1, 2**31]
TYPE_CONFUSION = [{"value": []}, {"value": {}}, {"value": True}, {"value": 1337}]


def payloads() -> dict[str, list[Any]]:
    return {"chaos": CHAOS, "boundary": BOUNDARY, "type-confusion": TYPE_CONFUSION}


def _score_response(status: int, text: str) -> str:
    lower = text.lower()
    if status >= 500:
        return "500/exception"
    if "../" in text:
        return "path-traversal-hint"
    if any(token in lower for token in ("sql", "traceback", "syntax error", "permission denied", "command not found")):
        return "injection-hint"
    return "ok"


def fuzz_url(url: str, *, tool: str | None = None, strategy: str = "chaos") -> list[dict[str, Any]]:
    chosen = payloads().get(strategy, CHAOS)
    results = []
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        for item in chosen:
            body = {"tool": tool or "test", "args": item}
            try:
                resp = client.post(url, json=body)
                text = resp.text[:500]
                results.append({"payload": item, "status_code": resp.status_code, "verdict": _score_response(resp.status_code, text), "preview": text})
            except httpx.HTTPError as exc:
                results.append({"payload": item, "status_code": 0, "verdict": "transport-error", "preview": str(exc)})
    return results
