# engine/fuzzing/mutators.py

import random

def simple_mutator(input_data):
    """
    A simple mutation function that modifies the input by flipping random bits.
    
    :param input_data: The input data to mutate.
    :return: The mutated input data.
    """
    mutated_data = bytearray(input_data)

    byte_index = random.randint(0, len(mutated_data) - 1)
    mutated_data[byte_index] ^= 1 << random.randint(0, 7)
    return bytes(mutated_data)
