# New file: openvas_integration.py
import logging
from typing import Dict, Optional
import xml.etree.ElementTree as ET
import requests

class OpenVASIntegration:
    def __init__(self, host: str, username: str, password: str):
        self.logger = logging.getLogger("OpenVAS")
        self.base_url = f"https://{host}/omp"
        self.session = requests.Session()
        self.session.verify = False  # For testing only - use proper certs in production
        self._authenticate(username, password)

    def _authenticate(self, username: str, password: str):
        """Authenticate with OpenVAS manager"""
        auth_payload = f"""
        <authenticate>
            <credentials>
                <username>{username}</username>
                <password>{password}</password>
            </credentials>
        </authenticate>
        """
        response = self.session.post(
            f"{self.base_url}?cmd=authenticate",
            data=auth_payload,
            headers={'Content-Type': 'application/xml'}
        )
        response.raise_for_status()
        self.token = ET.fromstring(response.content).find('.//token').text

    def run_scan(self, target: str, config_id: str = "daba56c8-73ec-11df-a475-002264764cea") -> Dict:
        """Execute an OpenVAS scan and return parsed results"""
        try:
            # Create target
            create_target = f"""
            <create_target>
                <name>AigesX Target</name>
                <hosts>{target}</hosts>
            </create_target>
            """
            response = self.session.post(
                f"{self.base_url}?cmd=create_target&token={self.token}",
                data=create_target,
                headers={'Content-Type': 'application/xml'}
            )
            target_id = ET.fromstring(response.content).find('.//@id').text

            # Start task
            task_xml = f"""
            <create_task>
                <name>AigesX Scan</name>
                <config id="{config_id}"/>
                <target id="{target_id}"/>
            </create_task>
            """
            response = self.session.post(
                f"{self.base_url}?cmd=create_task&token={self.token}",
                data=task_xml,
                headers={'Content-Type': 'application/xml'}
            )
            task_id = ET.fromstring(response.content).find('.//@id').text

            # Get results
            report = self._get_results(task_id)
            return self._parse_results(report)
            
        except Exception as e:
            self.logger.error(f"OpenVAS scan failed: {str(e)}")
            return {}

    def _parse_results(self, report_xml: str) -> Dict:
        """Parse OpenVAS XML report into AigesX format"""
        root = ET.fromstring(report_xml)
        findings = []
        
        for result in root.findall('.//result'):
            findings.append({
                "type": "NETWORK",
                "severity": result.find('.//threat').text.upper(),
                "description": result.find('.//description').text,
                "cve_id": ",".join([n.text for n in result.findall('.//nvt/cve')]),
                "component": result.find('.//nvt/name').text,
                "recommendation": result.find('.//solution').text
            })
        
        return {"vulnerabilities": findings}