import os
from utilities import (iterate_over_json_files, 
                       iterate_over_json_files_by_codelements,
                       read_all_metrics_in_folder, 
                       create_separate_metrics_boxplots,
                       extract_code_element_types_from_files,
                       extract_transactions,
                       perform_association_rule_mining,
                       save_rules_to_excel,
                       compare_supports_from_excel)
from collections import Counter
import numpy as np
import pandas as pd
import seaborn as sns
from collections import Counter
from refAgent.metrics import *
import matplotlib.pyplot as plt

def count_folders_in_directory(directory_path):
    try:
        # List all entries in the directory
        entries = os.listdir(directory_path)
        
        # Filter out entries that are directories
        folders = [entry for entry in entries if os.path.isdir(os.path.join(directory_path, entry))]
        
        # Return the number of directories
        return len(folders)
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0

def create_cooccurrence_matrix(all_types):
    """
    Creates a co-occurrence matrix of refactoring types across all files.
    
    Args:
        all_types (dict): A dictionary with file names as keys and lists of refactoring types as values.

    Returns:
        pd.DataFrame: A co-occurrence matrix of refactoring types.
    """
    # Get all unique refactoring types
    unique_refactoring_types = set()
    for types in all_types.values():
        unique_refactoring_types.update(set(types))
    unique_refactoring_types = sorted(unique_refactoring_types)  # Sort for consistent ordering

    # Create an empty DataFrame for the co-occurrence matrix
    cooccurrence_matrix = pd.DataFrame(0, index=unique_refactoring_types, columns=unique_refactoring_types)

    # Fill in the co-occurrence matrix
    for types in all_types.values():
        unique_types_in_file = set(types)  # Remove duplicate refactoring types in the same file
        for ref_type_1 in unique_types_in_file:
            for ref_type_2 in unique_types_in_file:
                cooccurrence_matrix.loc[ref_type_1, ref_type_2] += 1

    return cooccurrence_matrix
# Example usage:
directory_path = 'results/javaxpath'
num_folders = count_folders_in_directory(directory_path)
print(f"Number of classes tested in javaxpath: {num_folders}")
# Example usage:
directory_path = 'results/gson'
num_folders = count_folders_in_directory(directory_path)
print(f"Number of classes tested in gson: {num_folders}")
# Example usage:
directory_path = 'results/closure-templates'
num_folders = count_folders_in_directory(directory_path)
print(f"Number of classes tested in closure: {num_folders}")
print("================================================================")

import matplotlib.pyplot as plt

# Data for the three projects
iterations = list(range(1, 20))
javax_avg_cc = [3.9, 3.82, 3.82, 3.7, 3.6, 3.65, 3.64, 3.67, 3.66, 3.54, 3.53, 3.48, 3.41, 3.41, 3.41, 3.41, 3.41, 3.41, 3.41]
gson_avg_cc = [5.3, 5.82, 5.42, 5.23, 5.3, 5.1, 5, 4.67, 4.66, 4.6, 4.6, 4.6, 4.6, 4.6, 4.6, 4.6001, 4.6001, 4.6, 4.6]
closure_avg_cc = [2.83, 2.82, 2.42, 2.22, 2.2, 2.2, 2.2, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1]

# Plot for javax
plt.figure(figsize=(10, 4))

plt.subplot(1, 3, 1)
plt.plot(iterations, javax_avg_cc, label="javax")
plt.xlabel('iteration')
plt.ylabel('avg CC')
plt.title('javax')

# Plot for gson
plt.subplot(1, 3, 2)
plt.plot(iterations, gson_avg_cc, label="gson")
plt.xlabel('iteration')
plt.ylabel('avg CC')
plt.title('gson')

# Plot for closure
plt.subplot(1, 3, 3)
plt.plot(iterations, closure_avg_cc, label="closure")
plt.xlabel('iteration')
plt.ylabel('avg CC')
plt.title('closure')

plt.tight_layout()
plt.show()

# New data for avg_WMC (Weighted Methods per Class)
javax_avg_wmc = [6, 6, 6.22, 6.2, 6.6, 6.65, 6.64, 7.67, 7.66, 7.54, 7.53, 7.48, 7.41, 8.41, 8.45, 8.41, 8.49, 8.49, 8.49]
gson_avg_wmc = [8.3, 8.82, 9.42, 9.23, 9.3, 9.3, 9, 9.67, 9.66, 10.6, 10, 10, 10.6, 10.6, 12, 12, 12, 12, 12]
closure_avg_wmc = [4.83, 4.82, 5.42, 5.22, 5.2, 5.2, 5.2, 6.1, 6.1, 6.1, 6.1, 6.1, 6.1, 6.1, 6.1, 6.1, 6.1, 6.1, 6.1]

# Plot for javax WMC
plt.figure(figsize=(10, 4))

plt.subplot(1, 3, 1)
plt.plot(iterations, javax_avg_wmc, label="javax")
plt.xlabel('iteration')
plt.ylabel('avg WMC')
plt.title('javax')

# Plot for gson WMC
plt.subplot(1, 3, 2)
plt.plot(iterations, gson_avg_wmc, label="gson")
plt.xlabel('iteration')
plt.ylabel('avg WMC')
plt.title('gson')

# Plot for closure WMC
plt.subplot(1, 3, 3)
plt.plot(iterations, closure_avg_wmc, label="closure")
plt.xlabel('iteration')
plt.ylabel('avg WMC')
plt.title('closure')

plt.tight_layout()
plt.show()

repo_names = ["closure-templates-release-2023-09-13", 
             "gson-gson-parent-2.10.1",
             "javaxpath"]
refactoring_types = set()
import sys
for repo_name in repo_names:

    #Refactoring analysis
    repo_path = f'data/refactoring_types/{repo_name}'  # Replace with the path to your repository containing JSON files
    all_types = iterate_over_json_files(repo_path)
    all_type_by_elements = iterate_over_json_files_by_codelements(repo_path)

    # Count the number of files with and without refactorings
    non_empty_count = sum(1 for types in all_types.values() if types)  # Files with refactorings
    empty_count = sum(1 for types in all_types.values() if not types)  # Files without refactorings

    # Plot the histogram
    labels = ['With Refactorings', 'Without Refactorings']
    counts = [non_empty_count, empty_count]

    plt.bar(labels, counts, color=['#AEC6CF', '#FFB347'])
    plt.xlabel('Refactoring Presence')
    plt.ylabel('Number of Files')
    plt.title(f'Histogram of Files with and without Refactorings {repo_name}')
    plt.savefig(f'Histogram_of_Files_with_and_without_Refactorings_{repo_name}.png')
    plt.show()

    #Plots a histogram showing how many files have more than one unique refactoring type.
    # Count the number of files with more than one unique refactoring type
    composite_count = 0
    single_count = 0

    for code_element, types in all_type_by_elements.items():
        print(types)
        if len(types) ==0:
            continue
        for type in types:
            for element in type.values():
                unique_types = set(element)
                print(unique_types)
                if len(unique_types) > 1:
                    composite_count += 1
                else:
                    single_count += 1
    # Plot the histogram
    labels = ['Composite Refactorings', 'Single']
    counts = [composite_count, single_count]
    pastel_colors = ['#77DD77', '#FF6961']  # Soft pastel green and pastel red

    plt.bar(labels, counts, color=pastel_colors)
    plt.xlabel('Refactoring Types')
    plt.ylabel('Number of Files')
    plt.title(f'Histogram of Files with Composite vs Single Refactorings {repo_name}')
    plt.savefig(f'Histogram_of_Files_with_Composite_vs_Single_Refactorings_{repo_name}.png')

    plt.show()

    #Identifies unique refactoring types across all files and counts how many times each type appears.
    refactoring_counter = Counter()

    # Iterate over each file's refactoring types
    for types in all_types.values():
        # Remove duplicates by converting the list to a set
        unique_types = set(types)
        refactoring_types.update(unique_types)
        # Update the counter with the unique refactoring types
        refactoring_counter.update(unique_types)

    # Convert the counter to a dictionary
    unique_refactoring_counts = dict(refactoring_counter)

    # Plotting
    types = list(unique_refactoring_counts.keys())
    counts = list(unique_refactoring_counts.values())

    plt.figure(figsize=(10, 6))  # Set the figure size
    plt.bar(types, counts, color='#76C1FA')  # Use a pastel blue color

    plt.xlabel('Refactoring Type')
    plt.ylabel('Count')
    plt.title(f'Unique Refactoring Types and Their Counts {repo_name}')
    plt.xticks(rotation=45, ha='right')  # Rotate the x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    plt.savefig(f'Unique_Refactoring_Types_and_Their_Counts_{repo_name}.png')
    plt.show()


    # #Creates a co-occurrence matrix of refactoring types across all files.
    # cooccurrence_matrix = create_cooccurrence_matrix(all_types)
    # plt.figure(figsize=(10, 8))
    # sns.heatmap(cooccurrence_matrix, annot=True, cmap='Blues', fmt='d')
    # plt.title('Co-occurrence Heatmap of Refactoring Types')
    # plt.xlabel('Refactoring Type')
    # plt.ylabel('Refactoring Type')
    # plt.xticks(rotation=45, ha='right')
    # plt.yticks(rotation=0)
    # plt.tight_layout()
    # plt.show()

repo_names = ["closure-templates-release-2023-09-13", 
             "gson-gson-parent-2.10.1"]

repo_dev = ["closure-templates", "gson"]
print("======================================")
print("Compute F1-score, Precision and Recall")
for repo, repo_llm in zip(repo_dev, repo_names):
    # Example usage
    llm_json = f'refactoring_results/{repo_llm}_refactorings_output.json'
    dev_json = f'refactoring_results/developers/{repo}_refactorings_output.json'

    precision, recall, total_overlap, overlap_details = compute_precision_recall(llm_json, 
                                                                                 dev_json, 
                                                                                 refactoring_types)

    

# Set width of bars
bar_width = 0.25

# Set positions of bars on the x-axis
r1 = np.arange(len(projects))
r2 = [x + bar_width for x in r1]
r3 = [x + bar_width for x in r2]

# Create subplots
plt.figure(figsize=(10, 6))

# Create bars
plt.bar(r1, precisions, color='#AEC6CF', width=bar_width, edgecolor='grey', label='Precision')
plt.bar(r2, recalls, color='#FFB347', width=bar_width, edgecolor='grey', label='Recall')
plt.bar(r3, f1_scores, color='#77DD77', width=bar_width, edgecolor='grey', label='F1-Score')

# Add labels and title
plt.xlabel('Projects', fontweight='bold')
plt.xticks([r + bar_width for r in range(len(projects))], projects)
plt.ylabel('Scores', fontweight='bold')
plt.title('Precision, Recall, and F1-Score for Three Projects')

# Add a legend
plt.legend()

# Show the plot
plt.savefig("metrics.png")
plt.show()

repo_names = []

for repo in repo_names:
    combined_df = read_all_metrics_in_folder(f'results/{repo}')
    combined_df.to_excel(f"results/metrics_summary/developers_{repo}_metrics.xlsx")


# Example usage:
dev_files = [f"results/metrics_summary/developers_{repo}_metrics.xlsx" for repo in repo_names]
llm_files = [f"results/metrics_summary/LLM_{repo}_metrics.xlsx" for repo in repo_names]
metrics = ["Mean Method Complexity", "WMC", "LCOM"]
create_separate_metrics_boxplots(llm_files, dev_files, metrics, repo_names)

# Example usage
folder_path = "data/refactoring_types/agents"  # Replace with the path to the folder containing JSON files
all_results = extract_code_element_types_from_files(folder_path)
# Print results
transactions = extract_transactions(all_results)
rules = perform_association_rule_mining(transactions, min_support=0.6, min_confidence=0.7)

print(rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']])

# Save the rules to an Excel file
output_file = "results/LLM_association_rules.xlsx"
save_rules_to_excel(rules, output_file)

# Example usage
dev_file_path = "results/LLM_association_rules.xlsx"  # Path to developers' rules Excel file
llm_file_path = "results/developers_association_rules.xlsx"         # Path to LLM's rules Excel file
output_file_path = "comparison_results.xlsx"  # Path to save the comparison results

compare_supports_from_excel(dev_file_path, llm_file_path, output_file_path)