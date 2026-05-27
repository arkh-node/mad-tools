"""Template loading and rendering."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path
from typing import Any

from .catalog import PLATFORMS, SEVERITY_CWE, VULN_TYPES


@dataclass(slots=True)
class TemplateContext:
    platform: str
    vuln_type: str
    program: str = "[program name]"
    severity: str = "Medium"
    target: str = "[TARGET]"
    vector: str = "[VECTOR]"
    cvss: str = "[score if applicable]"
    cvss_vector: str = "[CVSS:3.1/...]"
    bug_url: str = "[Bug URL]"
    poc_url: str = "[Proof of concept URL]"
    payload: str = "[Exact payload used]"
    response: str = "[LLM response demonstrating the issue]"


def supported_platforms() -> tuple[str, ...]:
    return PLATFORMS


def supported_types() -> tuple[str, ...]:
    return VULN_TYPES


def validate(platform: str, vuln_type: str) -> None:
    if platform not in PLATFORMS:
        raise ValueError(f"unsupported platform: {platform}")
    if vuln_type not in VULN_TYPES:
        raise ValueError(f"unsupported vulnerability type: {vuln_type}")


def template_text(platform: str, vuln_type: str) -> str:
    validate(platform, vuln_type)
    return resources.files("dt").joinpath("templates", platform, f"{vuln_type}.md").read_text(encoding="utf-8")


def default_context(platform: str, vuln_type: str) -> dict[str, str]:
    validate(platform, vuln_type)
    pretty_type = vuln_type.replace("-", " ").title()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "platform": platform,
        "platform_name": {
            "h1": "HackerOne",
            "bugcrowd": "Bugcrowd",
            "intigriti": "Intigriti",
        }[platform],
        "type": vuln_type,
        "type_label": pretty_type,
        "severity": "Medium",
        "severity_label": "MEDIUM",
        "program": "[program name]",
        "target": "[TARGET]",
        "vector": "[VECTOR]",
        "cvss": "[score if applicable]",
        "cvss_vector": "[CVSS:3.1/...]",
        "cwe": SEVERITY_CWE.get(vuln_type, "CWE-693 (Protection Mechanism Failure)"),
        "bug_url": "[Bug URL]",
        "poc_url": "[Proof of concept URL]",
        "payload": "[Exact payload used]",
        "response": "[LLM response demonstrating the issue]",
        "generated_at": now,
    }


def render_template(platform: str, vuln_type: str, context: dict[str, Any] | None = None) -> str:
    values = default_context(platform, vuln_type)
    if context:
        values.update({k: "" if v is None else str(v) for k, v in context.items()})
    rendered = template_text(platform, vuln_type)
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def write_template(
    platform: str,
    vuln_type: str,
    *,
    output_path: str | Path | None = None,
    context: dict[str, Any] | None = None,
) -> Path:
    rendered = render_template(platform, vuln_type, context=context)
    if output_path is None:
        safe_program = (context or {}).get("program", "report")
        safe_program = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in str(safe_program)).strip("-") or "report"
        output_path = Path.cwd() / f"{platform}__{vuln_type}__{safe_program}.md"
    path = Path(output_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")
    return path
