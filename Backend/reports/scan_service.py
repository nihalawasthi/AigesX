from __future__ import annotations

from typing import Any


def run_full_scan() -> tuple[dict[str, Any], str]:
    """
    Execute a full system scan and return:
    - report data as dict
    - generated report file name
    """
    from scan_engine.core.reporter import Reporter
    from scan_engine.core.scanner import AutomatedScannerEngine, Scanner

    scanner = Scanner()
    basic_vulnerabilities = scanner.scan_system() or []

    automated_scanner = AutomatedScannerEngine()
    deep_scan_results = automated_scanner.deep_system_scan()

    if isinstance(deep_scan_results, list):
        deep_scan_vulnerabilities = deep_scan_results
    elif isinstance(deep_scan_results, dict):
        deep_scan_vulnerabilities = deep_scan_results.get("vulnerabilities", [])
    else:
        deep_scan_vulnerabilities = []

    all_vulnerabilities = basic_vulnerabilities + deep_scan_vulnerabilities

    reporter = Reporter(all_vulnerabilities)
    report_data = reporter.generate_detailed_report()
    return report_data, reporter.report_name
