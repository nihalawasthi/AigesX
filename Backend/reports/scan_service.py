from __future__ import annotations

import datetime
import json
from typing import Any

from .target_cve_correlation import correlate_target_with_cves


def run_full_scan(
    *,
    binary_artifact=None,
    source_artifact=None,
    seed_artifact=None,
    timeout_seconds: int = 5,
    memory_limit_mb: int = 512,
    cpu_limit: float = 1.0,
) -> tuple[dict[str, Any], str]:
    """
    Execute target-oriented CVE correlation scan and return:
    - report data as dict
    - generated report file name
    """
    report_data = correlate_target_with_cves(
        binary_artifact=binary_artifact,
        source_artifact=source_artifact,
        seed_artifact=seed_artifact,
        timeout_seconds=timeout_seconds,
        memory_limit_mb=memory_limit_mb,
        cpu_limit=cpu_limit,
    )

    report_name = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_report.json"
    with open(report_name, "w", encoding="utf-8") as report_file:
        json.dump(report_data, report_file, indent=4)

    return report_data, report_name
