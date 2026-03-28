from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from .models import ScanJob, ScanReport
from .serializers import ScanJobSerializer, ScanReportSerializer
from .scan_service import run_full_scan
import json
import os
import threading
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.db import close_old_connections
from django.utils import timezone


def _execute_scan_job(job_id):
    close_old_connections()
    old_cwd = os.getcwd()
    reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    try:
        job = ScanJob.objects.select_related("user").get(id=job_id)
        job.status = ScanJob.STATUS_RUNNING
        job.started_at = timezone.now()
        job.error = None
        job.save(update_fields=["status", "started_at", "error"])

        os.chdir(reports_dir)
        report_data, report_file_name = run_full_scan()

        report = ScanReport.objects.create(
            user=job.user,
            report_path=os.path.join("reports", report_file_name),
        )

        job.status = ScanJob.STATUS_COMPLETED
        job.report = report
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "report", "finished_at"])
    except Exception as exc:
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
            report_data, report_file_name = run_full_scan()

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
        job = ScanJob.objects.create(user=request.user, status=ScanJob.STATUS_PENDING)

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
                    payload["report_data"] = None

        return Response(payload, status=status.HTTP_200_OK)