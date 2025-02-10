from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScanReportViewSet, UploadReportView

router = DefaultRouter()
router.register(r"reports", ScanReportViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("latest-report/", ScanReportViewSet.as_view({"get": "latest_report"}), name="latest-report"),
    path("upload-report/", UploadReportView.as_view(), name="upload-report"),
]
