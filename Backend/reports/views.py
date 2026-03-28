import logging
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from .models import ScanJob, ScanReport, UploadedArtifact
from .serializers import ScanJobSerializer, ScanReportSerializer
from .scan_service import run_full_scan
import json
import os
import threading
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.db import close_old_connections
from django.utils import timezone


logger = logging.getLogger(__name__)


def _execute_scan_job(job_id):
    close_old_connections()
    old_cwd = os.getcwd()
    reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    try:
        job = ScanJob.objects.select_related("user", "binary_artifact", "source_artifact").get(id=job_id)
        if job.stop_requested:
            job.status = ScanJob.STATUS_FAILED
            job.error = "Cancelled by user before execution started."
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "error", "finished_at"])
            return

        job.status = ScanJob.STATUS_RUNNING
        job.started_at = timezone.now()
        job.error = None
        job.save(update_fields=["status", "started_at", "error"])

        os.chdir(reports_dir)
        binary_artifact = job.binary_artifact
        if not binary_artifact:
            binary_artifact = (
                UploadedArtifact.objects.filter(
                    user=job.user,
                    kind=UploadedArtifact.KIND_BINARY,
                )
                .order_by("-created_at")
                .first()
            )

        report_data, report_file_name = run_full_scan(
            binary_artifact=binary_artifact,
            source_artifact=job.source_artifact,
        )

        job.refresh_from_db(fields=["stop_requested"])
        if job.stop_requested:
            job.status = ScanJob.STATUS_FAILED
            job.error = "Cancelled by user during execution."
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "error", "finished_at"])
            return

        report = ScanReport.objects.create(
            user=job.user,
            report_path=os.path.join("reports", report_file_name),
        )

        job.status = ScanJob.STATUS_COMPLETED
        job.report = report
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "report", "finished_at"])
    except Exception as exc:
        logger.exception("Scan job execution failed for job_id=%s", job_id)
        ScanJob.objects.filter(id=job_id).update(
            status=ScanJob.STATUS_FAILED,
            error=str(exc),
            finished_at=timezone.now(),
        )
    finally:
        os.chdir(old_cwd)
        close_old_connections()


class GenerateScanReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        old_cwd = os.getcwd()
        try:
            # Reporter writes output in the current working directory.
            os.chdir(reports_dir)
            latest_binary = (
                UploadedArtifact.objects.filter(
                    user=request.user,
                    kind=UploadedArtifact.KIND_BINARY,
                )
                .order_by("-created_at")
                .first()
            )

            latest_source = (
                UploadedArtifact.objects.filter(
                    user=request.user,
                    kind=UploadedArtifact.KIND_SOURCE,
                )
                .order_by("-created_at")
                .first()
            )

            report_data, report_file_name = run_full_scan(
                binary_artifact=latest_binary,
                source_artifact=latest_source,
            )

            report = ScanReport.objects.create(
                user=request.user,
                report_path=os.path.join("reports", report_file_name),
            )

            return Response(
                {
                    "message": "Scan completed successfully",
                    "report_id": report.id,
                    "report_data": report_data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as exc:
            logger.exception("Synchronous scan failed for user_id=%s", request.user.id)
            return Response(
                {"error": "Scan failed", "details": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            os.chdir(old_cwd)

class ScanReportViewSet(viewsets.ModelViewSet):
    queryset = ScanReport.objects.all()
    serializer_class = ScanReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-created_at")

    def latest_report(self, request):
        """Fetch and return the latest JSON report as JSON data"""
        latest_report = self.get_queryset().first()
        if not latest_report:
            return JsonResponse({"error": "No reports found"}, status=404)

        # Convert relative path to absolute path
        file_path = os.path.join(settings.MEDIA_ROOT, latest_report.report_path)

        if not os.path.exists(file_path):
            return JsonResponse({"error": "Report file not found"}, status=404)

        # Read JSON file and return as JSON response
        try:
            with open(file_path, "r") as f:
                report_data = json.load(f)
            return JsonResponse(report_data, status=200, safe=False)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=500)


class StartScanJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        timeout_seconds = int(request.data.get("timeout_seconds", 300))
        memory_limit_mb = int(request.data.get("memory_limit_mb", 512))
        binary_artifact_id = request.data.get("binary_artifact_id")
        seed_artifact_id = request.data.get("seed_artifact_id")
        source_artifact_id = request.data.get("source_artifact_id")

        binary_artifact = None
        if binary_artifact_id:
            try:
                binary_artifact = UploadedArtifact.objects.get(
                    id=binary_artifact_id,
                    user=request.user,
                    kind=UploadedArtifact.KIND_BINARY,
                )
            except UploadedArtifact.DoesNotExist:
                return Response({"error": "Invalid binary artifact"}, status=status.HTTP_400_BAD_REQUEST)

        seed_artifact = None
        if seed_artifact_id:
            try:
                seed_artifact = UploadedArtifact.objects.get(
                    id=seed_artifact_id,
                    user=request.user,
                    kind=UploadedArtifact.KIND_CORPUS,
                )
            except UploadedArtifact.DoesNotExist:
                return Response({"error": "Invalid seed artifact"}, status=status.HTTP_400_BAD_REQUEST)

        source_artifact = None
        if source_artifact_id:
            try:
                source_artifact = UploadedArtifact.objects.get(
                    id=source_artifact_id,
                    user=request.user,
                    kind=UploadedArtifact.KIND_SOURCE,
                )
            except UploadedArtifact.DoesNotExist:
                return Response({"error": "Invalid source artifact"}, status=status.HTTP_400_BAD_REQUEST)

        job = ScanJob.objects.create(
            user=request.user,
            status=ScanJob.STATUS_QUEUED,
            timeout_seconds=max(1, timeout_seconds),
            memory_limit_mb=max(64, memory_limit_mb),
            binary_artifact=binary_artifact,
            seed_artifact=seed_artifact,
            source_artifact=source_artifact,
        )

        thread = threading.Thread(target=_execute_scan_job, args=(job.id,), daemon=True)
        thread.start()

        return Response(
            {
                "message": "Scan job queued",
                "job": ScanJobSerializer(job).data,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class ScanJobStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id, *args, **kwargs):
        try:
            job = ScanJob.objects.get(id=job_id, user=request.user)
        except ScanJob.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        payload = ScanJobSerializer(job).data

        if job.status == ScanJob.STATUS_COMPLETED and job.report_id:
            file_path = os.path.join(settings.MEDIA_ROOT, job.report.report_path)
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        payload["report_data"] = json.load(f)
                except json.JSONDecodeError:
                    logger.warning("Invalid report JSON for job_id=%s", job.id)
                    payload["report_data"] = None

        return Response(payload, status=status.HTTP_200_OK)


class ScanJobListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        jobs = (
            ScanJob.objects.filter(user=request.user)
            .select_related("report")
            .order_by("-created_at")[:50]
        )
        return Response(ScanJobSerializer(jobs, many=True).data, status=status.HTTP_200_OK)


class StopScanJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id, *args, **kwargs):
        try:
            job = ScanJob.objects.get(id=job_id, user=request.user)
        except ScanJob.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        if job.status in [ScanJob.STATUS_COMPLETED, ScanJob.STATUS_FAILED]:
            return Response(
                {"error": "Job cannot be stopped in its current state"},
                status=status.HTTP_409_CONFLICT,
            )

        if job.status == ScanJob.STATUS_QUEUED:
            job.status = ScanJob.STATUS_FAILED
            job.error = "Cancelled by user before execution started."
            job.stop_requested = True
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "error", "stop_requested", "finished_at"])
            return Response(
                {"message": "Queued job cancelled", "job": ScanJobSerializer(job).data},
                status=status.HTTP_200_OK,
            )

        job.stop_requested = True
        job.error = "Stop requested by user."
        job.save(update_fields=["stop_requested", "error"])
        return Response(
            {
                "message": "Stop requested; running job will be marked failed when execution returns",
                "job": ScanJobSerializer(job).data,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class ScanJobCrashDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id, *args, **kwargs):
        try:
            job = ScanJob.objects.select_related("report").get(id=job_id, user=request.user)
        except ScanJob.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        if not job.report_id:
            return Response({"crashes": []}, status=status.HTTP_200_OK)

        file_path = os.path.join(settings.MEDIA_ROOT, job.report.report_path)
        if not os.path.exists(file_path):
            return Response({"error": "Report file not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            with open(file_path, "r") as f:
                report_data = json.load(f)
        except json.JSONDecodeError:
            logger.exception("Invalid report JSON when fetching crashes for job_id=%s", job.id)
            return Response({"error": "Invalid report format"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        crashes = report_data.get("detailed_findings", {}).get("vulnerabilities", [])
        return Response({"job_id": str(job.id), "crashes": crashes}, status=status.HTTP_200_OK)


class ScanJobCrashDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id, *args, **kwargs):
        try:
            job = ScanJob.objects.select_related("report").get(id=job_id, user=request.user)
        except ScanJob.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        if not job.report_id:
            return Response({"error": "No report available for this job"}, status=status.HTTP_404_NOT_FOUND)

        file_path = os.path.join(settings.MEDIA_ROOT, job.report.report_path)
        if not os.path.exists(file_path):
            return Response({"error": "Report file not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            with open(file_path, "r") as f:
                report_data = json.load(f)
        except json.JSONDecodeError:
            logger.exception("Invalid report JSON when downloading crashes for job_id=%s", job.id)
            return Response({"error": "Invalid report format"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        crashes = report_data.get("detailed_findings", {}).get("vulnerabilities", [])
        payload = json.dumps({"job_id": str(job.id), "crashes": crashes}, indent=2)

        response = HttpResponse(payload, content_type="application/json")
        response["Content-Disposition"] = f'attachment; filename="job_{job.id}_crashes.json"'
        return response


class UploadBinaryView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"error": "Missing file"}, status=status.HTTP_400_BAD_REQUEST)

        header = uploaded_file.read(4)
        uploaded_file.seek(0)
        if header != b"\x7fELF":
            return Response({"error": "Only ELF binaries are supported"}, status=status.HTTP_400_BAD_REQUEST)

        artifact = UploadedArtifact.objects.create(
            user=request.user,
            kind=UploadedArtifact.KIND_BINARY,
            file=uploaded_file,
        )

        return Response(
            {
                "id": artifact.id,
                "kind": artifact.kind,
                "file_name": os.path.basename(artifact.file.name),
                "file_path": artifact.file.name,
                "size": artifact.file.size,
            },
            status=status.HTTP_201_CREATED,
        )


class UploadCorpusView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"error": "Missing file"}, status=status.HTTP_400_BAD_REQUEST)

        artifact = UploadedArtifact.objects.create(
            user=request.user,
            kind=UploadedArtifact.KIND_CORPUS,
            file=uploaded_file,
        )

        return Response(
            {
                "id": artifact.id,
                "kind": artifact.kind,
                "file_name": os.path.basename(artifact.file.name),
                "file_path": artifact.file.name,
                "size": artifact.file.size,
            },
            status=status.HTTP_201_CREATED,
        )


class UploadedArtifactsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        kind = request.query_params.get("kind")
        artifacts = UploadedArtifact.objects.filter(user=request.user)
        if kind in [UploadedArtifact.KIND_BINARY, UploadedArtifact.KIND_CORPUS, UploadedArtifact.KIND_SOURCE]:
            artifacts = artifacts.filter(kind=kind)

        payload = [
            {
                "id": artifact.id,
                "kind": artifact.kind,
                "file_name": os.path.basename(artifact.file.name) if artifact.file else None,
                "file_path": artifact.file.name if artifact.file else None,
                "size": artifact.file.size if artifact.file else None,
                "repo_url": artifact.repo_url,
                "created_at": artifact.created_at,
            }
            for artifact in artifacts[:100]
        ]
        return Response(payload, status=status.HTTP_200_OK)


class UploadSourceRepoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        repo_url = (request.data.get("repo_url") or "").strip()
        if not repo_url:
            return Response({"error": "Missing repo_url"}, status=status.HTTP_400_BAD_REQUEST)

        if not repo_url.startswith("https://github.com/"):
            return Response({"error": "Only public GitHub repository links are supported"}, status=status.HTTP_400_BAD_REQUEST)

        artifact = UploadedArtifact.objects.create(
            user=request.user,
            kind=UploadedArtifact.KIND_SOURCE,
            repo_url=repo_url,
        )

        return Response(
            {
                "id": artifact.id,
                "kind": artifact.kind,
                "repo_url": artifact.repo_url,
            },
            status=status.HTTP_201_CREATED,
        )