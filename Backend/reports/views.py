from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from .models import ScanReport
from .serializers import ScanReportSerializer
from .scan_service import run_full_scan
import json
import os
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings


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