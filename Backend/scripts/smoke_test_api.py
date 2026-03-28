#!/usr/bin/env python3
"""Simple API smoke test for AigesX backend.

Flow:
1. Login via JWT token endpoint
2. Trigger a scan
3. Fetch latest report
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import requests


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def pretty(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="AigesX API smoke test")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Backend base URL")
    parser.add_argument("--username", required=True, help="Django username")
    parser.add_argument("--password", required=True, help="Django password")
    parser.add_argument("--timeout", type=int, default=300, help="Request timeout seconds")
    args = parser.parse_args()

    token_url = f"{args.base_url}/api/auth/token/"
    scan_url = f"{args.base_url}/api/scan/"
    latest_url = f"{args.base_url}/api/latest-report/"

    print("[1/3] Login...")
    token_resp = requests.post(
        token_url,
        json={"username": args.username, "password": args.password},
        timeout=args.timeout,
    )
    require(token_resp.status_code == 200, f"Login failed: {token_resp.status_code} {token_resp.text}")

    token_body = token_resp.json()
    access = token_body.get("access")
    require(bool(access), "Missing access token in login response")

    headers = {
        "Authorization": f"Bearer {access}",
        "Content-Type": "application/json",
    }

    print("[2/3] Trigger scan...")
    scan_resp = requests.post(scan_url, headers=headers, json={}, timeout=args.timeout)
    require(scan_resp.status_code in (200, 201), f"Scan request failed: {scan_resp.status_code} {scan_resp.text}")

    scan_body = scan_resp.json()
    require("report_data" in scan_body, f"Scan response missing report_data: {pretty(scan_body)}")

    print("[3/3] Fetch latest report...")
    latest_resp = requests.get(latest_url, headers=headers, timeout=args.timeout)
    require(latest_resp.status_code == 200, f"Latest report failed: {latest_resp.status_code} {latest_resp.text}")

    latest_body = latest_resp.json()
    require("scan_summary" in latest_body, "Latest report missing scan_summary")
    require("vulnerability_summary" in latest_body, "Latest report missing vulnerability_summary")

    print("Smoke test passed.")
    print(f"Risk score: {latest_body.get('scan_summary', {}).get('risk_score')}")
    print(f"Total vulnerabilities: {latest_body.get('scan_summary', {}).get('total_vulnerabilities')}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Smoke test failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
