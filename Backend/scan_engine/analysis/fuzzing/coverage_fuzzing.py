# engine/fuzzing/coverage_fuzzing.py

import subprocess
import os

def coverage_based_fuzzing(binary_path, afl_path='/home/morpheus/Downloads/AFLplusplus/afl-fuzz', input_dir='./afl_inputs', output_dir='./afl_outputs'):
    """
    Automate AFL++ fuzzing for the target binary through WSL.

    :param binary_path: Path to the binary to fuzz.
    :param afl_path: Path to AFL++ fuzzer executable inside WSL.
    :param input_dir: Directory containing seed files for AFL++.
    :param output_dir: Directory to store AFL++ output (fuzzing results).
    """
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        with open(os.path.join(input_dir, 'seed'), 'wb') as f:
            f.write(b"A" * 100)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    afl_command = [
        "wsl",
        afl_path,
        '-i', input_dir,
        '-o', output_dir,
        '--', binary_path
    ]

    print(f"Starting AFL++ fuzzing on {binary_path}...")
    subprocess.run(afl_command)
