import requests
import json
import os
from datetime import datetime, timedelta

# Constants
CVE_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
LOCAL_CVE_FILE = "cve_data/cve_data.json"
PATTERNS_FILE = "cve_data/cve_patterns.json"
CACHE_EXPIRY_DAYS = 7

def fetch_cve_data():
    """Fetch CVE data from NVD API in chunks and update local cache."""
    try:
        print("Fetching CVE data...")
        response = requests.get(CVE_API_URL)
        response.raise_for_status()
        data = response.json()

        with open(LOCAL_CVE_FILE, "w") as file:
            json.dump(data, file, indent=4)
        print("CVE data updated successfully.")
    except Exception as e:
        print(f"Error fetching CVE data: {e}")

def load_cve_data():
    """Load CVE data from local file."""
    if os.path.exists(LOCAL_CVE_FILE):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(LOCAL_CVE_FILE))
        if datetime.now() - file_mod_time < timedelta(days=CACHE_EXPIRY_DAYS):
            with open(LOCAL_CVE_FILE, "r") as file:
                return json.load(file)
        else:
            print("Cache expired. Fetching new data...")
            fetch_cve_data()
            return load_cve_data()
    else:
        print("No local cache found. Fetching data...")
        fetch_cve_data()
        return load_cve_data()

def preprocess_cve_data():
    """Extract relevant fields from raw CVE data and save as patterns."""
    if not os.path.exists(LOCAL_CVE_FILE):
        print("Error: CVE data file not found. Please fetch data first.")
        return

    try:
        with open(LOCAL_CVE_FILE, "r") as file:
            cve_data = json.load(file)

        patterns = []
        for cve_entry in cve_data.get("vulnerabilities", []):
            cve = cve_entry.get("cve", {})
            id = cve.get("id")
            description = next(
                (desc["value"] for desc in cve.get("descriptions", []) if desc["lang"] == "en"),
                "No description available"
            )
            affected_products = [
                match["criteria"]
                for config in cve.get("configurations", [])
                for node in config.get("nodes", [])
                for match in node.get("cpeMatch", [])
                if match.get("vulnerable")
            ]
            patterns.append({
                "id": id,
                "description": description,
                "affected_products": affected_products,
            })

        with open(PATTERNS_FILE, "w") as file:
            json.dump(patterns, file, indent=4)
        print(f"CVE patterns saved successfully to {PATTERNS_FILE}.")
    except Exception as e:
        print(f"Error preprocessing CVE data: {e}")


if __name__ == "__main__":
    cve_data = load_cve_data()
    preprocess_cve_data()