from __future__ import annotations

import math
from collections import Counter
from typing import Any

import httpx


def _tokens(text: str) -> list[str]:
    return [token for token in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split() if token]


def cosine_text(left: str, right: str) -> float:
    left_counts = Counter(_tokens(left))
    right_counts = Counter(_tokens(right))
    if not left_counts or not right_counts:
        return 0.0
    vocab = set(left_counts) | set(right_counts)
    numerator = sum(left_counts[token] * right_counts[token] for token in vocab)
    left_norm = math.sqrt(sum(value * value for value in left_counts.values()))
    right_norm = math.sqrt(sum(value * value for value in right_counts.values()))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


def generate_candidates(target: str, steps: int = 12) -> list[str]:
    words = _tokens(target) or ["target"]
    variants = [
        target,
        f"{target} summary",
        f"notes about {target}",
        f"{target} internal memo",
        " ".join(reversed(words)),
        " ".join(words + words[:2]),
    ]
    out: list[str] = []
    for idx in range(steps):
        base = variants[idx % len(variants)]
        out.append(f"{base} variant {idx + 1}")
    return out


def rank(left: str, right: str) -> float:
    return cosine_text(left, right)


def find(target: str, embed_url: str | None = None) -> dict[str, Any]:
    if embed_url:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.post(embed_url, json={"text": target})
        return {"mode": "remote", "candidate": target, "score": 1.0, "preview": response.text[:200]}
    best_text = ""
    best_score = -1.0
    for candidate in generate_candidates(target):
        score = rank(target, candidate)
        if score > best_score:
            best_text = candidate
            best_score = score
    return {"mode": "fallback", "candidate": best_text, "score": best_score}
