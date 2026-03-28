from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenerateScanReportView, ScanReportViewSet

router = DefaultRouter()
router.register(r"reports", ScanReportViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("latest-report/", ScanReportViewSet.as_view({"get": "latest_report"}), name="latest-report"),
    path("scan/", GenerateScanReportView.as_view(), name="scan-report"),
]
