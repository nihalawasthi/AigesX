from __future__ import annotations

import base64
import logging
import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import close_old_connections
from django.utils import timezone

from .models import CrashArtifact, JobExecutionLog, ScanJob, ScanReport, UploadedArtifact
from .scan_service import run_full_scan

logger = logging.getLogger(__name__)


def log_job_event(job: ScanJob, level: str, message: str, context: dict | None = None) -> None:
    safe_level = level if level in {JobExecutionLog.LEVEL_INFO, JobExecutionLog.LEVEL_WARNING, JobExecutionLog.LEVEL_ERROR} else JobExecutionLog.LEVEL_INFO
    JobExecutionLog.objects.create(
        job=job,
        user=job.user,
        level=safe_level,
        message=message,
        context=context or {},
    )


def persist_crash_artifacts(job: ScanJob, report_data: dict) -> int:
    vulnerabilities = report_data.get("detailed_findings", {}).get("vulnerabilities", [])
    persisted = 0
    for idx, vuln in enumerate(vulnerabilities, start=1):
        details = vuln.get("details") or {}
        input_b64 = details.get("input_b64")
        crash_hash = details.get("crash_hash")
        if not input_b64 or not crash_hash:
            continue

        crash_group_hash = details.get("crash_group_hash") or crash_hash
        payload = None
        try:
            payload = base64.b64decode(input_b64)
        except Exception:
            payload = None
        if not payload:
            continue

        crash_obj, created = CrashArtifact.objects.get_or_create(
            job=job,
            crash_hash=crash_hash,
            defaults={
                "user": job.user,
                "crash_group_hash": crash_group_hash,
                "crash_type": vuln.get("type") or "Crash",
                "severity": vuln.get("severity") or "LOW",
                "cve_id": vuln.get("cve_id"),
                "potential_match_indicator": bool(vuln.get("potential_match_indicator")),
                "metadata": {
                    "artifact_id": details.get("artifact_id"),
                    "returncode": details.get("returncode"),
                    "input_size": details.get("input_size"),
                    "stderr_excerpt": details.get("stderr_excerpt"),
                    "stdout_excerpt": details.get("stdout_excerpt"),
                    "match_score": details.get("match_score"),
                    "match_reason": details.get("match_reason"),
                    "source": details.get("source"),
                    "execution_mode": details.get("execution_mode"),
                },
                "crash_input": ContentFile(payload, name=f"job_{job.id}_crash_{idx}.bin"),
            },
        )
        if created:
            persisted += 1

    return persisted


def execute_scan_job(job_id):
    close_old_connections()
    old_cwd = os.getcwd()
    reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    try:
        job = ScanJob.objects.select_related("user", "binary_artifact", "source_artifact", "seed_artifact").get(id=job_id)
        log_job_event(job, JobExecutionLog.LEVEL_INFO, "Worker picked job", {"job_id": str(job.id)})

        if job.stop_requested:
            job.status = ScanJob.STATUS_FAILED
            job.error = "Cancelled by user before execution started."
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "error", "finished_at"])
            log_job_event(job, JobExecutionLog.LEVEL_WARNING, "Job cancelled before execution")
            return

        job.status = ScanJob.STATUS_RUNNING
        job.started_at = timezone.now()
        job.error = None
        job.save(update_fields=["status", "started_at", "error"])
        log_job_event(job, JobExecutionLog.LEVEL_INFO, "Job started", {"timeout_seconds": job.timeout_seconds, "memory_limit_mb": job.memory_limit_mb, "cpu_limit": job.cpu_limit})

        os.chdir(reports_dir)
        binary_artifact = job.binary_artifact
        if not binary_artifact:
            binary_artifact = (
                UploadedArtifact.objects.filter(user=job.user, kind=UploadedArtifact.KIND_BINARY)
                .order_by("-created_at")
                .first()
            )

        report_data, report_file_name = run_full_scan(
            binary_artifact=binary_artifact,
            source_artifact=job.source_artifact,
            seed_artifact=job.seed_artifact,
            timeout_seconds=min(900, max(10, int(job.timeout_seconds or 120))),
            memory_limit_mb=max(64, int(job.memory_limit_mb or 512)),
            cpu_limit=max(0.1, float(job.cpu_limit or 1.0)),
        )

        job.refresh_from_db(fields=["stop_requested"])
        if job.stop_requested:
            job.status = ScanJob.STATUS_FAILED
            job.error = "Cancelled by user during execution."
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "error", "finished_at"])
            log_job_event(job, JobExecutionLog.LEVEL_WARNING, "Job cancelled during execution")
            return

        report = ScanReport.objects.create(
            user=job.user,
            report_path=os.path.join("reports", report_file_name),
        )

        persisted = persist_crash_artifacts(job=job, report_data=report_data)
        log_job_event(job, JobExecutionLog.LEVEL_INFO, "Crash artifacts persisted", {"count": persisted})

        job.status = ScanJob.STATUS_COMPLETED
        job.report = report
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "report", "finished_at"])
        log_job_event(job, JobExecutionLog.LEVEL_INFO, "Job completed", {"report_id": report.id})
    except Exception as exc:  # pragma: no cover
        logger.exception("Scan job execution failed for job_id=%s", job_id)
        ScanJob.objects.filter(id=job_id).update(
            status=ScanJob.STATUS_FAILED,
            error=str(exc),
            finished_at=timezone.now(),
        )
        try:
            failed_job = ScanJob.objects.select_related("user").get(id=job_id)
            log_job_event(failed_job, JobExecutionLog.LEVEL_ERROR, "Job failed", {"error": str(exc)})
        except Exception:
            pass
    finally:
        os.chdir(old_cwd)
        close_old_connections()
