from rest_framework import serializers
from .models import ScanJob, ScanReport

class ScanReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanReport
        fields = '__all__'


class ScanJobSerializer(serializers.ModelSerializer):
    report_id = serializers.IntegerField(source="report.id", read_only=True)

    class Meta:
        model = ScanJob
        fields = [
            "id",
            "status",
            "error",
            "report_id",
            "created_at",
            "started_at",
            "finished_at",
        ]
