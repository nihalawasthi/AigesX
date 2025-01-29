#!/usr/bin/env python3

from core.scanner import Scanner, AutomatedScannerEngine, MLScanner, VulnerabilityFeatureExtractor
from core.reporter import Reporter
import os
import logging
import subprocess
import colorama
from colorama import Fore, Style
from tqdm import tqdm
import sys
from tabulate import tabulate
import time

logging.basicConfig(
    filename='aigesx.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

colorama.init()
class HackerStyle:
    spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    @staticmethod
    def print(text, end="\n"):
        sys.stdout.write(f"{Fore.GREEN}{Style.BRIGHT}{text}{Style.RESET_ALL}{end}")
        sys.stdout.flush()

    @staticmethod
    def error(text):
        sys.stdout.write(f"{Fore.RED}{Style.BRIGHT}[!] Error: {text}{Style.RESET_ALL}\n")
        sys.stdout.flush()

    @staticmethod
    def success(text):
        sys.stdout.write(f"{Fore.GREEN}{Style.BRIGHT}[+] {text}{Style.RESET_ALL}\n")
        sys.stdout.flush()

    @staticmethod
    def info(text):
        sys.stdout.write(f"{Fore.CYAN}{Style.BRIGHT}[*] {text}{Style.RESET_ALL}\n")
        sys.stdout.flush()

class ProgressBar:
    @staticmethod
    def show_progress(task_list):
        with tqdm(total=100, 
                  bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET),
                  desc="Task Progress",
                  position=0) as pbar:
            for task, weight in task_list:
                with tqdm(total=100,
                          bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET),
                          desc=f"  └─ {task}",
                          position=1,
                          leave=False) as process_bar:
                    for _ in range(100):
                        time.sleep(0.02)
                        process_bar.update(1)
                pbar.update(weight)
                time.sleep(0.1)
        sys.stdout.write("\033[A\033[K")

class ReportFormatter:
    @staticmethod
    def display_results(vulnerabilities):
        """Display vulnerabilities in a tabular format"""
        headers = ["Type", "Category", "Severity", "Description"]
        table = [
            [vuln.get("type"), vuln.get("category"), vuln.get("severity"), vuln.get("description")]
            for vuln in vulnerabilities
        ]
        formatted_table = tabulate(table, headers, tablefmt="grid", colalign=("left", "left", "center", "left"))
        HackerStyle.info("Vulnerabilities Found:")
        print(f"\n{Fore.YELLOW}{formatted_table}{Style.RESET_ALL}\n")

def scan_system():
    HackerStyle.info("Starting system scan...")
    scan_tasks = [
        ("Initializing Scanner", 10),
        ("Scanning hardware components", 25),
        ("Analyzing software vulnerabilities", 25),
        ("Scanning system configurations", 20),
        ("Checking security settings", 20)
    ]
    ProgressBar.show_progress(scan_tasks)
    
    scanner = Scanner()
    ports = scanner.perform_port_scan()
    protocol_info = scanner.analyze_protocols(ports)
    HackerStyle.info("Protocol Analysis Results:")
    for port, info in protocol_info.items():
        HackerStyle.info(f"Port {port}: {info}")
    HackerStyle.info("System scan completed.")

def perform_deep_scan():
    HackerStyle.info("Performing detailed vulnerability scan...")
    detailed_tasks = [
        ("Loading CVE data", 20),
        ("Performing advanced deep scan", 50),
        ("Running ML-based analysis", 20),
        ("Generating comprehensive report", 10)
    ]
    ProgressBar.show_progress(detailed_tasks)

def main():
    try:
        logging.getLogger('werkzeug').disabled = True

        HackerStyle.print("""
        ╔═══════════════════════════════════════╗
        ║             AigesX v1.0               ║
        ║      Vulnerability Scanner Tool       ║
        ╚═══════════════════════════════════════╝
        """)

        scan_system()

        automated_scanner = AutomatedScannerEngine()
        ml_scanner = MLScanner()
        reporter = Reporter([])

        perform_deep_scan()

        basic_vulnerabilities = Scanner().scan_system()
        deep_scan_results = automated_scanner.deep_system_scan()
        features = ml_scanner.extract_features(deep_scan_results)
        ml_predictions = ml_scanner.predict_vulnerabilities(features)

        all_vulnerabilities = basic_vulnerabilities
        if isinstance(deep_scan_results, dict):
            all_vulnerabilities.extend(deep_scan_results.get("vulnerabilities", []))
        all_vulnerabilities.extend(ml_predictions)

        ReportFormatter.display_results(all_vulnerabilities)
        reporter = Reporter(all_vulnerabilities)
        reporter.generate_detailed_report()

        HackerStyle.success("Scan completed successfully!")
        HackerStyle.info("Launching report viewer...")

        with open(os.devnull, 'w') as devnull:
            sys.stdout = devnull
            sys.stderr = devnull
            subprocess.run(["python", "public/server.py", reporter.report_name])

    except KeyboardInterrupt:
        logging.error("Scan interrupted by user")
        HackerStyle.error("Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error("Critical error: %s", str(e))
        HackerStyle.error(f"Critical error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()