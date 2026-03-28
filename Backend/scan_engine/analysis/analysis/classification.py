# engine/analysis/classification.py

def classify_vulnerability(crash_data):
    """
    Classifies vulnerabilities based on the crash data.

    :param crash_data: Raw crash data or symbolic execution output.
    :return: A dictionary with the vulnerability type and description.
    """
    vulnerabilities = []

    # Example: Check for common vulnerabilities based on patterns in crash data
    if "segmentation fault" in crash_data:
        vulnerabilities.append({
            'type': 'Segmentation Fault',
            'description': 'Buffer overflow or illegal memory access.'
        })
    elif "use-after-free" in crash_data:
        vulnerabilities.append({
            'type': 'Use After Free',
            'description': 'Memory access after freeing it.'
        })
    elif "integer overflow" in crash_data:
        vulnerabilities.append({
            'type': 'Integer Overflow',
            'description': 'Overflowed integer value leading to unexpected behavior.'
        })
    else:
        vulnerabilities.append({
            'type': 'Unknown Vulnerability',
            'description': 'Unable to classify the vulnerability based on the crash data.'
        })

    return vulnerabilities
