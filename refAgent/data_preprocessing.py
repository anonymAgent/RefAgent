import json
import os

def extract_refactorings_from_json(file_path):
    refactorings_info = []
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        has_refactoring = False
        
        for commit in data.get('commits', []):
            for refactoring in commit.get('refactorings', []):
                has_refactoring = True
                refactoring_type = refactoring.get('type', 'Unknown')
                
                # Extract left and right side locations
                for side in ['leftSideLocations', 'rightSideLocations']:
                    for location in refactoring.get(side, []):
                        file_path_from_json = location.get('filePath', 'Unknown')
                        code_element = location.get('codeElement', 'Unknown')
                        start_line = location.get('startLine', 'Unknown')
                        end_line = location.get('endLine', 'Unknown')
                        
                        refactorings_info.append({
                            'file': file_path_from_json,
                            'type': refactoring_type,
                            'codeElement': code_element,
                            'startLine': start_line,
                            'endLine': end_line
                        })
        
        # If no refactorings found, add an entry indicating "no refactoring"
        if not has_refactoring:
            refactorings_info.append({
                'file': file_path,  # This would still be the external file path in case of no refactoring
                'type': 'No Refactoring',
                'codeElement': None,
                'startLine': None,
                'endLine': None
            })
    
    except json.decoder.JSONDecodeError:
        # If JSON decoding fails, it is treated as "no refactoring"
        refactorings_info.append({
            'file': file_path,
            'type': 'No Refactoring (Invalid JSON)',
            'codeElement': None,
            'startLine': None,
            'endLine': None
        })
    
    return refactorings_info

def process_json_files_in_directory(directory_path):
    all_refactorings = []
    
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(directory_path, file_name)
            refactorings_info = extract_refactorings_from_json(file_path)
            all_refactorings.extend(refactorings_info)
    
    return all_refactorings

def export_to_json(refactorings_data, output_file):
    with open(output_file, 'w') as jsonfile:
        json.dump(refactorings_data, jsonfile, indent=4)

# Example usage
project_name= "gson"
directory_path = f'data/refactoring_types/developers/{project_name}'
output_file = f'refactoring_results/developers/{project_name}_refactorings_output.json'
refactorings_data = process_json_files_in_directory(directory_path)


# Export the data to JSON
export_to_json(refactorings_data, output_file)

print(f"Data has been exported to {output_file}")