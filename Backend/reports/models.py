from django.conf import settings
from django.db import models
import uuid

class ScanReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Updated line
    created_at = models.DateTimeField(auto_now_add=True)
    report_path = models.CharField(max_length=255)

    def __str__(self):
        return f"Report {self.id} - {self.user.username}"


class ScanJob(models.Model):
    STATUS_QUEUED = "QUEUED"
    STATUS_RUNNING = "RUNNING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"

    STATUS_CHOICES = [
        (STATUS_QUEUED, "Queued"),
        (STATUS_RUNNING, "Running"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_QUEUED)
    error = models.TextField(blank=True, null=True)
    stop_requested = models.BooleanField(default=False)
    timeout_seconds = models.PositiveIntegerField(default=300)
    memory_limit_mb = models.PositiveIntegerField(default=512)
    binary_artifact = models.ForeignKey("UploadedArtifact", on_delete=models.SET_NULL, blank=True, null=True, related_name="binary_jobs")
    seed_artifact = models.ForeignKey("UploadedArtifact", on_delete=models.SET_NULL, blank=True, null=True)
    source_artifact = models.ForeignKey("UploadedArtifact", on_delete=models.SET_NULL, blank=True, null=True, related_name="source_jobs")
    report = models.ForeignKey(ScanReport, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"ScanJob {self.id} - {self.status}"


class UploadedArtifact(models.Model):
    KIND_BINARY = "BINARY"
    KIND_CORPUS = "CORPUS"
    KIND_SOURCE = "SOURCE"

    KIND_CHOICES = [
        (KIND_BINARY, "Binary"),
        (KIND_CORPUS, "Corpus"),
        (KIND_SOURCE, "Source"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    kind = models.CharField(max_length=16, choices=KIND_CHOICES)
    file = models.FileField(upload_to="uploads/", blank=True, null=True)
    repo_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.kind} artifact {self.id} - {self.user.username}"
