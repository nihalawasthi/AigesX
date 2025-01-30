import sys
import os
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": [
        "os", 
        "sys",
        "json",
        "platform",
        "subprocess",
        "psycopg2",
        "win32security",
        "ntsecuritycon",
        "win32api",
        "re",
        "uuid",
        "datetime",
        "psutil",
        "wmi",
        "joblib",
        "numpy",
        "sklearn",
        "colorama",
        "tqdm",
        "matplotlib",
        "tabulate"
    ],
    "excludes": [],
    "include_files": [
        ("cve_data/cve_patterns.json", "cve_data/cve_patterns.json"),
        ("cve_data/port_service_map.json", "cve_data/port_service_map.json"),
        ("public/server.py", "public/server.py"),
        ("public/design.html", "public/design.html"),
        ("public/styles/script.js", "public/styles/script.js"),
        ("public/styles/styles.css", "public/styles/styles.css"),
        ("public/assets/", "public/assets/"),  
    ],
    "include_msvcr": True,
}

base = None
if sys.platform == "win32":
    base = "Console"

setup(
    name="AigesX",
    version="1.0",
    description="Vulnerability Scanner Tool",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="AigesX.exe",
            icon="public/assets/icon.ico",
        )
    ]
)