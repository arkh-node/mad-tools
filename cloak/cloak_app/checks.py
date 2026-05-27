"""API-backed and local OPSEC checks."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import requests

from .config import AUDIT_PATH, load_layers, load_secrets


def hibp_check(email: str) -> dict[str, Any]:
    load_secrets()
    key = os.getenv("HIBP_API_KEY", "").strip()
    headers = {"hibp-api-key": key, "user-agent": "mad-cloak/0.1"} if key else {"user-agent": "mad-cloak/0.1"}
    resp = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}", headers=headers, timeout=30)
    if resp.status_code == 404:
        return {"email": email, "ok": True, "breaches": []}
    if resp.status_code == 401:
        return {"email": email, "ok": False, "error": "hibp_unauthorized"}
    resp.raise_for_status()
    data = resp.json()
    return {"email": email, "ok": True, "breaches": [item.get("Name") for item in data]}


def username_check(username: str) -> dict[str, Any]:
    results = []
    for label, url in {
        "github": f"https://github.com/{username}",
        "hackerone": f"https://hackerone.com/{username}",
        "bugcrowd": f"https://bugcrowd.com/{username}",
    }.items():
        try:
            resp = requests.get(url, timeout=20)
            results.append({"platform": label, "url": url, "status": resp.status_code, "present": resp.status_code == 200})
        except requests.RequestException as exc:
            results.append({"platform": label, "url": url, "status": "error", "present": False, "error": str(exc)})
    return {"username": username, "results": results}


def ip_check(ip: str) -> dict[str, Any]:
    load_secrets()
    out: dict[str, Any] = {"ip": ip}
    shodan_key = os.getenv("SHODAN_API_KEY", "").strip()
    if shodan_key:
        resp = requests.get(f"https://api.shodan.io/shodan/host/{ip}", params={"key": shodan_key}, timeout=30)
        out["shodan"] = {"status": resp.status_code}
        if resp.status_code == 200:
            data = resp.json()
            out["shodan"].update({"ports": data.get("ports", []), "org": data.get("org"), "vulns": list((data.get("vulns") or {}).keys()) if isinstance(data.get("vulns"), dict) else data.get("vulns", [])})
        else:
            out["shodan"]["error"] = resp.text[:240]
    else:
        out["shodan"] = {"error": "missing SHODAN_API_KEY"}

    abuse_key = os.getenv("ABUSEIPDB_KEY", "").strip()
    if abuse_key:
        resp = requests.get(
            "https://api.abuseipdb.com/api/v2/check",
            params={"ipAddress": ip, "maxAgeInDays": 90},
            headers={"Key": abuse_key, "Accept": "application/json"},
            timeout=30,
        )
        out["abuseipdb"] = {"status": resp.status_code}
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            out["abuseipdb"].update({"abuseConfidenceScore": data.get("abuseConfidenceScore"), "countryCode": data.get("countryCode"), "usageType": data.get("usageType")})
        else:
            out["abuseipdb"]["error"] = resp.text[:240]
    else:
        out["abuseipdb"] = {"error": "missing ABUSEIPDB_KEY"}
    return out


def git_email_check() -> dict[str, Any]:
    proc = subprocess.run(["git", "config", "--global", "--get", "user.email"], capture_output=True, text=True, check=False)
    return {"configured_email": proc.stdout.strip(), "ok": proc.returncode == 0}


def run_audit() -> dict[str, Any]:
    layers = load_layers().get("layers", {})
    report: dict[str, Any] = {"layers": [], "git": git_email_check()}
    for name, layer in layers.items():
        item: dict[str, Any] = {"layer": name, "name": layer.get("name"), "platforms": layer.get("platforms", [])}
        if layer.get("email"):
            try:
                item["email_check"] = hibp_check(layer["email"])
            except Exception as exc:
                item["email_check"] = {"email": layer["email"], "ok": False, "error": str(exc)}
        if layer.get("name"):
            item["username_check"] = username_check(str(layer["name"]))
        if layer.get("ip"):
            item["ip_check"] = ip_check(str(layer["ip"]))
        report["layers"].append(item)
    AUDIT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
