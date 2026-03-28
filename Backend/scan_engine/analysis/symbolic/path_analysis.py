# engine/symbolic/path_analysis.py

import re

def analyze_paths(symbolic_paths):
    """
    Analyze the symbolic execution paths to classify vulnerabilities.

    :param symbolic_paths: List of symbolic paths from the symbolic execution.
    :return: List of detected vulnerabilities.
    """
    vulnerabilities = []

    for path in symbolic_paths:
        if is_vulnerable(path):
            vulnerabilities.append({'path': path, 'vulnerability': 'buffer overflow'})
        elif is_use_after_free(path):
            vulnerabilities.append({'path': path, 'vulnerability': 'use-after-free'})
        elif is_integer_overflow(path):
            vulnerabilities.append({'path': path, 'vulnerability': 'integer overflow'})

    return vulnerabilities


def is_vulnerable(path):
    """
    Check for buffer overflow vulnerability in the symbolic path.

    :param path: A symbolic execution path.
    :return: Boolean indicating whether the path contains a buffer overflow vulnerability.
    """
    input_data = path.posix.dumps(0).decode("utf-8", errors="ignore")
    
    if "gets" in input_data or "strcpy" in input_data or "memcpy" in input_data:
        return True
    if len(input_data) > 100:
        return True
    return False


def is_use_after_free(path):
    """
    Check for use-after-free vulnerability in the symbolic path.

    :param path: A symbolic execution path.
    :return: Boolean indicating whether the path contains a use-after-free vulnerability.
    """
    memory_operations = path.posix.dumps(0).decode("utf-8", errors="ignore")
    if re.search(r'free\((.*)\)', memory_operations):
        if re.search(r'\1', memory_operations):
            return True
    return False


def is_integer_overflow(path):
    """
    Check for integer overflow vulnerability in the symbolic path.

    :param path: A symbolic execution path.
    :return: Boolean indicating whether the path contains an integer overflow vulnerability.
    """
    input_data = path.posix.dumps(0).decode("utf-8", errors="ignore")
    if re.search(r'\d+\s*\+\s*\d+', input_data) or re.search(r'\d+\s*\*\s*\d+', input_data):
        return True
    return False
