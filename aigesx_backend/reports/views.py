from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, generics
from .models import ScanReport
from .serializers import ScanReportSerializer
import json
import os
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import FileUploadParser, MultiPartParser
from django.core.files.storage import default_storage
from django.conf import settings

User = get_user_model()

class UploadReportView(generics.CreateAPIView):
    queryset = ScanReport.objects.all()
    serializer_class = ScanReportSerializer
    parser_classes = [MultiPartParser, FileUploadParser]  # Accept file uploads

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "No such user exists"}, status=status.HTTP_404_NOT_FOUND)

        if "file" not in request.FILES:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES["file"]
        reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        file_path = os.path.join(reports_dir, file.name)

        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        report = ScanReport.objects.create(
            user=user,
            report_path=os.path.join("reports", file.name)
        )

        return Response(
            {"message": "File uploaded successfully", "report_id": report.id},
            status=status.HTTP_201_CREATED
        )

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