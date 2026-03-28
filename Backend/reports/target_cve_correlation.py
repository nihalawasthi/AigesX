from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
import base64
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


CRASH_KEYWORDS = [
    "segmentation fault",
    "sigsegv",
    "abort",
    "assert",
    "stack smashing",
    "heap-buffer-overflow",
    "addresssanitizer",
    "asan",
    "bus error",
    "illegal instruction",
    "floating point exception",
    "use-after-free",
]


def _infer_crash_type(text: str) -> str:
    lower = (text or "").lower()
    if "use-after-free" in lower:
        return "Use After Free"
    if "stack smashing" in lower or "buffer overflow" in lower or "heap-buffer-overflow" in lower:
        return "Buffer Overflow"
    if "integer overflow" in lower:
        return "Integer Overflow"
    if "segmentation fault" in lower or "sigsegv" in lower:
        return "Segmentation Fault"
    if "abort" in lower or "assert" in lower:
        return "Abort/Assertion Failure"
    return "Crash Anomaly"


def _infer_severity(text: str) -> str:
    lower = (text or "").lower()
    if any(keyword in lower for keyword in ["use-after-free", "heap-buffer-overflow", "stack smashing", "segmentation fault"]):
        return "HIGH"
    if any(keyword in lower for keyword in ["abort", "assert", "illegal instruction", "bus error"]):
        return "MEDIUM"
    return "LOW"


def _load_seed_inputs(seed_artifact, max_inputs: int = 16) -> list[bytes]:
    if not seed_artifact or not seed_artifact.file:
        return [b"A" * 32, b"%x%n" * 8, b"\x00" * 64]

    path = seed_artifact.file.path
    inputs: list[bytes] = []

    try:
        if zipfile.is_zipfile(path):
            with zipfile.ZipFile(path, "r") as archive:
                for name in archive.namelist():
                    if len(inputs) >= max_inputs:
                        break
                    if name.endswith("/"):
                        continue
                    try:
                        data = archive.read(name)
                    except KeyError:
                        continue
                    if data:
                        inputs.append(data[:8192])
        else:
            with open(path, "rb") as handle:
                data = handle.read(131072)
            if data:
                chunk_size = max(1, min(4096, len(data) // max(1, max_inputs // 2)))
                for start in range(0, len(data), chunk_size):
                    if len(inputs) >= max_inputs:
                        break
                    chunk = data[start : start + chunk_size]
                    if chunk:
                        inputs.append(chunk)
    except OSError:
        pass

    return inputs or [b"A" * 32, b"%x%n" * 8, b"\x00" * 64]


def _mutate_seed_inputs(seed_inputs: list[bytes], max_mutations: int = 64) -> list[bytes]:
    """Generate deterministic, low-cost mutations to increase crash surface."""
    if not seed_inputs:
        return []

    mutations: list[bytes] = []
    seen: set[bytes] = set()

    def add_candidate(candidate: bytes) -> None:
        if not candidate:
            return
        clipped = candidate[:8192]
        if clipped in seen:
            return
        seen.add(clipped)
        mutations.append(clipped)

    interesting_tokens = [
        b"%x%x%x%x",
        b"%n%n%n%n",
        b"../../../../etc/passwd",
        b"A" * 1024,
        b"\x00" * 1024,
        b"\xff" * 1024,
    ]

    for base in seed_inputs:
        if len(mutations) >= max_mutations:
            break

        add_candidate(base)
        add_candidate(base + b"\n")
        add_candidate(base + b"\x00")
        add_candidate(base * 2)
        add_candidate(base[: max(1, len(base) // 2)])
        add_candidate(base[::-1])

        if base:
            flip_idx = len(base) // 2
            flipped = bytearray(base)
            flipped[flip_idx] ^= 0xFF
            add_candidate(bytes(flipped))

        for token in interesting_tokens:
            add_candidate(base + token)
            add_candidate(token + base)

        # Single-byte substitution sweep over up to first 16 bytes.
        for idx in range(min(16, len(base))):
            for value in (0x00, 0x7F, 0x80, 0xFF):
                mutated = bytearray(base)
                mutated[idx] = value
                add_candidate(bytes(mutated))
                if len(mutations) >= max_mutations:
                    break
            if len(mutations) >= max_mutations:
                break

    return mutations[:max_mutations]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _run_binary_local(binary_path: str, payload: bytes, timeout_seconds: int) -> dict[str, Any]:
    def _exec(cmd: list[str], *, input_bytes: bytes | None = None):
        return subprocess.run(
            cmd,
            input=input_bytes,
            capture_output=True,
            timeout=max(1, timeout_seconds),
        )

    # Mode 1: stdin-driven executables.
    completed = _exec([binary_path], input_bytes=payload)
    stderr_text = completed.stderr.decode("utf-8", errors="ignore")
    stdout_text = completed.stdout.decode("utf-8", errors="ignore")
    combined = f"{stderr_text}\n{stdout_text}".strip()
    crash_detected = completed.returncode != 0 or any(keyword in combined.lower() for keyword in CRASH_KEYWORDS)
    if crash_detected:
        return {
            "crash_detected": True,
            "returncode": completed.returncode,
            "stderr": stderr_text,
            "stdout": stdout_text,
            "combined": combined,
            "run_mode": "stdin",
        }

    # Mode 2: executables expecting a file path argument.
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(payload)
        tf.flush()
        temp_path = tf.name
    try:
        completed_file = _exec([binary_path, temp_path])
        stderr_text_f = completed_file.stderr.decode("utf-8", errors="ignore")
        stdout_text_f = completed_file.stdout.decode("utf-8", errors="ignore")
        combined_f = f"{stderr_text_f}\n{stdout_text_f}".strip()
        crash_detected_f = completed_file.returncode != 0 or any(keyword in combined_f.lower() for keyword in CRASH_KEYWORDS)
        return {
            "crash_detected": crash_detected_f,
            "returncode": completed_file.returncode,
            "stderr": stderr_text_f,
            "stdout": stdout_text_f,
            "combined": combined_f,
            "run_mode": "file_arg",
        }
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


def _run_binary_docker(binary_path: str, payload: bytes, timeout_seconds: int, memory_limit_mb: int, cpu_limit: float) -> dict[str, Any]:
    image = os.getenv("AIGESX_DOCKER_IMAGE", "ubuntu:24.04")
    binary_abs = os.path.abspath(binary_path)
    binary_dir = os.path.dirname(binary_abs)
    binary_name = os.path.basename(binary_abs)

    with tempfile.NamedTemporaryFile(delete=False) as input_file:
        input_file.write(payload)
        input_file.flush()
        input_path = input_file.name

    try:
        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--cpus",
            str(max(0.1, cpu_limit)),
            "--memory",
            f"{max(64, memory_limit_mb)}m",
            "--pids-limit",
            "256",
            "-v",
            f"{binary_dir}:/target:ro",
            "-v",
            f"{os.path.dirname(input_path)}:/inputs:ro",
            image,
            "bash",
            "-lc",
            f"cat /inputs/{os.path.basename(input_path)} | timeout {max(1, timeout_seconds)} /target/{binary_name}",
        ]

        completed = subprocess.run(docker_cmd, capture_output=True, timeout=max(2, timeout_seconds + 5))
        stderr_text = completed.stderr.decode("utf-8", errors="ignore")
        stdout_text = completed.stdout.decode("utf-8", errors="ignore")
        combined = f"{stderr_text}\n{stdout_text}".strip()
        crash_detected = completed.returncode != 0 or any(keyword in combined.lower() for keyword in CRASH_KEYWORDS)
        return {
            "crash_detected": crash_detected,
            "returncode": completed.returncode,
            "stderr": stderr_text,
            "stdout": stdout_text,
            "combined": combined,
            "execution_mode": "docker",
        }
    finally:
        try:
            os.remove(input_path)
        except OSError:
            pass


def _run_binary_with_input(binary_path: str, payload: bytes, timeout_seconds: int, memory_limit_mb: int, cpu_limit: float) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile(delete=False) as input_file:
        input_file.write(payload)
        input_file.flush()
        input_path = input_file.name

    try:
        use_docker = os.getenv("AIGESX_EXECUTOR", "local").lower() == "docker" and shutil.which("docker")
        if use_docker:
            result = _run_binary_docker(
                binary_path=binary_path,
                payload=payload,
                timeout_seconds=timeout_seconds,
                memory_limit_mb=memory_limit_mb,
                cpu_limit=cpu_limit,
            )
        else:
            result = _run_binary_local(binary_path=binary_path, payload=payload, timeout_seconds=timeout_seconds)
            result["execution_mode"] = "local"
        result["input_path"] = input_path
        return result
    except subprocess.TimeoutExpired as exc:
        stderr_text = (exc.stderr or b"").decode("utf-8", errors="ignore") if isinstance(exc.stderr, (bytes, bytearray)) else str(exc.stderr or "")
        stdout_text = (exc.stdout or b"").decode("utf-8", errors="ignore") if isinstance(exc.stdout, (bytes, bytearray)) else str(exc.stdout or "")
        combined = f"{stderr_text}\n{stdout_text}\nExecution timed out".strip()
        return {
            "crash_detected": True,
            "returncode": -1,
            "stderr": stderr_text,
            "stdout": stdout_text,
            "combined": combined,
            "input_path": input_path,
            "timeout": True,
            "execution_mode": "local",
        }
    except Exception as exc:  # pragma: no cover - environment-specific execution errors
        combined = str(exc)
        return {
            "crash_detected": True,
            "returncode": -2,
            "stderr": combined,
            "stdout": "",
            "combined": combined,
            "input_path": input_path,
            "execution_error": True,
            "execution_mode": "local",
        }
    finally:
        try:
            os.remove(input_path)
        except OSError:
            pass


def _run_aflpp_campaign(binary_path: str, seed_inputs: list[bytes], timeout_seconds: int) -> list[dict[str, Any]]:
    if shutil.which("afl-fuzz") is None:
        return []

    afl_crashes: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as seed_dir, tempfile.TemporaryDirectory() as out_dir:
        for idx, payload in enumerate(seed_inputs, start=1):
            with open(os.path.join(seed_dir, f"seed_{idx}.bin"), "wb") as f:
                f.write(payload)

        cmd = [
            "afl-fuzz",
            "-i",
            seed_dir,
            "-o",
            out_dir,
            "-V",
            str(max(5, timeout_seconds * 2)),
            "--",
            binary_path,
        ]

        try:
            subprocess.run(cmd, capture_output=True, timeout=max(8, timeout_seconds * 3))
        except Exception:
            return []

        crashes_dir = os.path.join(out_dir, "default", "crashes")
        if not os.path.isdir(crashes_dir):
            return []

        for name in os.listdir(crashes_dir):
            if name.lower().startswith("readme"):
                continue
            crash_path = os.path.join(crashes_dir, name)
            if not os.path.isfile(crash_path):
                continue
            try:
                payload = open(crash_path, "rb").read()
            except OSError:
                continue
            afl_crashes.append(
                {
                    "artifact_id": f"afl-{name}",
                    "payload": payload,
                    "summary": f"AFL++ crash file: {name}",
                    "stderr": "",
                    "stdout": "",
                    "returncode": -3,
                    "source": "AFL++",
                    "execution_mode": "aflpp",
                }
            )

    return afl_crashes


def _extract_crash_artifacts(binary_artifact, seed_artifact, timeout_seconds: int, memory_limit_mb: int, cpu_limit: float) -> list[dict[str, Any]]:
    if not binary_artifact or not binary_artifact.file:
        return []

    binary_path = binary_artifact.file.path
    if not os.path.exists(binary_path):
        return []

    seed_inputs = _load_seed_inputs(seed_artifact=seed_artifact)
    candidate_inputs = _mutate_seed_inputs(seed_inputs, max_mutations=64) or seed_inputs
    crash_artifacts: list[dict[str, Any]] = []
    seen_hashes: set[str] = set()
    max_crashes = max(5, int(os.getenv("AIGESX_MAX_CRASHES", "30")))

    # AFL++ primary engine integration (if available), then direct execution fallback.
    for afl_crash in _run_aflpp_campaign(binary_path=binary_path, seed_inputs=seed_inputs, timeout_seconds=timeout_seconds):
        payload = afl_crash["payload"]
        crash_hash = _sha256_bytes(payload + afl_crash["summary"].encode("utf-8", errors="ignore"))
        if crash_hash in seen_hashes:
            continue
        seen_hashes.add(crash_hash)
        crash_group_hash = _sha256_bytes((afl_crash["summary"] + "::AFL++").encode("utf-8", errors="ignore"))
        crash_artifacts.append(
            {
                "artifact_id": afl_crash["artifact_id"],
                "returncode": afl_crash.get("returncode"),
                "crash_type": _infer_crash_type(afl_crash["summary"]),
                "severity": "HIGH",
                "stderr": afl_crash.get("stderr") or "",
                "stdout": afl_crash.get("stdout") or "",
                "summary": afl_crash["summary"][:1500],
                "input_size": len(payload),
                "input_b64": base64.b64encode(payload).decode("ascii"),
                "crash_hash": crash_hash,
                "crash_group_hash": crash_group_hash,
                "source": "AFL++",
                "execution_mode": afl_crash.get("execution_mode", "aflpp"),
            }
        )

    for idx, payload in enumerate(candidate_inputs, start=1):
        if len(crash_artifacts) >= max_crashes:
            break
        result = _run_binary_with_input(
            binary_path=binary_path,
            payload=payload,
            timeout_seconds=timeout_seconds,
            memory_limit_mb=memory_limit_mb,
            cpu_limit=cpu_limit,
        )
        if not result["crash_detected"]:
            continue

        combined = result["combined"] or "Crash detected with non-zero return code"
        crash_hash = _sha256_bytes(payload + combined.encode("utf-8", errors="ignore"))
        if crash_hash in seen_hashes:
            continue
        seen_hashes.add(crash_hash)
        crash_group_hash = _sha256_bytes((_infer_crash_type(combined) + "::" + combined[:120]).encode("utf-8", errors="ignore"))
        crash_artifacts.append(
            {
                "artifact_id": f"crash-{idx}",
                "returncode": result.get("returncode"),
                "crash_type": _infer_crash_type(combined),
                "severity": _infer_severity(combined),
                "stderr": result.get("stderr") or "",
                "stdout": result.get("stdout") or "",
                "summary": combined[:1500],
                "input_size": len(payload),
                "input_b64": base64.b64encode(payload).decode("ascii"),
                "crash_hash": crash_hash,
                "crash_group_hash": crash_group_hash,
                "source": "DIRECT_EXECUTION",
                "execution_mode": result.get("execution_mode", "local"),
                "run_mode": result.get("run_mode", "stdin"),
            }
        )

    return crash_artifacts


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


def _build_vuln_from_crash(crash: dict[str, Any], now_iso: str, binary_path: str | None) -> dict[str, Any]:
    return {
        "severity": crash["severity"],
        "type": crash["crash_type"],
        "description": f"Crash artifact {crash['artifact_id']} detected during target execution.",
        "timestamp": now_iso,
        "component": os.path.basename(binary_path) if binary_path else "unknown_binary",
        "affected_service": None,
        "details": {
            "artifact_id": crash["artifact_id"],
            "returncode": crash["returncode"],
            "input_size": crash["input_size"],
            "crash_hash": crash.get("crash_hash"),
            "crash_group_hash": crash.get("crash_group_hash"),
            "source": crash.get("source"),
            "execution_mode": crash.get("execution_mode"),
            "input_b64": crash.get("input_b64"),
            "stderr_excerpt": crash["stderr"][:800],
            "stdout_excerpt": crash["stdout"][:300],
        },
        "recommendation": "Reproduce with minimized crashing input and inspect memory/error traces.",
        "cve_id": None,
        "potential_match_indicator": False,
    }


def correlate_target_with_cves(
    *,
    binary_artifact=None,
    source_artifact=None,
    seed_artifact=None,
    timeout_seconds: int = 5,
    memory_limit_mb: int = 512,
    cpu_limit: float = 1.0,
) -> dict[str, Any]:
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    patterns = _load_cve_patterns()

    binary_path = None
    if binary_artifact and binary_artifact.file:
        binary_path = binary_artifact.file.path
    source_url = None
    if source_artifact and source_artifact.repo_url:
        source_url = source_artifact.repo_url
    crash_artifacts = _extract_crash_artifacts(
        binary_artifact=binary_artifact,
        seed_artifact=seed_artifact,
        timeout_seconds=timeout_seconds,
        memory_limit_mb=memory_limit_mb,
        cpu_limit=cpu_limit,
    )

    vulnerabilities: list[dict[str, Any]] = []
    for crash in crash_artifacts:
        crash_tokens = _tokenize(" ".join([crash.get("summary", ""), crash.get("crash_type", ""), crash.get("stderr", "")]))
        best_match: dict[str, Any] | None = None
        for pattern in patterns:
            pattern_tokens = _extract_pattern_tokens(pattern)
            score = _score_pattern(crash_tokens, pattern_tokens)
            if score <= 0:
                continue
            if not best_match or score > best_match["score"]:
                best_match = {"pattern": pattern, "score": score}

        vuln = _build_vuln_from_crash(crash=crash, now_iso=now_iso, binary_path=binary_path)
        if best_match and best_match["score"] >= 0.03:
            pattern = best_match["pattern"]
            score = best_match["score"]
            vuln["cve_id"] = pattern.get("id")
            vuln["potential_match_indicator"] = True
            vuln["details"]["match_score"] = round(score, 4)
            vuln["details"]["match_reason"] = "Crash artifact tokens overlap with CVE description/products"
            vuln["details"]["affected_products"] = pattern.get("affected_products", [])[:5]
            vuln["description"] = pattern.get("description") or vuln["description"]
            vuln["severity"] = _score_to_severity(score)

        vulnerabilities.append(vuln)

    if not vulnerabilities:
        message = "No crash artifacts were produced from the selected target inputs."
        if source_url and not binary_path:
            message = "Source target selected without executable binary; crash execution was skipped."

        vulnerabilities.append(
            {
                "severity": "LOW",
                "type": "CVE_CORRELATION",
                "description": message,
                "timestamp": now_iso,
                "component": os.path.basename(binary_path) if binary_path else (source_url or "unknown_target"),
                "affected_service": None,
                "details": {
                    "match_score": 0.0,
                    "match_reason": "No crash artifact evidence available for CVE mapping",
                    "crash_artifacts_parsed": 0,
                },
                "recommendation": "Upload a runnable binary and seed corpus to generate crash artifacts for CVE mapping.",
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
                "crash_artifacts_parsed": len(crash_artifacts),
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
