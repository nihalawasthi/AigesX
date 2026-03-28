from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenerateScanReportView, ScanJobCrashDataView, ScanJobCrashDownloadView, ScanJobListView, ScanJobStatusView, ScanReportViewSet, StartScanJobView, StopScanJobView, UploadBinaryView, UploadCorpusView, UploadSourceRepoView, UploadedArtifactsView

router = DefaultRouter()
router.register(r"reports", ScanReportViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("latest-report/", ScanReportViewSet.as_view({"get": "latest_report"}), name="latest-report"),
    path("scan/", GenerateScanReportView.as_view(), name="scan-report"),
    path("scan/upload/binary/", UploadBinaryView.as_view(), name="scan-upload-binary"),
    path("scan/upload/corpus/", UploadCorpusView.as_view(), name="scan-upload-corpus"),
    path("scan/upload/source/", UploadSourceRepoView.as_view(), name="scan-upload-source"),
    path("scan/upload/artifacts/", UploadedArtifactsView.as_view(), name="scan-upload-artifacts"),
    path("scan/start/", StartScanJobView.as_view(), name="scan-start"),
    path("scan/jobs/", ScanJobListView.as_view(), name="scan-jobs"),
    path("scan/jobs/<uuid:job_id>/", ScanJobStatusView.as_view(), name="scan-job-status"),
    path("scan/jobs/<uuid:job_id>/stop/", StopScanJobView.as_view(), name="scan-job-stop"),
    path("scan/jobs/<uuid:job_id>/crashes/", ScanJobCrashDataView.as_view(), name="scan-job-crashes"),
    path("scan/jobs/<uuid:job_id>/crashes/download/", ScanJobCrashDownloadView.as_view(), name="scan-job-crashes-download"),
]
