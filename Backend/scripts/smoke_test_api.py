#!/usr/bin/env python3
"""API sanity test for AigesX backend.

Flow:
1. Login via JWT token endpoint
2. Create scan job
3. Poll job status until terminal state
4. Fetch crash data and validate metadata fields
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
    start_url = f"{args.base_url}/api/scan/start/"
    crashes_url_tpl = f"{args.base_url}/api/scan/jobs/{{job_id}}/crashes/"
    status_url_tpl = f"{args.base_url}/api/scan/jobs/{{job_id}}/"

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

    print("[2/4] Create scan job...")
    start_resp = requests.post(
        start_url,
        headers=headers,
        json={"timeout_seconds": 30, "memory_limit_mb": 256, "cpu_limit": 0.5},
        timeout=args.timeout,
    )
    require(start_resp.status_code in (200, 201, 202), f"Job start failed: {start_resp.status_code} {start_resp.text}")

    start_body = start_resp.json()
    job_id = (start_body.get("job") or {}).get("id")
    require(bool(job_id), f"Missing job id: {pretty(start_body)}")

    print("[3/4] Poll job status...")
    final_status = None
    report_data = None
    for _ in range(120):
        status_resp = requests.get(status_url_tpl.format(job_id=job_id), headers=headers, timeout=args.timeout)
        require(status_resp.status_code == 200, f"Status failed: {status_resp.status_code} {status_resp.text}")
        status_body = status_resp.json()
        final_status = status_body.get("status")
        report_data = status_body.get("report_data")
        if final_status in {"COMPLETED", "FAILED"}:
            break
    require(final_status in {"COMPLETED", "FAILED"}, f"Unexpected final status: {final_status}")

    print("[4/4] Fetch crash data...")
    crashes_resp = requests.get(crashes_url_tpl.format(job_id=job_id), headers=headers, timeout=args.timeout)
    require(crashes_resp.status_code == 200, f"Crash fetch failed: {crashes_resp.status_code} {crashes_resp.text}")
    crashes_body = crashes_resp.json()
    crashes = crashes_body.get("crashes", [])

    for crash in crashes:
        details = crash.get("details") or {}
        if "crash_hash" in details:
            require(bool(details.get("crash_hash")), "Crash hash must not be empty")
            require(bool(details.get("crash_group_hash")), "Crash group hash must not be empty")

    if report_data:
        require("scan_summary" in report_data, "Status report missing scan_summary")
        require("vulnerability_summary" in report_data, "Status report missing vulnerability_summary")

    print("Sanity test passed.")
    print(f"Job status: {final_status}")
    print(f"Crash records: {len(crashes)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Smoke test failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
