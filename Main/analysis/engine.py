# engine/engine.py

from analysis.symbolic.symbolic_main import main as symbolic_main
from analysis.fuzzing.binary_fuzzing import binary_fuzzing_with_afl
from analysis.analysis.crash_analysis import detect_crash
from analysis.analysis.classification import classify_vulnerability
from analysis.analysis.cve_generation import generate_cve
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
def run_analysis(binary_path, fuzz_output_dir, afl_path='/home/morpheus/Downloads/AFLplusplus/afl-fuzz'):
    """
    Main function to run fuzzing, symbolic execution, and analyze vulnerabilities.

    :param binary_path: Path to the binary to analyze.
    :param fuzz_output_dir: Directory where fuzzing inputs and results are stored.
    :param afl_path: Path to AFL++ fuzzer executable.
    """
    print(f"Running symbolic execution on {binary_path}...")
    symbolic_main(binary_path)

    print(f"Starting AFL++ fuzzing for {binary_path}...")
    binary_fuzzing_with_afl(binary_path, afl_path, output_dir=fuzz_output_dir)

    for fuzz_input in os.listdir(fuzz_output_dir):
        input_file = os.path.join(fuzz_output_dir, fuzz_input)
        print(f"Checking for crashes on input {input_file}...")
        crash_data = detect_crash(binary_path, input_file)

        if crash_data:
            print(f"Crash detected on input {input_file}. Analyzing...")
            vulnerabilities = classify_vulnerability(crash_data)
            print(f"Classified vulnerabilities: {vulnerabilities}")
            cve_report = generate_cve(vulnerabilities, binary_path)
            print(f"CVE Report Generated: {cve_report['CVE_ID']}")
