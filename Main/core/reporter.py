#!/usr/bin/env python3

import datetime
import json
import subprocess
from .scanner import Scanner
import platform
import logging

class Reporter:
    def __init__(self, vulnerabilities_found):
        self.logger = logging.getLogger("Reporter")
        self.logger.info("Initializing Reporter with %d vulnerabilities", len(vulnerabilities_found))
        
        self.vulnerabilities_found = self.filter_duplicates(vulnerabilities_found)
        self.report_name = self.generate_timestamped_report_name()
        self.config_issues = []
        self.suspicious_traffic = []
        
    def filter_duplicates(self, vulnerabilities):
        """Filter out duplicate vulnerability entries"""
        self.logger.debug("Filtering duplicate vulnerabilities")
        if not vulnerabilities:
            return []
            
        unique_vulns = []
        seen = set()
        
        for vuln in vulnerabilities:
            vuln_key = (
                vuln.get('type', ''),
                vuln.get('description', ''),
                vuln.get('severity', ''),
                vuln.get('cve_id', ''),
                vuln.get('component', ''),
                vuln.get('affected_service', '')
            )
            
            if vuln_key not in seen:
                seen.add(vuln_key)
                unique_vulns.append(vuln)
        
        self.logger.info("Filtered %d unique vulnerabilities", len(unique_vulns))
        return unique_vulns

    def generate_timestamped_report_name(self):
        """Generate a timestamped report name"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"{timestamp}_report.json"
        return report_name

    def generate_detailed_report(self):
        """Generate comprehensive security report"""
        report_data = {
            "scan_summary": {
                "generated_at": datetime.datetime.now().isoformat(),
                "system_info": {
                    "platform": platform.system(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "architecture": platform.architecture()[0]
                },
                "risk_score": self.calculate_risk_score(),
                "total_vulnerabilities": len(self.vulnerabilities_found),
                "unique_categories": len(set(v.get('type', '') for v in self.vulnerabilities_found))
            },
            "vulnerability_summary": {
                "by_severity": self.summarize_by_severity(),
                "by_category": self.summarize_by_category(),
                "critical_findings": self.get_critical_findings()
            },
            "detailed_findings": {
                "vulnerabilities": self.vulnerabilities_found,
                "configuration_issues": self.config_issues,
                "suspicious_activities": self.suspicious_traffic
            },
            "recommendations": self.generate_recommendations(),
            "remediation_timeline": self.generate_remediation_timeline()
        }

        # Save report to file
        with open(self.report_name, "w") as report_file:
            json.dump(report_data, report_file, indent=4)

        self.logger.info("Detailed report saved: %s", self.report_name)
        print(f"Detailed report generated: {self.report_name}")
        return report_data
    
    def calculate_risk_score(self):
        """Calculate overall risk score based on findings"""
        score = 0
        severity_weights = {
            'CRITICAL': 10,
            'HIGH': 8,
            'MEDIUM': 5,
            'LOW': 2
        }
        
        for vuln in self.vulnerabilities_found:
            severity = vuln.get('severity', 'LOW').upper()
            score += severity_weights.get(severity, 1)
            
            # Additional weight for specific vulnerability types
            if vuln.get('type') in ['BIOS_SECURITY', 'ENCRYPTION', 'MALWARE']:
                score += 2
                
        # Normalize score to 0-100 range
        normalized_score = min(100, (score / (len(self.vulnerabilities_found) * 10)) * 100) if self.vulnerabilities_found else 0
        return round(normalized_score, 2)

    def generate_recommendations(self):
        """Generate detailed security recommendations based on findings"""
        recommendations = []
        
        # Group vulnerabilities by type
        vuln_types = {}
        for vuln in self.vulnerabilities_found:
            vuln_type = vuln.get('type', 'UNKNOWN')
            if vuln_type not in vuln_types:
                vuln_types[vuln_type] = []
            vuln_types[vuln_type].append(vuln)
        
        # Generate recommendations for each type
        for vuln_type, vulns in vuln_types.items():
            rec = {
                "category": vuln_type,
                "severity": max([v.get('severity', 'LOW') for v in vulns], key=lambda x: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].index(x)),
                "findings": len(vulns),
                "actions": []
            }
            
            # Add specific recommendations based on vulnerability type
            if vuln_type == 'HARDWARE':
                rec["actions"].extend([
                    "Update all hardware drivers to latest versions",
                    "Monitor system temperatures and performance",
                    "Consider hardware upgrades for critical components"
                ])
            elif vuln_type == 'SOFTWARE':
                rec["actions"].extend([
                    "Install all pending security updates",
                    "Remove or update vulnerable software versions",
                    "Review and adjust software security settings"
                ])
            elif vuln_type == 'CONFIGURATION':
                rec["actions"].extend([
                    "Apply security baseline configurations",
                    "Review and adjust security policies",
                    "Implement security best practices"
                ])
            
            recommendations.append(rec)
        
        return recommendations
    
    def summarize_by_severity(self):
        """Summarize vulnerabilities by severity"""
        summary = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0
        }
        
        for vuln in self.vulnerabilities_found:
            severity = vuln.get('severity', 'LOW').upper()
            summary[severity] = summary.get(severity, 0) + 1
            
        return summary

    def summarize_by_category(self):
        """Summarize vulnerabilities by category"""
        summary = {}
        
        for vuln in self.vulnerabilities_found:
            category = vuln.get('type', 'UNKNOWN')
            summary[category] = summary.get(category, 0) + 1
            
        return summary

    def get_critical_findings(self):
        """Extract critical and high severity findings"""
        return [vuln for vuln in self.vulnerabilities_found 
                if vuln.get('severity', '').upper() in ['CRITICAL', 'HIGH']]

    def generate_remediation_timeline(self):
        """Generate suggested remediation timeline"""
        timeline = {
            "immediate": [],
            "short_term": [],
            "long_term": []
        }
        
        for vuln in self.vulnerabilities_found:
            severity = vuln.get('severity', '').upper()
            if severity in ['CRITICAL', 'HIGH']:
                timeline["immediate"].append(vuln)
            elif severity == 'MEDIUM':
                timeline["short_term"].append(vuln)
            else:
                timeline["long_term"].append(vuln)
                
        return {
            "immediate": len(timeline["immediate"]),
            "short_term": len(timeline["short_term"]),
            "long_term": len(timeline["long_term"]),
            "suggested_timeline": {
                "immediate": "Within 24 hours",
                "short_term": "Within 1 week",
                "long_term": "Within 1 month"
            }
        }

    CATEGORY_MAP = {
        'ssh': 'NETWORK',
        'http': 'WEB',
        'kernel': 'SYSTEM',
        'driver': 'DRIVER'
    }
        
    def _categorize_vulnerability(self, vuln: Dict) -> str:
        """Improved categorization logic"""
        description = vuln.get('description', '').lower()
        component = vuln.get('component', '').lower()
        
        # Check component first
        for key, category in self.CATEGORY_MAP.items():
            if key in component:
                return category
                
        # Check description patterns
        if 'buffer overflow' in description:
            return 'MEMORY'
        if 'xss' in description or 'sql injection' in description:
            return 'WEB'
        if 'privilege escalation' in description:
            return 'AUTHORIZATION'
            
        return 'SYSTEM'

'''
def test_environment():
    print("Testing for vulnerable ports and services...")
    scanner = Scanner()
    vulnerabilities_found = scanner.scan_system()
    reporter = Reporter(vulnerabilities_found)
    reporter.generate_detailed_report()


if __name__ == "__main__":
    test_environment()'''