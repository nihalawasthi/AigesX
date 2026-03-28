# engine/fuzzing/fuzz_utils.py

import os

def create_seed_file(input_data, output_dir='./afl_inputs'):
    """
    Creates a seed file for AFL++ or other fuzzers.

    :param input_data: Data to write into the seed file.
    :param output_dir: Directory to save the seed file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    seed_file_path = os.path.join(output_dir, 'seed')
    with open(seed_file_path, 'wb') as f:
        f.write(input_data)
    
    print(f"Seed file created at: {seed_file_path}")
