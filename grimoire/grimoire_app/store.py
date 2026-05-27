"""Filesystem storage for wiki."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

import frontmatter

WIKI_ROOT = Path.home() / "wiki"
RAW_DIR = WIKI_ROOT / "raw"
WIKI_DIR = WIKI_ROOT / "wiki"
SCHEMA_DIR = WIKI_ROOT / "schema"
LINKS_PATH = SCHEMA_DIR / "links.json"
TAGS_PATH = SCHEMA_DIR / "tags.json"
QUOTES_PATH = SCHEMA_DIR / "quotes.json"


def ensure_structure() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    for path, default in (
        (LINKS_PATH, {}),
        (TAGS_PATH, {}),
        (QUOTES_PATH, []),
    ):
        if not path.exists():
            path.write_text(json.dumps(default, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9а-яА-Я]+", "-", title.strip().lower()).strip("-")
    return slug or "note"


def new_note(title: str, *, wiki: bool = False) -> Path:
    ensure_structure()
    slug = slugify(title)
    target = WIKI_DIR if wiki else RAW_DIR
    filename = f"{slug}.md" if wiki else f"{date.today().isoformat()}_{slug}.md"
    path = target / filename
    if wiki:
        post = frontmatter.Post(
            f"# {title}\n\n## Суть атаки\n...\n",
            **{
                "title": title,
                "tags": ["mad"],
                "created": date.today().isoformat(),
                "updated": date.today().isoformat(),
                "links": [],
            },
        )
        path.write_text(frontmatter.dumps(post), encoding="utf-8")
    else:
        path.write_text(f"# {title}\n\n", encoding="utf-8")
    return path


def list_notes(*, wiki: bool = False) -> list[Path]:
    ensure_structure()
    target = WIKI_DIR if wiki else RAW_DIR
    return sorted(target.glob("*.md"))


def read_note(slug: str) -> Path:
    ensure_structure()
    for target in (WIKI_DIR, RAW_DIR):
        for path in target.glob("*.md"):
            if path.stem == slug or path.name.startswith(slug):
                return path
    raise FileNotFoundError(f"note not found: {slug}")


def search_notes(query: str) -> list[Path]:
    ensure_structure()
    hits = []
    q = query.lower()
    for path in list_notes() + list_notes(wiki=True):
        if q in path.read_text(encoding="utf-8").lower():
            hits.append(path)
    return hits


def add_link(src: str, dst: str) -> None:
    ensure_structure()
    data = json.loads(LINKS_PATH.read_text(encoding="utf-8"))
    data.setdefault(src, [])
    if dst not in data[src]:
        data[src].append(dst)
    LINKS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sync_schema() -> None:
    ensure_structure()
    links: dict[str, list[str]] = {}
    tags: dict[str, list[str]] = {}
    for path in list_notes(wiki=True):
        post = frontmatter.load(path)
        slug = path.stem
        links[slug] = list(post.metadata.get("links", []))
        for tag in post.metadata.get("tags", []):
            tags.setdefault(tag, []).append(slug)
    LINKS_PATH.write_text(json.dumps(links, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    TAGS_PATH.write_text(json.dumps(tags, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_quote(text: str, author: str, source: str, tags: list[str], lang: str) -> dict[str, Any]:
    ensure_structure()
    quotes = json.loads(QUOTES_PATH.read_text(encoding="utf-8"))
    next_id = f"q{len(quotes) + 1:03d}"
    item = {"id": next_id, "text": text, "author": author, "source": source, "tags": tags, "lang": lang}
    quotes.append(item)
    QUOTES_PATH.write_text(json.dumps(quotes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return item


def search_quotes(query: str) -> list[dict[str, Any]]:
    ensure_structure()
    q = query.lower()
    quotes = json.loads(QUOTES_PATH.read_text(encoding="utf-8"))
    return [item for item in quotes if q in json.dumps(item, ensure_ascii=False).lower()]


def export_html() -> Path:
    ensure_structure()
    html = ["<html><body><h1>grimoire</h1>"]
    for path in list_notes(wiki=True):
        html.append(f"<h2>{path.stem}</h2><pre>{path.read_text(encoding='utf-8')}</pre>")
    html.append("</body></html>")
    out = WIKI_ROOT / "export.html"
    out.write_text("\n".join(html), encoding="utf-8")
    return out
