#!/usr/bin/env python3

import sys
import os
import json
import platform
import subprocess
import psycopg2
import win32security
import wmi
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import win32api
import re
import uuid
import datetime
import requests
import psutil
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import cve_data.fetcher

class Scanner:
    def __init__(self):
        self.logger = logging.getLogger("Scanner")
        self.logger.info("Initializing Scanner")
        
        if getattr(sys, 'frozen', False):
            self.application_path = os.path.dirname(sys.executable)
        else:
            self.application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        # Define data file paths
        self.patterns_file = os.path.join(self.application_path, "cve_data", "cve_patterns.json")
        self.port_service_map_file = os.path.join(self.application_path, "cve_data", "port_service_map.json")
        
        # Load data files
        self.cve_patterns = self.load_cve_patterns()
        self.port_service_map = self.load_port_service_map()
        self.system_ports = []
        self.detected_services = []
        self.processes = []
        self.found_vulnerabilities = set()  # Track already found vulnerabilities
        self.vulnerabilities = []
        self.system_info = self.get_system_info()
        self.severity_levels = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1
        }

    def load_cve_patterns(self):
        """Load CVE patterns with proper path handling"""
        self.logger.info("Loading CVE patterns from %s", self.patterns_file)
        try:
            with open(self.patterns_file, 'r') as f:
                patterns = json.load(f)
                self.logger.info("Loaded %d CVE patterns", len(patterns))
                return patterns
        except Exception as e:
            self.logger.error("Error loading CVE patterns: %s", e)
            return []
    
    def load_port_service_map(self):
        """Load port service map with proper path handling"""
        try:
            with open(self.port_service_map_file, 'r') as f:
                print("Loading port-service mapping...")
                return json.load(f)
        except Exception as e:
            print(f"Error loading port service map: {e}")
            return {}
        
    def perform_port_scan(self):
        """Scan listening ports on the system."""
        self.logger.info("Performing port scan")
        ports_in_use = []
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["netstat", "-an"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            elif platform.system() in ["Linux", "Darwin"]:
                result = subprocess.run(
                    ["ss", "-tuln"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            else:
                raise Exception("Platform not supported for port scanning.")
            
            for line in result.stdout.splitlines():
                if "LISTENING" in line or "LISTEN" in line:
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)', line) or re.search(r'(\[.*?\]):(\d+)', line)
                    if match:
                        port = int(match.group(2))
                        ports_in_use.append(port)

            self.logger.info("Found %d open ports", len(ports_in_use))
        except Exception as e:
            self.logger.error("Error during port scan: %s", e)
        
        self.system_ports = ports_in_use
        return ports_in_use

    def analyze_protocols(self, ports):
        """Analyze protocols running on open ports"""
        self.logger.info("Analyzing protocols on open ports")
        protocol_info = {}
        for port in ports:
            try:
                if port == 80 or port == 443:
                    protocol_info[port] = self.check_http_version(port)
                elif port == 445:
                    protocol_info[port] = self.check_smb_version(port)
                else:
                    protocol_info[port] = "Unknown protocol"
            except Exception as e:
                self.logger.error(f"Error analyzing port {port}: {e}")
                protocol_info[port] = "Error"
        return protocol_info

    def check_http_version(self, port):
        """Check HTTP version running on a port"""
        self.logger.info(f"Checking HTTP version on port {port}")
        try:
            if port == 80:
                url = "http://localhost"
            elif port == 443:
                url = "https://localhost"
            else:
                return "Not an HTTP port"
            
            response = requests.get(url, timeout=5)
            return f"HTTP/{response.raw.version} ({response.status_code})"
        except Exception as e:
            self.logger.error(f"Error checking HTTP version on port {port}: {e}")
            return "Unknown"

    def check_smb_version(self, port):
        """Check SMB version running on a port"""
        self.logger.info(f"Checking SMB version on port {port}")
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["powershell", "Get-SmbServerConfiguration"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return "SMBv3"  # Placeholder for actual SMB version detection
                else:
                    return "Unknown SMB version"
            else:
                return "SMB not supported on this platform"
        except Exception as e:
            self.logger.error(f"Error checking SMB version on port {port}: {e}")
            return "Unknown"


    def detect_network_services(self):
        """Detect known network services by matching ports with JSON service map."""
        print("Detecting network services...")
        detected_services = []
        for port in self.system_ports:
            try:
                service = self.port_service_map.get(str(port), {})
                banner = self._get_banner(port)
                
                if banner:
                    version = self._parse_version(banner)
                    service['version'] = version
                    service['vulnerable'] = self._check_version_against_cve(version)
                    
                self.detected_services.append(service)
                
            except Exception as e:
                self.logger.error(f"Service detection error on port {port}: {str(e)}")
        self.detected_services = detected_services
        return detected_services


    def perform_process_scan(self):
        """Scan currently running processes."""
        print("Scanning system processes...")
        processes = []
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["tasklist"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                for line in result.stdout.splitlines():
                    if line.strip():
                        processes.append(line.strip())
            elif platform.system() in ["Linux", "Darwin"]:
                result = subprocess.run(
                    ["ps", "-aux"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                for line in result.stdout.splitlines():
                    if line.strip():
                        processes.append(line.strip())
            else:
                raise Exception("Platform not supported for process scan.")

            print("Processes scanned.")
        except Exception as e:
            print(f"Error during process scan: {e}")
        self.processes = processes
        return processes

    def check_for_vulnerabilities(self):
        """Check system ports, detected services, and processes against loaded CVE patterns."""
        print("Scanning system data against CVE patterns...")
        results = []
        for pattern in self.cve_patterns:
            for service in self.detected_services:
                if service["service"] in pattern.get("affected_products", []):
                    results.append({
                        "cve_id": pattern["id"],
                        "description": pattern["description"],
                        "matched_pattern": f"Detected service: {service['service']} on port {service['port']}"
                    })

            for process in self.processes:
                if any(affected_product in process for affected_product in pattern.get("affected_products", [])):
                    results.append({
                        "cve_id": pattern["id"],
                        "description": pattern["description"],
                        "matched_pattern": f"Matched running process: {process}"
                    })
        print("Scan completed.")
        return results

    def add_vulnerability(self, vuln_type=None, severity=None, description=None, component=None, 
                         details=None, recommendation=None, cve_id=None, **kwargs):
        """Add vulnerability - accepts both dict and individual parameters"""
        if isinstance(vuln_type, dict):
            # If first argument is a dictionary, use it as the vulnerability
            vulnerability = vuln_type
            # Ensure severity_score is set
            if 'severity' in vulnerability and 'severity_score' not in vulnerability:
                vulnerability['severity_score'] = self.severity_levels.get(vulnerability['severity'], 0)
        else:
            # Otherwise construct from individual parameters
            vulnerability = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.datetime.now().isoformat(),
                "type": vuln_type,
                "severity": severity,
                "severity_score": self.severity_levels.get(severity, 0),
                "description": description,
                "component": component,
                "details": details,
                "recommendation": recommendation,
                "cve_id": cve_id
            }
            vulnerability.update(kwargs)  # Add any additional fields
        
        self.vulnerabilities.append(vulnerability)

    def scan_system(self):
        """Perform comprehensive system scanning"""
        print("Starting comprehensive system scan...")
        vulnerabilities = []
        bios_vulns = self.check_bios_security()
        vulnerabilities.extend(bios_vulns)
        service_vulns = self.check_dangerous_services()
        vulnerabilities.extend(service_vulns)
        driver_vulns = self.check_driver_security()
        vulnerabilities.extend(driver_vulns)
        
        return vulnerabilities

    def check_bios_security(self):
        """Check BIOS/UEFI security settings"""
        vulnerabilities = []
        try:
            # Check Secure Boot Status
            result = subprocess.run(
                ["powershell", "Confirm-SecureBootUEFI"],
                capture_output=True,
                text=True
            )
            if "False" in result.stdout or result.returncode != 0:
                vulnerabilities.append({
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "BIOS_SECURITY",
                    "severity": "HIGH",
                    "severity_score": 3,
                    "description": "Secure Boot is disabled",
                    "component": "BIOS/UEFI",
                    "details": None,
                    "recommendation": "Enable Secure Boot in BIOS/UEFI settings",
                    "cve_id": None
                })
        except Exception as e:
            print(f"Error checking Secure Boot: {e}")
        
        return vulnerabilities

    def check_dangerous_services(self):
        """Check for dangerous services"""
        vulnerabilities = []
        dangerous_services = {
            "RemoteRegistry": {
                "description": "Remote Registry service is enabled",
                "recommendation": "Disable Remote Registry service if not required"
            },
            "RpcSs": {
                "description": "RPC service might be exposed",
                "recommendation": "Restrict RPC access if not needed"
            }
        }
        
        try:
            result = subprocess.run(
                ["powershell", "Get-Service"],
                capture_output=True,
                text=True
            )
            
            for service_name, info in dangerous_services.items():
                if service_name in result.stdout and "Running" in result.stdout:
                    vulnerabilities.append({
                        "id": str(uuid.uuid4()),
                        "timestamp": datetime.datetime.now().isoformat(),
                        "type": "DANGEROUS_SERVICE",
                        "severity": "HIGH" if service_name == "RemoteRegistry" else "MEDIUM",
                        "severity_score": 3 if service_name == "RemoteRegistry" else 2,
                        "description": info["description"],
                        "component": "Services",
                        "details": None,
                        "recommendation": info["recommendation"],
                        "cve_id": None
                    })
        except Exception as e:
            print(f"Error checking services: {e}")
        
        return vulnerabilities

    def check_driver_security(self):
        """Check for vulnerable drivers"""
        vulnerabilities = []
        try:
            result = subprocess.run(
                ["powershell", "driverquery /v"],
                capture_output=True,
                text=True
            )
            
            # Check for Realtek HD Audio driver
            if "rtkvhd64.sys" in result.stdout:
                vulnerabilities.append({
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "DRIVER_SECURITY",
                    "severity": "HIGH",
                    "severity_score": 3,
                    "description": "Potentially vulnerable driver detected: Realtek HD Audio driver",
                    "component": "Drivers",
                    "details": "Driver: rtkvhd64.sys, Version: ",
                    "recommendation": "Update driver to latest version",
                    "cve_id": None
                })
            
        except Exception as e:
            print(f"Error checking drivers: {e}")
        
        return vulnerabilities

    def filter_duplicates(self, vulnerabilities):
        """Filter out duplicate vulnerability entries"""
        if not vulnerabilities:
            return []
        
        unique_vulns = []
        seen = set()
        
        for vuln in vulnerabilities:
            # Create a tuple of key attributes to check for duplicates
            key = (vuln['type'], vuln['description'])
            if key not in seen:
                seen.add(key)
                unique_vulns.append(vuln)
        
        return unique_vulns

    def get_system_info(self):
        """Gather basic system information"""
        return {
            "os": platform.system(),
            "version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node()
        }

    def scan_configurations(self):
        """Scan system configurations for security issues"""
        config_issues = []
        
        # Check common security misconfigurations
        if platform.system() == "Windows":
            # Check Windows Firewall status
            result = subprocess.run(
                ["netsh", "advfirewall", "show", "allprofiles"], 
                capture_output=True, 
                text=True
            )
            if "State                                 OFF" in result.stdout:
                config_issues.append({
                    "type": "FIREWALL_DISABLED",
                    "severity": "HIGH",
                    "description": "Windows Firewall is disabled"
                })
            
        elif platform.system() in ["Linux", "Darwin"]:
            # Check SSH configuration
            if os.path.exists("/etc/ssh/sshd_config"):
                with open("/etc/ssh/sshd_config") as f:
                    config = f.read()
                    if "PermitRootLogin yes" in config:
                        config_issues.append({
                            "type": "SSH_ROOT_LOGIN",
                            "severity": "HIGH",
                            "description": "SSH root login is enabled"
                        })
        
        return config_issues

    def get_running_services(self):
        """Get list of running services with versions"""
        services = {}
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "service", "get", "name,pathname"],
                    capture_output=True,
                    text=True
                )
                # Parse Windows services
                for line in result.stdout.splitlines()[1:]:
                    if line.strip():
                        parts = line.split()
                        if parts:
                            services[parts[0]] = self.get_service_version(parts[0])
            else:
                result = subprocess.run(
                    ["systemctl", "list-units", "--type=service"],
                    capture_output=True,
                    text=True
                )
                # Parse Linux services
                for line in result.stdout.splitlines():
                    if "running" in line:
                        service = line.split()[0]
                        services[service] = self.get_service_version(service)
        except Exception as e:
            print(f"Error getting running services: {e}")
        return services

    def check_weak_permissions(self):
        """Check for weak file and directory permissions"""
        weak_perms = []
        critical_paths = [
            "/etc/passwd", "/etc/shadow",  # Linux
            "C:\\Windows\\System32",       # Windows
            "/usr/bin", "/usr/sbin"        # Linux
        ]
        
        for path in critical_paths:
            if os.path.exists(path):
                try:
                    perms = os.stat(path).st_mode
                    if platform.system() != "Windows":
                        # Check for world-writeable files
                        if perms & 0o002:
                            weak_perms.append(f"World-writeable permissions on {path}")
                    else:
                        security = win32security.GetFileSecurity(
                            path, 
                            win32security.DACL_SECURITY_INFORMATION
                        )
                        dacl = security.GetSecurityDescriptorDacl()
                        if dacl is None:
                            weak_perms.append(f"No DACL protection on {path}")
                except Exception as e:
                    print(f"Error checking permissions for {path}: {e}")
        
        return weak_perms

    def check_malware_indicators(self):
        """Check for common malware indicators"""
        indicators = []
        
        # Check for suspicious processes
        suspicious_processes = [
            "cryptominer", "miner", "botnet",
            "backdoor", "trojan", "keylogger"
        ]
        
        for process in self.processes:
            if any(indicator in process.lower() for indicator in suspicious_processes):
                indicators.append(f"Suspicious process: {process}")
        
        # Check for suspicious network connections
        suspicious_ports = [
            "21320",  # Known malware proxy port
            "6667",   # Common botnet C&C port
            "4444"    # Common backdoor port
        ]
        
        for port in self.system_ports:
            if str(port) in suspicious_ports:
                indicators.append(f"Suspicious port in use: {port}")
        
        return indicators

    def get_service_version(self, service_name):
        """Get version information for a service"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "service", "where", f"name='{service_name}'", "get", "pathname"],
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    path = result.stdout.split("\n")[1].strip()
                    if path:
                        return self.get_file_version(path)
            else:
                # Try to get version from package manager
                result = subprocess.run(
                    ["dpkg", "-s", service_name] if os.path.exists("/usr/bin/dpkg") else ["rpm", "-q", service_name],
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    return result.stdout.split("Version: ")[-1].split("\n")[0]
        except Exception as e:
            print(f"Error getting service version: {e}")
        return "Unknown"

    def get_file_version(self, file_path):
        """Get version information from a file"""
        try:
            info = win32api.GetFileVersionInfo(file_path, "\\")
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            return f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
        except:
            return "Unknown"

    def check_hardware_vulnerabilities(self):
        """Check hardware components and drivers for vulnerabilities using PowerShell"""
        vulnerabilities = []
        
        if platform.system() == "Windows":
            try:
                # Check Graphics Drivers
                result = subprocess.run(
                    ["powershell", "Get-WmiObject Win32_VideoController | Select-Object Caption,DriverVersion"],
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    for line in result.stdout.splitlines()[3:]:  # Skip header lines
                        if line.strip():
                            vuln = {
                                "type": "HARDWARE_DRIVER",
                                "component": "Graphics",
                                "details": line.strip(),
                                "severity": "MEDIUM",
                                "recommendation": "Check for graphics driver updates"
                            }
                            if self.add_vulnerability(vuln):
                                vulnerabilities.append(vuln)

                # Check Storage Devices
                result = subprocess.run(
                    ["powershell", "Get-PhysicalDisk | Select-Object FriendlyName,HealthStatus,OperationalStatus"],
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    for line in result.stdout.splitlines()[3:]:
                        if "Unhealthy" in line or "Warning" in line:
                            vuln = {
                                "type": "HARDWARE",
                                "component": "Storage",
                                "details": line.strip(),
                                "severity": "HIGH",
                                "recommendation": "Check disk health and consider replacement"
                            }
                            if self.add_vulnerability(vuln):
                                vulnerabilities.append(vuln)

                # Check Memory Status
                result = subprocess.run(
                    ["powershell", "Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity,Speed,Manufacturer"],
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    total_memory = 0
                    for line in result.stdout.splitlines()[3:]:
                        if line.strip():
                            total_memory += 1
                            if "Error" in line or "Unknown" in line:
                                vuln = {
                                    "type": "HARDWARE",
                                    "component": "Memory",
                                    "details": line.strip(),
                                    "severity": "HIGH",
                                    "recommendation": "Check memory health and consider replacement"
                                }
                                if self.add_vulnerability(vuln):
                                    vulnerabilities.append(vuln)

                # Check Network Adapters
                result = subprocess.run(
                    ["powershell", "Get-NetAdapter | Select-Object Name,Status,LinkSpeed"],
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    for line in result.stdout.splitlines()[3:]:
                        if "Disabled" in line or "Disconnected" in line:
                            vuln = {
                                "type": "HARDWARE",
                                "component": "Network Adapter",
                                "details": line.strip(),
                                "severity": "MEDIUM",
                                "recommendation": "Check network adapter status and drivers"
                            }
                            if self.add_vulnerability(vuln):
                                vulnerabilities.append(vuln)

                # Check CPU Information
                result = subprocess.run(
                    ["powershell", "Get-WmiObject Win32_Processor | Select-Object Name,MaxClockSpeed,Status"],
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    for line in result.stdout.splitlines()[3:]:
                        if "Error" in line or "Unknown" in line:
                            vuln = {
                                "type": "HARDWARE",
                                "component": "CPU",
                                "details": line.strip(),
                                "severity": "HIGH",
                                "recommendation": "Check CPU health and cooling system"
                            }
                            if self.add_vulnerability(vuln):
                                vulnerabilities.append(vuln)

                # Check System Temperature (if available)
                try:
                    result = subprocess.run(
                        ["powershell", "Get-CimInstance MSAcpi_ThermalZoneTemperature -Namespace root/wmi"],
                        capture_output=True,
                        text=True
                    )
                    if result.stdout and "CurrentTemperature" in result.stdout:
                        temp = float(result.stdout.split("CurrentTemperature")[1].split()[0])
                        # Convert temperature from decikelvin to celsius
                        temp = (temp / 10) - 273.15
                        if temp > 80:  # CPU temperature threshold
                            vuln = {
                                "type": "HARDWARE",
                                "component": "System Temperature",
                                "details": f"High system temperature detected: {temp:.1f}°C",
                                "severity": "HIGH",
                                "recommendation": "Check system cooling and clean dust"
                            }
                            if self.add_vulnerability(vuln):
                                vulnerabilities.append(vuln)
                except Exception as e:
                    print(f"Error checking temperature: {e}")

            except Exception as e:
                print(f"Error checking hardware: {e}")

        return vulnerabilities

    def check_system_components(self):
        """Check system components for vulnerabilities"""
        vulnerabilities = []
        
        if platform.system() == "Windows":
            try:
                # Check Windows Update Status
                result = subprocess.run(
                    ["powershell", "Get-HotFix | Sort-Object -Property InstalledOn"],
                    capture_output=True,
                    text=True
                )
                last_update = None
                if result.stdout:
                    updates = result.stdout.splitlines()
                    if updates:
                        last_update = updates[-1]
                        # Check if last update is older than 30 days
                        if "InstalledOn" in last_update:
                            vuln = {
                                "type": "SYSTEM_UPDATE",
                                "severity": "HIGH",
                                "description": "System updates may be outdated",
                                "details": f"Last update: {last_update}",
                                "recommendation": "Check and install Windows updates"
                            }
                            if self.add_vulnerability(vuln):
                                vulnerabilities.append(vuln)

                # Check System Restore Status
                result = subprocess.run(
                    ["powershell", "Get-ComputerRestorePoint"],
                    capture_output=True,
                    text=True
                )
                if not result.stdout:
                    vuln = {
                        "type": "SYSTEM_PROTECTION",
                        "severity": "MEDIUM",
                        "description": "System Restore points not found",
                        "recommendation": "Enable System Restore and create restore points"
                    }
                    if self.add_vulnerability(vuln):
                        vulnerabilities.append(vuln)

                # Check Disk Encryption Status
                result = subprocess.run(
                    ["manage-bde", "-status"],
                    capture_output=True,
                    text=True
                )
                if "Protection Off" in result.stdout:
                    vuln = {
                        "type": "ENCRYPTION",
                        "severity": "HIGH",
                        "description": "BitLocker encryption is not enabled",
                        "recommendation": "Enable BitLocker disk encryption"
                    }
                    if self.add_vulnerability(vuln):
                        vulnerabilities.append(vuln)

                # Check User Account Control Settings
                result = subprocess.run(
                    ["reg", "query", "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", "/v", "EnableLUA"],
                    capture_output=True,
                    text=True
                )
                if "0x0" in result.stdout:
                    vuln = {
                        "type": "SECURITY_CONTROL",
                        "severity": "HIGH",
                        "description": "User Account Control (UAC) is disabled",
                        "recommendation": "Enable UAC for better system security"
                    }
                    if self.add_vulnerability(vuln):
                        vulnerabilities.append(vuln)

                # Check for Unsigned Drivers
                result = subprocess.run(
                    ["powershell", "Get-WindowsDriver -Online | Where-Object {$_.IsSigned -eq $false}"],
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    vuln = {
                        "type": "DRIVER_SECURITY",
                        "severity": "HIGH",
                        "description": "Unsigned drivers detected",
                        "details": result.stdout.strip(),
                        "recommendation": "Remove or replace unsigned drivers"
                    }
                    if self.add_vulnerability(vuln):
                        vulnerabilities.append(vuln)

            except Exception as e:
                print(f"Error checking system components: {e}")

        return vulnerabilities

    def check_windows_updates(self):
        """Check Windows update status"""
        # Implementation needed
        pass

    def check_user_accounts(self):
        """Check user accounts for security issues"""
        # Implementation needed
        pass

    def check_admin_privileges(self):
        """Check admin privileges for security issues"""
        # Implementation needed
        pass

    def check_password_policy(self):
        """Check password policy for security issues"""
        # Implementation needed
        pass

    def check_audit_policy(self):
        """Check audit policy for security issues"""
        # Implementation needed
        pass

    def check_network_shares(self):
        """Check network shares for security issues"""
        # Implementation needed
        pass

    def check_wifi_security(self):
        """Check WiFi security"""
        # Implementation needed
        pass

    def check_ssl_certificates(self):
        """Check SSL certificates for security issues"""
        # Implementation needed
        pass

    def check_open_ports(self):
        """Check open ports for security issues"""
        # Implementation needed
        pass

    def check_tpm_status(self):
        """Check TPM status"""
        # Implementation needed
        pass

    def check_windows_firewall(self):
        """Check Windows Firewall status"""
        try:
            result = subprocess.run(
                ["netsh", "advfirewall", "show", "allprofiles"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                if "State                                 OFF" in result.stdout:
                    self.add_vulnerability({
                        "type": "FIREWALL",
                        "severity": "HIGH",
                        "description": "Windows Firewall is disabled",
                        "component": "Windows Firewall",
                        "recommendation": "Enable Windows Firewall for all profiles"
                    })
                
                # Check individual profiles
                profiles = ["Domain Profile", "Private Profile", "Public Profile"]
                for profile in profiles:
                    if f"{profile}\nState                                 OFF" in result.stdout:
                        self.add_vulnerability({
                            "type": "FIREWALL",
                            "severity": "MEDIUM",
                            "description": f"Windows Firewall is disabled for {profile}",
                            "component": "Windows Firewall",
                            "recommendation": f"Enable Windows Firewall for {profile}"
                        })
        except Exception as e:
            print(f"Error checking Windows Firewall: {e}")

    def check_memory_health(self):
        """Check system memory health"""
        try:
            if platform.system() == "Windows":
                # Using WMI to get memory information
                result = subprocess.run(
                    ["powershell", "Get-WmiObject Win32_PhysicalMemory | Select-Object Status,DeviceLocator"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    if "Error" in result.stdout or "Degraded" in result.stdout:
                        self.add_vulnerability(
                            vuln_type="HARDWARE",
                            severity="HIGH",
                            description="Memory health issues detected",
                            component="System Memory",
                            recommendation="Run memory diagnostics and consider replacement if issues persist"
                        )
                        
                # Check memory usage
                memory = psutil.virtual_memory()
                if memory.percent > 90:
                    self.add_vulnerability(
                        vuln_type="HARDWARE",
                        severity="MEDIUM",
                        description=f"High memory usage detected ({memory.percent}%)",
                        component="System Memory",
                        recommendation="Close unnecessary applications or consider adding more RAM"
                    )
                
        except Exception as e:
            print(f"Error checking memory health: {e}")


class VulnerabilityPattern:
    def __init__(self):
        self.patterns = {
            'system_services': self.load_service_patterns(),
            'registry_keys': self.load_registry_patterns(),
            'hardware_indicators': self.load_hardware_patterns(),
            'bios_configurations': self.load_bios_patterns(),
            'driver_issues': self.load_driver_patterns()
        }
        
    def load_service_patterns(self):
        return {
            'critical_services': {
                'paths': [
                    r'SYSTEM\CurrentControlSet\Services',
                    r'SYSTEM\CurrentControlSet\Control'
                ],
                'indicators': {
                    'unquoted_service_path': r'^[^"].*\s+.*\.exe',
                    'weak_permissions': r'Everyone|Authenticated Users',
                    'vulnerable_versions': r'1\.[0-5]\.'
                }
            }
        }

    def load_registry_patterns(self):
        return {
            'security_settings': {
                'paths': [
                    r'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies',
                    r'SOFTWARE\Policies\Microsoft\Windows\System',
                    r'SYSTEM\CurrentControlSet\Control\SecurityProviders'
                ],
                'dangerous_values': {
                    'EnableLUA': 0,
                    'ConsentPromptBehaviorAdmin': 0,
                    'FilterAdministratorToken': 0
                }
            }
        }

    def load_hardware_patterns(self):
        return {
            'temperature_thresholds': {
                'CPU': {'warning': 70, 'critical': 85},
                'GPU': {'warning': 80, 'critical': 90},
                'Storage': {'warning': 45, 'critical': 55}
            },
            'performance_indicators': {
                'memory_usage': {'warning': 85, 'critical': 95},
                'disk_usage': {'warning': 85, 'critical': 95},
                'cpu_usage': {'warning': 90, 'critical': 95}
            }
        }

    def load_bios_patterns(self):
        return {
            'security_features': [
                'SecureBoot',
                'TPM',
                'VirtualizationTechnology',
                'ExecuteDisable',
                'BootGuard'
            ],
            'dangerous_settings': [
                'LegacyBoot',
                'CSM',
                'FastBoot'
            ]
        }

    def load_driver_patterns(self):
        """Load patterns for detecting vulnerable drivers"""
        return {
            'vulnerable_drivers': {
                'known_vulnerable': [
                    'nvlddmkm.sys',  # NVIDIA display driver
                    'atikmpag.sys',  # AMD display driver
                    'igdkmd64.sys',  # Intel display driver
                    'dxgkrnl.sys',   # DirectX Graphics Kernel
                    'bcmwl63a.sys',  # Broadcom wireless driver
                    'rtkvhd64.sys',  # Realtek HD Audio driver
                    'usbhub3.sys'    # USB 3.0 hub driver
                ],
                'version_patterns': [
                    r'\b(201[0-7]|200\d)\b',  # Old versions (2000-2017)
                    r'(nvidia|intel|amd).*\b(1\.|2\.0)\b',  # Known vulnerable versions
                    r'driver.*\b(5\.0|6\.0)\b'  # Generic old driver versions
                ]
            },
            'indicators': {
                'unsigned': True,
                'outdated': r'\b(201[0-7]|200\d)\b',
                'known_vulnerable': r'(nvidia|intel|amd).*\b(1\.|2\.0)\b'
            },
            'risk_factors': {
                'kernel_mode': True,
                'direct_hardware_access': True,
                'system_level_privileges': True
            }
        }

class AutomatedScannerEngine:
    def __init__(self):
        self.patterns = VulnerabilityPattern()
        self.wmi_client = self.initialize_wmi()
        self.vulnerability_db = {}  # Initialize empty first
        try:
            self.vulnerability_db = self.load_vulnerability_database()
        except Exception as e:
            print(f"Error initializing vulnerability database: {e}")
        
    def initialize_wmi(self):
        try:
            return wmi.WMI()
        except Exception as e:
            print(f"Error initializing WMI: {e}")
            return None

    def load_vulnerability_database(self):
        """Load vulnerability database from multiple sources"""
        vulnerabilities = {}
        try:
            # Load from NVD
            nvd_vulns = self.fetch_nvd_data()
            vulnerabilities.update(nvd_vulns)
            
            # Load from local database
            local_vulns = self.load_local_vulnerability_db()
            vulnerabilities.update(local_vulns)
            
            # Load from custom patterns
            custom_vulns = self.load_custom_patterns()
            vulnerabilities.update(custom_vulns)
            
        except Exception as e:
            print(f"Error loading vulnerability database: {e}")
        
        return vulnerabilities

    def fetch_nvd_data(self):
        """Fetch vulnerability data from National Vulnerability Database"""
        try:
            # Placeholder for actual NVD API integration
            return {}
        except Exception as e:
            print(f"Error fetching NVD data: {e}")
            return {}

    def load_local_vulnerability_db(self):
        """Load vulnerability data from local database"""
        try:
            # Placeholder for local database loading
            return {}
        except Exception as e:
            print(f"Error loading local vulnerability database: {e}")
            return {}

    def load_custom_patterns(self):
        """Load custom vulnerability patterns"""
        try:
            # Use patterns from VulnerabilityPattern class
            return self.patterns.patterns
        except Exception as e:
            print(f"Error loading custom patterns: {e}")
            return {}

    def deep_system_scan(self):
        """Perform deep system scanning using WMI and system APIs"""
        scan_results = {
            'hardware': self.scan_hardware_deep(),
            'software': self.scan_software_deep(),
            'configuration': self.scan_configuration_deep(),
            'security': self.scan_security_deep()
        }
        return self.analyze_results(scan_results)

    def scan_hardware_deep(self):
        """Deep hardware scanning"""
        hardware_info = {}
        
        if self.wmi_client:
            try:
                # CPU Information
                hardware_info['cpu'] = [{
                    'name': cpu.Name,
                    'load': cpu.LoadPercentage,
                    'voltage': cpu.CurrentVoltage,
                    'cores': cpu.NumberOfCores
                } for cpu in self.wmi_client.Win32_Processor()]

                # Memory Information
                hardware_info['memory'] = [{
                    'capacity': mem.Capacity,
                    'speed': mem.Speed,
                    'manufacturer': mem.Manufacturer,
                    'location': mem.DeviceLocator
                } for mem in self.wmi_client.Win32_PhysicalMemory()]

                # Storage Information
                hardware_info['storage'] = [{
                    'model': disk.Model,
                    'size': disk.Size,
                    'status': disk.Status,
                    'smart_status': self.get_smart_status(disk.DeviceID)
                } for disk in self.wmi_client.Win32_DiskDrive()]

            except Exception as e:
                print(f"Error during hardware scan: {e}")

        return hardware_info

    def get_smart_status(self, device_id):
        """Get SMART status for a disk"""
        try:
            if self.wmi_client:
                # Query MSStorageDriver_FailurePredictStatus
                query = f"SELECT * FROM MSStorageDriver_FailurePredictStatus WHERE InstanceName LIKE '%{device_id}%'"
                smart_info = self.wmi_client.query(query)
                
                for item in smart_info:
                    return {
                        'predictFailure': bool(item.PredictFailure),
                        'reason': item.Reason if hasattr(item, 'Reason') else 'Unknown',
                        'status': 'Warning' if item.PredictFailure else 'OK'
                    }
            return {'status': 'Unknown', 'error': 'WMI unavailable'}
        except Exception as e:
            return {'status': 'Error', 'error': str(e)}

    def scan_software_deep(self):
        """Deep software scanning"""
        return {
            'drivers': self.scan_drivers(),
            'services': self.scan_services(),
            'processes': self.scan_processes(),
            'installed_software': self.scan_installed_software()
        }

    def scan_drivers(self):
        """Scan system drivers"""
        drivers = []
        try:
            if self.wmi_client:
                for driver in self.wmi_client.Win32_SystemDriver():
                    drivers.append({
                        'name': driver.Name,
                        'path': driver.PathName,
                        'state': driver.State,
                        'start_mode': driver.StartMode,
                        'status': driver.Status
                    })
        except Exception as e:
            print(f"Error scanning drivers: {e}")
        return drivers

    def scan_services(self):
        """Scan system services"""
        services = []
        try:
            if self.wmi_client:
                for service in self.wmi_client.Win32_Service():
                    services.append({
                        'name': service.Name,
                        'display_name': service.DisplayName,
                        'state': service.State,
                        'start_mode': service.StartMode,
                        'path': service.PathName
                    })
        except Exception as e:
            print(f"Error scanning services: {e}")
        return services

    def scan_processes(self):
        """Scan running processes"""
        processes = []
        try:
            if self.wmi_client:
                for process in self.wmi_client.Win32_Process():
                    processes.append({
                        'name': process.Name,
                        'pid': process.ProcessId,
                        'path': process.ExecutablePath,
                        'command_line': process.CommandLine
                    })
        except Exception as e:
            print(f"Error scanning processes: {e}")
        return processes

    def scan_installed_software(self):
        """Scan installed software"""
        software = []
        try:
            if self.wmi_client:
                for product in self.wmi_client.Win32_Product():
                    software.append({
                        'name': product.Name,
                        'version': product.Version,
                        'vendor': product.Vendor,
                        'install_date': product.InstallDate
                    })
        except Exception as e:
            print(f"Error scanning installed software: {e}")
        return software

    def scan_configuration_deep(self):
        """Deep configuration scanning"""
        return {
            'registry': self.scan_registry_recursive(),
            'services': self.scan_service_configurations(),
            'network': self.scan_network_configuration(),
            'security': self.scan_security_configuration()
        }

    def scan_security_deep(self):
        """Deep security scanning"""
        return {
            'firewall': self.scan_firewall_configuration(),
            'antivirus': self.scan_antivirus_status(),
            'updates': self.scan_system_updates(),
            'permissions': self.scan_security_permissions()
        }

    # Add placeholder methods for remaining scans
    def scan_registry_recursive(self):
        return {}

    def scan_service_configurations(self):
        return {}

    def scan_network_configuration(self):
        return {}

    def scan_security_configuration(self):
        return {}

    def scan_firewall_configuration(self):
        return {}

    def scan_antivirus_status(self):
        return {}

    def scan_system_updates(self):
        return {}

    def scan_security_permissions(self):
        return {}

    def matches_pattern(self, value, pattern_data):
        """Match a value against a pattern"""
        try:
            if isinstance(pattern_data, dict):
                return any(self.matches_pattern(value, p) for p in pattern_data.values())
            elif isinstance(pattern_data, (list, tuple)):
                return any(self.matches_pattern(value, p) for p in pattern_data)
            elif isinstance(pattern_data, str):
                return bool(re.search(pattern_data, str(value), re.IGNORECASE))
            elif isinstance(pattern_data, bool):
                return bool(value) == pattern_data
            return False
        except Exception as e:
            print(f"Error matching pattern: {e}")
            return False

    def calculate_severity(self, category, pattern_name, value):
        """Calculate severity based on pattern match"""
        try:
            # Default severity levels
            severity_map = {
                'critical_services': 'HIGH',
                'vulnerable_drivers': 'HIGH',
                'security_settings': 'MEDIUM',
                'performance_indicators': 'LOW'
            }
            return severity_map.get(pattern_name, 'MEDIUM')
        except Exception as e:
            print(f"Error calculating severity: {e}")
            return 'LOW'

    def prioritize_vulnerabilities(self, vulnerabilities):
        """Prioritize vulnerabilities based on severity and impact"""
        try:
            severity_scores = {
                'CRITICAL': 4,
                'HIGH': 3,
                'MEDIUM': 2,
                'LOW': 1
            }
            
            for vuln in vulnerabilities:
                vuln['priority_score'] = severity_scores.get(vuln.get('severity', 'LOW'), 0)
                
                # Adjust score based on additional factors
                if vuln.get('category') == 'security':
                    vuln['priority_score'] *= 1.5
                if 'kernel' in str(vuln.get('description', '')).lower():
                    vuln['priority_score'] *= 1.2
                    
            return sorted(vulnerabilities, key=lambda x: x.get('priority_score', 0), reverse=True)
        except Exception as e:
            print(f"Error prioritizing vulnerabilities: {e}")
            return vulnerabilities

    def analyze_results(self, scan_results):
        """Analyze scan results and return vulnerabilities"""
        try:
            vulnerabilities = []
            
            # Process hardware vulnerabilities
            if 'hardware' in scan_results:
                hw_vulns = self.analyze_hardware_vulnerabilities(scan_results['hardware'])
                vulnerabilities.extend(hw_vulns)
            
            # Process software vulnerabilities
            if 'software' in scan_results:
                sw_vulns = self.analyze_software_vulnerabilities(scan_results['software'])
                vulnerabilities.extend(sw_vulns)
            
            # Process configuration vulnerabilities
            if 'configuration' in scan_results:
                config_vulns = self.analyze_configuration_vulnerabilities(scan_results['configuration'])
                vulnerabilities.extend(config_vulns)
            
            # Process security vulnerabilities
            if 'security' in scan_results:
                sec_vulns = self.analyze_security_vulnerabilities(scan_results['security'])
                vulnerabilities.extend(sec_vulns)
            
            return self.prioritize_vulnerabilities(vulnerabilities)
        except Exception as e:
            print(f"Error analyzing results: {e}")
            return []

    def analyze_hardware_vulnerabilities(self, hardware_data):
        """Analyze hardware-specific vulnerabilities"""
        vulnerabilities = []
        try:
            if 'cpu' in hardware_data:
                for cpu in hardware_data['cpu']:
                    if cpu.get('load', 0) > 90:
                        vulnerabilities.append({
                            'type': 'HARDWARE',
                            'category': 'CPU',
                            'severity': 'MEDIUM',
                            'description': f"High CPU load detected: {cpu.get('load')}%"
                        })

            if 'memory' in hardware_data:
                for mem in hardware_data['memory']:
                    if not mem.get('status', '').upper() == 'OK':
                        vulnerabilities.append({
                            'type': 'HARDWARE',
                            'category': 'MEMORY',
                            'severity': 'HIGH',
                            'description': f"Memory issue detected: {mem.get('status')}"
                        })

            if 'storage' in hardware_data:
                for disk in hardware_data['storage']:
                    smart_status = disk.get('smart_status', {})
                    if smart_status.get('predictFailure'):
                        vulnerabilities.append({
                            'type': 'HARDWARE',
                            'category': 'STORAGE',
                            'severity': 'CRITICAL',
                            'description': f"Disk failure predicted: {smart_status.get('reason', 'Unknown reason')}"
                        })
        except Exception as e:
            print(f"Error analyzing hardware vulnerabilities: {e}")

        return vulnerabilities

    def analyze_software_vulnerabilities(self, software_data):
        """Analyze software-specific vulnerabilities"""
        vulnerabilities = []
        try:
            if 'drivers' in software_data:
                for driver in software_data['drivers']:
                    if driver.get('state') != 'Running':
                        vulnerabilities.append({
                            'type': 'SOFTWARE',
                            'category': 'DRIVER',
                            'severity': 'MEDIUM',
                            'description': f"Driver issue: {driver.get('name')} - {driver.get('state')}"
                        })
        except Exception as e:
            print(f"Error analyzing software vulnerabilities: {e}")
        return vulnerabilities

    def analyze_configuration_vulnerabilities(self, config_data):
        """Analyze configuration-specific vulnerabilities"""
        vulnerabilities = []
        try:
            if 'security' in config_data:
                sec_config = config_data['security']
                if not sec_config.get('firewall_enabled', True):
                    vulnerabilities.append({
                        'type': 'CONFIGURATION',
                        'category': 'SECURITY',
                        'severity': 'HIGH',
                        'description': "Firewall is disabled"
                    })
        except Exception as e:
            print(f"Error analyzing configuration vulnerabilities: {e}")
        return vulnerabilities

    def analyze_security_vulnerabilities(self, security_data):
        """Analyze security-specific vulnerabilities"""
        vulnerabilities = []
        try:
            if 'antivirus' in security_data:
                av_status = security_data['antivirus']
                if not av_status.get('enabled', False):
                    vulnerabilities.append({
                        'type': 'SECURITY',
                        'category': 'ANTIVIRUS',
                        'severity': 'CRITICAL',
                        'description': "Antivirus protection is disabled"
                    })
        except Exception as e:
            print(f"Error analyzing security vulnerabilities: {e}")
        return vulnerabilities

class MLScanner:
    def __init__(self):
        self.logger = logging.getLogger("MLScanner")
        self.logger.info("Initializing MLScanner")
        self.model = self.load_model()
        self.feature_extractor = self.initialize_feature_extractor()
        
    def load_model(self):
        """Load or train ML model for vulnerability detection"""
        model_path = "models/aigesx_cve_model_v2.pkl"
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found at {model_path}")
            self.logger.info("Loading pre-trained model from %s", model_path)
            return joblib.load(model_path)
        except Exception as e:
            self.logger.error("Error loading ML model: %s", e)
            
    def train_new_model(self):
        """Train a new model if none exists"""
        self.logger.info("Training new RandomForest model")
        model = RandomForestClassifier(n_estimators=100)
        
        X_train = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
        y_train = np.array([0, 1, 0, 1])
        
        model.fit(X_train, y_train)
        joblib.dump(model, "models/vulnerability_model.joblib")
        self.logger.info("Model trained and saved to %s", "models/vulnerability_model.joblib")
        return model
            
    def initialize_feature_extractor(self):
        """Initialize feature extraction"""
        self.logger.info("Initializing feature extractor")
        return VulnerabilityFeatureExtractor()
        
class EnhancedMLScanner(MLScanner):
    def extract_features(self, scan_data):
        """Enhanced feature extraction"""
        features = []
        try:
            # Network features
            net_features = [
                len(scan_data.get('open_ports', [])),
                len(scan_data.get('suspicious_protocols', []))
            ]
            
            # System features
            sys_features = [
                scan_data.get('unpatched_days', 0),
                scan_data.get('weak_permission_count', 0)
            ]
            
            # Vulnerability features
            vuln_features = [
                scan_data.get('risk_score', 0),
                len(scan_data.get('critical_findings', []))
            ]
            
            return np.array([net_features + sys_features + vuln_features])
            
        except Exception as e:
            self.logger.error(f"Feature extraction error: {str(e)}")
            return None
        
    def predict_vulnerabilities(self, features):
        """Predict vulnerabilities using ML model"""
        self.logger.info("Predicting vulnerabilities using ML model")
        if not features:
            return []
        try:
            predictions = self.model.predict(features)
            return self.process_predictions(predictions)
        except Exception as e:
            self.logger.error("Error in ML prediction: %s", e)
            return []
            
    def process_predictions(self, predictions):
        """Process ML predictions into vulnerability reports"""
        self.logger.info("Processing ML predictions")
        return [
            {
                "type": "ML_DETECTION",
                "severity": "MEDIUM",
                "description": f"ML-detected potential vulnerability: {pred}",
                "confidence": 0.8
            }
            for pred in predictions if pred > 0.5
        ]

class VulnerabilityFeatureExtractor:
    def extract_features(self, scan_data):
        """Extract numerical features from scan data"""
        features = []
        try:
            if isinstance(scan_data, dict):
                features = [
                    len(scan_data.get('vulnerabilities', [])),
                    len(scan_data.get('configuration_issues', [])),
                    scan_data.get('risk_score', 0)
                ]
        except Exception as e:
            print(f"Error extracting features: {e}")
        return np.array(features).reshape(1, -1) if features else None

'''
if __name__ == "__main__":
    scanner = Scanner()
    vulnerabilities_found = scanner.scan_system()
    if vulnerabilities_found:
        print("\nDetected vulnerabilities:")
        for vuln in vulnerabilities_found:
            print(
                f"Detected CVE: {vuln['cve_id']}\nDescription: {vuln['description']}\nMatched Pattern: {vuln['matched_pattern']}\n"
            )
    else:
        print("\nNo vulnerabilities detected.")'''