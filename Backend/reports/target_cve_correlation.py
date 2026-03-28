from __future__ import annotations

import datetime
import json
import os
import re
from collections import Counter
from typing import Any

from django.conf import settings


TOKEN_RE = re.compile(r"[a-zA-Z0-9_\-\.]{3,}")


def _tokenize(value: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(value or "")}


def _load_cve_patterns() -> list[dict[str, Any]]:
    patterns_file = os.path.join(settings.BASE_DIR, "scan_engine", "cve_data", "cve_patterns.json")
    if not os.path.exists(patterns_file):
        return []

    try:
        with open(patterns_file, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, list):
            return data
    except (OSError, json.JSONDecodeError):
        return []
    return []


def _extract_binary_tokens(binary_path: str, limit_bytes: int = 2_000_000) -> set[str]:
    if not binary_path or not os.path.exists(binary_path):
        return set()

    try:
        with open(binary_path, "rb") as handle:
            content = handle.read(limit_bytes)
        text = content.decode("utf-8", errors="ignore")
        return _tokenize(text)
    except OSError:
        return set()


def _extract_source_tokens(repo_url: str) -> set[str]:
    return _tokenize(repo_url or "")


def _extract_pattern_tokens(pattern: dict[str, Any]) -> set[str]:
    description = pattern.get("description") or ""
    products = pattern.get("affected_products") or []
    product_tokens: set[str] = set()
    for product in products:
        product_tokens |= _tokenize(str(product))
    return _tokenize(description) | product_tokens


def _score_pattern(evidence_tokens: set[str], pattern_tokens: set[str]) -> float:
    if not evidence_tokens or not pattern_tokens:
        return 0.0
    overlap = evidence_tokens & pattern_tokens
    if not overlap:
        return 0.0
    return len(overlap) / max(1, len(pattern_tokens))


def _score_to_severity(score: float) -> str:
    if score >= 0.2:
        return "HIGH"
    if score >= 0.1:
        return "MEDIUM"
    return "LOW"


def _build_target_info(binary_artifact, source_artifact) -> dict[str, Any]:
    target_type = "UNKNOWN"
    display_target = "No target selected"

    if binary_artifact and binary_artifact.file:
        target_type = "BINARY"
        display_target = os.path.basename(binary_artifact.file.name)
    elif source_artifact and source_artifact.repo_url:
        target_type = "SOURCE"
        display_target = source_artifact.repo_url

    return {
        "target_type": target_type,
        "target": display_target,
        "binary_artifact_id": binary_artifact.id if binary_artifact else None,
        "source_artifact_id": source_artifact.id if source_artifact else None,
    }


def correlate_target_with_cves(*, binary_artifact=None, source_artifact=None) -> dict[str, Any]:
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    patterns = _load_cve_patterns()

    binary_tokens = set()
    binary_path = None
    if binary_artifact and binary_artifact.file:
        binary_path = binary_artifact.file.path
        binary_tokens = _extract_binary_tokens(binary_path)

    source_tokens = set()
    source_url = None
    if source_artifact and source_artifact.repo_url:
        source_url = source_artifact.repo_url
        source_tokens = _extract_source_tokens(source_url)

    evidence_tokens = binary_tokens | source_tokens

    scored_matches: list[dict[str, Any]] = []
    for pattern in patterns:
        pattern_tokens = _extract_pattern_tokens(pattern)
        score = _score_pattern(evidence_tokens, pattern_tokens)
        if score <= 0:
            continue
        scored_matches.append(
            {
                "pattern": pattern,
                "score": score,
                "severity": _score_to_severity(score),
            }
        )

    scored_matches.sort(key=lambda item: item["score"], reverse=True)
    top_matches = scored_matches[:15]

    vulnerabilities: list[dict[str, Any]] = []
    for match in top_matches:
        pattern = match["pattern"]
        cve_id = pattern.get("id")
        vulnerabilities.append(
            {
                "severity": match["severity"],
                "type": "CVE_CORRELATION",
                "description": pattern.get("description", "Potential CVE pattern match"),
                "timestamp": now_iso,
                "component": os.path.basename(binary_path) if binary_path else (source_url or "unknown_target"),
                "affected_service": None,
                "details": {
                    "match_score": round(match["score"], 4),
                    "match_reason": "Token overlap between target evidence and CVE metadata",
                    "affected_products": pattern.get("affected_products", [])[:5],
                },
                "recommendation": "Validate this potential match with targeted reproduction and patch verification.",
                "cve_id": cve_id,
                "potential_match_indicator": True,
            }
        )

    if not vulnerabilities:
        vulnerabilities.append(
            {
                "severity": "LOW",
                "type": "CVE_CORRELATION",
                "description": "No strong CVE pattern matches were identified for the selected target.",
                "timestamp": now_iso,
                "component": os.path.basename(binary_path) if binary_path else (source_url or "unknown_target"),
                "affected_service": None,
                "details": {
                    "match_score": 0.0,
                    "match_reason": "Insufficient overlapping evidence with known CVE patterns",
                },
                "recommendation": "Provide richer seed corpus and rerun fuzzing to improve correlation quality.",
                "cve_id": None,
                "potential_match_indicator": False,
            }
        )

    severity_counter = Counter(v["severity"] for v in vulnerabilities)
    category_counter = Counter(v["type"] for v in vulnerabilities)
    risk_score = round(min(100.0, sum({"CRITICAL": 10, "HIGH": 8, "MEDIUM": 5, "LOW": 2}.get(v["severity"], 1) for v in vulnerabilities) / max(1, len(vulnerabilities)) * 10), 2)

    target_info = _build_target_info(binary_artifact=binary_artifact, source_artifact=source_artifact)
    total_matches = sum(1 for v in vulnerabilities if v.get("cve_id"))

    report = {
        "scan_summary": {
            "generated_at": now_iso,
            "system_info": {
                "platform": "AigesX Target Examination",
                "version": "MVP",
                "machine": target_info["target_type"],
                "processor": "n/a",
                "architecture": "n/a",
            },
            "target_info": target_info,
            "risk_score": risk_score,
            "total_vulnerabilities": len(vulnerabilities),
            "unique_categories": len(category_counter),
        },
        "vulnerability_summary": {
            "by_severity": {
                "CRITICAL": severity_counter.get("CRITICAL", 0),
                "HIGH": severity_counter.get("HIGH", 0),
                "MEDIUM": severity_counter.get("MEDIUM", 0),
                "LOW": severity_counter.get("LOW", 0),
            },
            "by_category": dict(category_counter),
            "critical_findings": [v for v in vulnerabilities if v["severity"] in {"CRITICAL", "HIGH"}],
            "cve_correlation": {
                "total_cve_matches": total_matches,
                "potential_match_indicator": total_matches > 0,
            },
        },
        "detailed_findings": {
            "vulnerabilities": vulnerabilities,
            "configuration_issues": [],
            "suspicious_activities": [],
        },
        "recommendations": [
            {
                "category": "CVE_CORRELATION",
                "severity": "HIGH" if total_matches > 0 else "LOW",
                "findings": len(vulnerabilities),
                "actions": [
                    "Review CVE matches against target version and build context.",
                    "Prioritize HIGH-confidence matches for patch and regression testing.",
                ],
            }
        ],
        "remediation_timeline": {
            "immediate": severity_counter.get("CRITICAL", 0) + severity_counter.get("HIGH", 0),
            "short_term": severity_counter.get("MEDIUM", 0),
            "long_term": severity_counter.get("LOW", 0),
            "suggested_timeline": {
                "immediate": "Within 24 hours",
                "short_term": "Within 1 week",
                "long_term": "Within 1 month",
            },
        },
    }

    return report
