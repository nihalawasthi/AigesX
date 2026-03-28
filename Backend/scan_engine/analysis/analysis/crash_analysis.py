# engine/analysis/crash_analysis.py

import subprocess
import logging

def detect_crash(binary_path, input_file, timeout=5):
    """
    Executes the binary with the given input file and detects crashes or abnormal terminations.
    
    :param binary_path: Path to the binary to fuzz.
    :param input_file: Path to the input file that triggers the crash.
    :param timeout: Timeout for execution in seconds.
    :return: None if no crash detected, else returns crash details.
    """
    try:
        result = subprocess.run([binary_path], input=open(input_file, 'rb').read(), timeout=timeout, capture_output=True)
        if result.returncode != 0:  # Non-zero exit indicates crash or error
            logging.error(f"Crash detected on input {input_file}. Return code: {result.returncode}")
            return result.stderr.decode('utf-8', errors='ignore')
        return None  # No crash detected
    except subprocess.TimeoutExpired:
        logging.warning(f"Timeout expired for {input_file}.")
    except Exception as e:
        logging.error(f"Error when running {binary_path} with input {input_file}: {e}")
        return str(e)
    
    return None
