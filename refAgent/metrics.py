import json

# Example data for three projects
projects = ['closure-templates', 'gson', 'JxPath']
precisions = [0.67, 0.78, 0.76]
recalls = [0.82, 0.75, 0.80]
f1_scores = [0.73744966, 0.76470588, 0.77948718]

def load_json_from_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def find_matching_changes(llm_changes, dev_changes, valid_refactoring_types):
    total_overlap = 0
    overlap_details = []

    # Loop over LLM changes and check if there is a matching developer change
    for llm_change in llm_changes:
        llm_file = llm_change['file']
        llm_type = llm_change['type']
        llm_start = llm_change['startLine']
        llm_end = llm_change['endLine']

        # Loop over developer changes to find matching file and refactoring
        for dev_change in dev_changes:
            dev_file = dev_change['file']
            dev_type = dev_change['type']
            dev_start = dev_change['startLine']
            dev_end = dev_change['endLine']

            # Check if developer's refactoring type is in the valid refactoring types list
            if dev_type not in valid_refactoring_types:
                continue  # Skip if the developer's refactoring type is not in the list

            # Check if the files match and the refactoring type is the same
            if llm_file == dev_file and llm_type == dev_type:
                # Check if LLM's start line overlaps with the developer's range
                if llm_start and dev_start and llm_end and dev_end:
                    if dev_start <= llm_start <= dev_end:
                        total_overlap += 1
                        overlap_details.append({
                            'file': llm_file,
                            'refactoring_type': llm_type,
                            'llm_startLine': llm_start,
                            'llm_endLine': llm_end,
                            'dev_startLine': dev_start,
                            'dev_endLine': dev_end
                        })
    
    return total_overlap, overlap_details

def compute_precision_recall(llm_json, dev_json, valid_refactoring_types):
    # Parse the JSON contents
    llm_changes = load_json_from_file(llm_json)
    dev_changes = load_json_from_file(dev_json)

    # Track unique files with refactorings for LLM and developers
    llm_refactoring_files = set()
    dev_refactoring_files = set()

    # Count unique files with refactorings for LLM
    for change in llm_changes:
        if change['type'] != "No Refactoring":
            llm_refactoring_files.add(change['file'])

    # Count unique files with refactorings for developers
    for change in dev_changes:
        if change['type'] in valid_refactoring_types and change['type'] != "No Refactoring":
            dev_refactoring_files.add(change['file'])

    # Ensure dev_refactoring_files must be in llm_refactoring_files
    dev_refactoring_files &= llm_refactoring_files  # Intersection of sets
    # Calculate total unique refactorings based on unique files
    total_llm_refactorings = len(llm_refactoring_files)
    total_dev_refactorings = len(dev_refactoring_files)

    # Find matching changes (overlap)
    total_overlap, overlap_details = find_matching_changes(llm_changes, dev_changes, valid_refactoring_types)

    # Compute precision and recall
    precision = total_overlap / total_llm_refactorings if total_llm_refactorings > 0 else 0
    recall = total_overlap / total_dev_refactorings if total_dev_refactorings > 0 else 0

    return precision, recall, total_overlap, overlap_details

