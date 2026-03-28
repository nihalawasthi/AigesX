# engine/symbolic/symbolic_utils.py

import angr

def find_avoid_addresses(binary_path):
    """
    Automatically identifies addresses to avoid, such as known crash points or error-handling code.

    :param binary_path: Path to the binary.
    :return: List of addresses to avoid.
    """
    avoid_addrs = []
    project = angr.Project(binary_path, auto_load_libs=False)
    cfg = project.analyses.CFGFast()
    
    for function in cfg.functions.values():
        if any("exit" in block.disassembly_string for block in function.blocks):
            avoid_addrs.append(function.addr)

    return avoid_addrs

def identify_target_addresses(binary_path):
    """
    Identifies addresses that are potential targets, such as functions or paths likely to contain vulnerabilities.

    :param binary_path: Path to the binary.
    :return: List of target addresses.
    """
    find_addrs = []
    project = angr.Project(binary_path, auto_load_libs=False)
    cfg = project.analyses.CFGFast()

    for function in cfg.functions.values():
        if any(keyword in function.name for keyword in ["strcpy", "memcpy", "strcat", "gets"]):
            find_addrs.append(function.addr)

    return find_addrs
