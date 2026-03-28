# engine/fuzzing/binary_fuzzing.py

import subprocess
import os
from analysis.fuzzing.mutators import simple_mutator

def binary_fuzzing_with_afl(binary_path, afl_path='/home/morpheus/Downloads/AFLplusplus/afl-fuzz', timeout=5, output_dir='./fuzz_outputs'):
    """
    Perform direct binary fuzzing by mutating inputs and using AFL++ for fuzzing, through WSL.
    
    :param binary_path: Path to the binary to fuzz.
    :param afl_path: Path to AFL++ binary executable inside WSL.
    :param timeout: Timeout for each fuzzing iteration (in seconds).
    :param output_dir: Directory to store fuzzing inputs and results.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    seed_input = b"A" * 100

    for i in range(100):
        mutated_input = simple_mutator(seed_input)

        input_file = os.path.join(output_dir, f'fuzz_input_{i}.bin')
        with open(input_file, 'wb') as f:
            f.write(mutated_input)

        print(f"Fuzzing iteration {i} with input saved to {input_file}")

        afl_command = [
            "wsl",
            afl_path,
            '-i', input_file,
            '-o', output_dir,
            '--', binary_path
        ]
        try:
            result = subprocess.run(afl_command, timeout=timeout, capture_output=True)
            print(f"Output: {result.stdout.decode('utf-8', errors='ignore')}")
        except subprocess.TimeoutExpired:
            print(f"Timeout on input {i}.")
        except Exception as e:
            print(f"Crash detected on input {i}: {e}")
