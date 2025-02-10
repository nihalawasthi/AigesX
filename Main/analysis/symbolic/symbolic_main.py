# engine/symbolic/symbolic_main.py

from analysis.symbolic.symbolic_execution import symbolic_execution
from analysis.symbolic.symbolic_utils import find_avoid_addresses, identify_target_addresses
from analysis.symbolic.path_analysis import analyze_paths

def main(binary_path):
    """
    Main entry point to run symbolic execution on the binary and analyze paths.

    :param binary_path: Path to the binary to analyze.
    """
    avoid_addrs = find_avoid_addresses(binary_path)
    find_addrs = identify_target_addresses(binary_path)

    if not find_addrs:
        print("No potential target addresses found.")
        return
    
    symbolic_paths = symbolic_execution(binary_path, avoid_addrs=avoid_addrs, find_addrs=find_addrs)

    if symbolic_paths:
        print(f"Found {len(symbolic_paths)} paths to target addresses.")
        vulnerabilities = analyze_paths(symbolic_paths)
        print(f"Detected vulnerabilities: {vulnerabilities}")
    else:
        print("No paths found to the target addresses.")
