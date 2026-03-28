import json
import os
from django.conf import settings
from rest_framework import serializers
from .models import CrashArtifact, ScanJob, ScanReport

class ScanReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanReport
        fields = '__all__'


class ScanJobSerializer(serializers.ModelSerializer):
    report_id = serializers.IntegerField(source="report.id", read_only=True)
    crash_count = serializers.SerializerMethodField()

    def get_crash_count(self, obj):
        crash_count = CrashArtifact.objects.filter(job=obj).count()
        if crash_count:
            return crash_count

        if not obj.report:
            return None

        file_path = os.path.join(settings.MEDIA_ROOT, obj.report.report_path)
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            return data.get("scan_summary", {}).get("total_vulnerabilities")
        except (json.JSONDecodeError, OSError):
            return None

    class Meta:
        model = ScanJob
        fields = [
            "id",
            "status",
            "error",
            "timeout_seconds",
            "memory_limit_mb",
            "cpu_limit",
            "binary_artifact_id",
            "seed_artifact_id",
            "source_artifact_id",
            "report_id",
            "crash_count",
            "created_at",
            "started_at",
            "finished_at",
        ]
