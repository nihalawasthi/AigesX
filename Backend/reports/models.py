from django.conf import settings
from django.db import models

class ScanReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Updated line
    created_at = models.DateTimeField(auto_now_add=True)
    report_path = models.CharField(max_length=255)

    def __str__(self):
        return f"Report {self.id} - {self.user.username}"
