# engine/analysis/cve_generation.py

import json
from datetime import datetime

def generate_cve(vulnerabilities, affected_binary):
    """
    Generates a CVE-like report for detected vulnerabilities.

    :param vulnerabilities: List of classified vulnerabilities.
    :param affected_binary: The binary where vulnerabilities were found.
    :return: CVE report in JSON format.
    """
    cve_report = {
        "CVE_ID": f"CVE-{datetime.now().year}-{str(hash(affected_binary))[-6:]}",  # Generate a temporary CVE ID
        "date_reported": datetime.now().strftime("%Y-%m-%d"),
        "affected_binary": affected_binary,
        "vulnerabilities": vulnerabilities
    }

    # Save the CVE report as a JSON file
    cve_filename = f"CVE_{cve_report['CVE_ID']}.json"
    with open(cve_filename, 'w') as cve_file:
        json.dump(cve_report, cve_file, indent=4)

    print(f"CVE Report Generated: {cve_filename}")
    return cve_report
