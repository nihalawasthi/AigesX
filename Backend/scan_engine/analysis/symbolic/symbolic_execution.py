# engine/symbolic/symbolic_execution.py

import angr
import logging

logging.getLogger('angr').setLevel(logging.CRITICAL)

def symbolic_execution(binary_path, avoid_addrs=[], find_addrs=[]):
    """
    Perform symbolic execution on the given binary to explore hard-to-reach paths.

    :param binary_path: Path to the binary to analyze.
    :param avoid_addrs: List of addresses to avoid (e.g., crash points).
    :param find_addrs: List of addresses to find (e.g., vulnerable functions).
    :return: List of paths that reached the target address.
    """
    project = angr.Project(binary_path, auto_load_libs=False)
    
    state = project.factory.entry_state()
    simgr = project.factory.simgr(state)

    for find_addr in find_addrs:
        simgr.explore(find=find_addr, avoid=avoid_addrs)

    return simgr.found
