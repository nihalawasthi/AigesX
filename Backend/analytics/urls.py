from django.urls import path
from .views import get_vulnerability_trends, get_cyber_risk_index

urlpatterns = [
    path("vulnerability-trends/", get_vulnerability_trends, name="vulnerability-trends"),
    path("cyber-risk-index/", get_cyber_risk_index, name="cyber-risk-index"),
]
