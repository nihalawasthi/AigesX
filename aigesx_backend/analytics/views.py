import requests
from rest_framework.decorators import api_view
import random
from django.http import JsonResponse
from datetime import datetime, timedelta
from collections import Counter

VULNERABILITY_TRENDS_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

@api_view(['GET'])
def get_vulnerability_trends(request):
    """Fetch latest global vulnerability trends from NVD API v2.0"""
    try:
        response = requests.get(VULNERABILITY_TRENDS_URL, timeout=10)
        
        if response.status_code != 200:
            return JsonResponse({"error": "Failed to fetch data from NVD"}, status=response.status_code)
        
        data = response.json()
        
        if "vulnerabilities" not in data:
            return JsonResponse({"error": "Invalid data format received"}, status=500)
        
        vulnerabilities = data["vulnerabilities"]
        
        # Extract CWE (Common Weakness Enumeration) categories
        cwe_counter = Counter()

        for vuln in vulnerabilities:
            weaknesses = vuln["cve"].get("weaknesses", [])
            for weakness in weaknesses:
                cwe_ids = [cwe["value"] for cwe in weakness.get("description", [])]
                cwe_counter.update(cwe_ids)

        # Get the top 10 most common vulnerability categories
        top_cwes = cwe_counter.most_common(10)
        
        trends = {
            "labels": [f"CWE-{cwe_id}" for cwe_id, _ in top_cwes],
            "values": [count for _, count in top_cwes]
        }

        return JsonResponse(trends)

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

    

@api_view(['GET'])
def get_cyber_risk_index(request):
    """Generate mock Cyber Risk Index data"""
    try:
        today = datetime.today()
        dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(10)]

        risk_index = {
            "labels": dates[::-1],  # Reverse order for latest first
            "values": [round(random.uniform(50, 95), 2) for _ in range(10)]
        }

        return JsonResponse(risk_index)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
