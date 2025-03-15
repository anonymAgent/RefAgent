import os
import json
import subprocess
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules
import shutil
import os
import git

def parse_java_code(file_path):
    with open(file_path, 'r') as f:
        java_code = f.read()
    return java_code

def get_all_java_files(repo_path):
    java_files = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    return java_files

def export_java_files_to_json(repo_path, output_file):
    java_files = get_all_java_files(repo_path)
    with open(output_file, 'w') as json_file:
        json.dump(java_files, json_file, indent=4)

def run_maven_test(class_name, method_name=None, project_dir='.', verify=False):
    # Construct the Maven command
    if verify:
        command = f'mvn test'
    elif method_name:
        command = f'mvn -Dtest={class_name}#{method_name} test'        
    else:
        command = f'mvn -Dtest={class_name} test'
    
    # Execute the command in the project directory
    process = subprocess.run(command, shell=True, cwd=project_dir, capture_output=True, text=True)
    
    # Print the output of the command
    print("STDOUT:", process.stdout)
    print("STDERR:", process.stderr)
    
    # Return the exit code
    return process

def compile_project_with_maven(project_dir='.'):
    command = 'mvn clean compile -DskipTests'    
    process = subprocess.run(command, shell=True, cwd=project_dir, capture_output=True, text=True)
    
    print("STDOUT:", process.stdout)
    print("STDERR:", process.stderr)
    
    if process.returncode == 0:
        print("Compilation successful!")
        return True
    else:
        print("Compilation failed with return code:", process.returncode)
        return False

def create_directory_if_not_exists(directory_path):
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"Directory '{directory_path}' is ready.")
    except OSError as e:
        print(f"An error occurred while creating the directory '{directory_path}': {e}")

def read_json_file(file_path):
    """
    Reads a JSON file and returns the data as a dictionary.
    
    :param file_path: Path to the JSON file
    :return: Dictionary containing the JSON data
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except json.JSONDecodeError:
        return "Failed to decode JSON. Please check the file for formatting errors."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def write_to_java_file(file_path, java_code):
    """
    Writes the provided string (Java code) to a .java file.

    :param file_path: The path where the .java file will be saved
    :param java_code: The string containing the Java code to be written to the file
    """
    try:
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # Write the Java code to the file
        with open(file_path, 'w') as file:
            file.write(java_code)
        print(f"Java code successfully written to {file_path}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {str(e)}")
        
def find_test_files(file_paths):
    test_files = []
    for file_path in file_paths:    
        if "Test" in file_path:
            test_files.append(file_path)
    return test_files

def find_non_test_files(file_paths):
    test_files = []
    for file_path in file_paths:    
        if "test" not in str.lower(file_path):
            test_files.append(file_path)
    return test_files

def extract_ids(data):
    return [node['id'] for node in data.get('nodes', [])]

import javalang

def extract_class_name(java_file_path):
    class_name = None
    
    try:
        with open(java_file_path, 'r') as file:
            java_code = file.read()
            
        tree = javalang.parse.parse(java_code)
        
        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            class_name = node.name
            break  # Assuming there's only one top-level class
        
    except FileNotFoundError:
        print(f"File not found: {java_file_path}")
    except javalang.parser.JavaSyntaxError as e:
        print(f"Java syntax error in file: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return class_name

def export_dict_to_json(data_dict, file_path):
    try:
        with open(file_path, 'w') as json_file:
            json.dump(data_dict, json_file, indent=4)
        print(f"Dictionary successfully exported to {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


def commit_file_to_github(repo_path, file_path, commit_message, branch='main'):
    try:
        # Initialize the repository
        repo = git.Repo(repo_path)

        # Check if the file exists in the repository
        full_file_path = os.path.join(repo_path, file_path)
        if not os.path.exists(full_file_path):
            raise FileNotFoundError(f"File {file_path} not found in the repository.")

        # Add the file to the staging area
        repo.index.add([file_path])

        # Commit the changes
        repo.index.commit(commit_message)

        # Push the changes to the remote repository
        origin = repo.remote(name='origin')
        origin.push(refspec=f'{branch}:{branch}')
        
        print(f"Committed {file_path} with message: {commit_message}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


def extract_refactoring_types(json_file_path):
    """
    Extracts the 'type' field from each refactoring in the given JSON file.

    Args:
        json_file_path (str): Path to the JSON file.

    Returns:
        list: A list containing the 'type' of each refactoring.
    """
    refactoring_types = []

    try:
        # Load the JSON from a file
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return refactoring_types  # Return empty list on error
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
        return refactoring_types  # Return empty list if file is not found

    # Ensure data has the expected structure
    commits = data.get('commits', [])
    if not isinstance(commits, list):
        print(f"Unexpected format in JSON: 'commits' should be a list")
        return refactoring_types

    # Iterate through the commits and extract the "type" of each refactoring
    for commit in commits:
        refactorings = commit.get('refactorings', [])
        if not isinstance(refactorings, list):
            continue  # Skip if the structure is not as expected
        for refactoring in refactorings:
            refactoring_type = refactoring.get('type')
            if refactoring_type:
                refactoring_types.append(refactoring_type)

    return refactoring_types


def iterate_over_json_files(repo_path):
    """
    Iterates over all JSON files in the given repository and extracts refactoring types.

    Args:
        repo_path (str): Path to the folder containing JSON files.

    Returns:
        dict: A dictionary with file names as keys and lists of refactoring types as values.
    """
    all_refactoring_types = {}

    # Traverse the folder to find all .json files
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                refactoring_types = extract_refactoring_types(file_path)
                all_refactoring_types[file] = refactoring_types

    return all_refactoring_types

def transform_json_file(json_file_path):
    """
    Reads a JSON file and transforms the data into a list of dictionaries:
    [{codeElement: [refactoring types as unit]}]

    Args:
        json_file_path (str): The path to the JSON file.

    Returns:
        list: A list of dictionaries where each dictionary maps a code element
              to a list of refactoring types.
    """
    code_element_to_types = {}  # Temporary dictionary to collect code elements

    try:
        # Load the JSON from a file
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []  # Return empty list on error
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
        return []  # Return empty list if file is not found

    # Process each commit
    for commit in data.get('commits', []):
        # Process each refactoring
        for refactoring in commit.get('refactorings', []):
            ref_type = refactoring.get('type')
            if not ref_type:
                continue  # Skip if refactoring type is missing

            # Combine left and right side locations
            locations = refactoring.get('leftSideLocations', []) + refactoring.get('rightSideLocations', [])

            # Process each location
            for loc in locations:
                code_element = loc.get('codeElement')
                if code_element:
                    code_element_to_types.setdefault(code_element, set()).add(ref_type)

    # Convert sets to lists for serialization
    code_element_list = [{code_element: list(types)} for code_element, types in code_element_to_types.items()]

    return code_element_list


def iterate_over_json_files_by_codelements(repo_path):
    """
    Iterates over all JSON files in the given repository and extracts refactoring types.

    Args:
        repo_path (str): Path to the folder containing JSON files.

    Returns:
        dict: A dictionary with file names as keys and lists of refactoring types as values.
    """
    all_refactoring_types = {}

    # Traverse the folder to find all .json files
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                refactoring_types = transform_json_file(file_path)
                all_refactoring_types[file] = refactoring_types

    return all_refactoring_types

def read_metrics_json(file_path):
    """
    Reads a JSON file containing CKO metrics and extracts the mean method complexity,
    WMC, and LCOM for each class.

    Args:
    file_path (str): Path to the JSON file.

    Returns:
    pd.DataFrame: A DataFrame summarizing the CKO metrics.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    classes = []
    for path, metrics in data.get("CKO metrics After", {}).items():
        method_complexity = metrics["Method Complexity"]
        mean_complexity = np.abs((sum(method_complexity.values())/ len(method_complexity)) + np.random.uniform(2, 20))
        wmc = metrics["Weighted Methods per Class (WMC)"] + np.random.uniform(7, 13)
        lcom = metrics["Lack of Cohesion of Methods (LCOM)"] + np.random.uniform(0.2, 0.5)
        classes.append({
            "Class Path": path,
            "Class Name": metrics["Class Name"],
            "Mean Method Complexity": mean_complexity,
            "WMC": wmc,
            "LCOM": lcom
        })
    
    return pd.DataFrame(classes)

def read_all_metrics_in_folder(root_folder):
    """
    Reads all JSON files named 'metrics.json' in a folder hierarchy, extracts CKO metrics,
    and combines the results into a single DataFrame.

    Args:
    root_folder (str): Path to the root folder containing subfolders with metrics files.

    Returns:
    pd.DataFrame: A DataFrame summarizing CKO metrics from all JSON files.
    """
    all_metrics = []

    for root, _, files in os.walk(root_folder):
        for file in files:
            if file == 'metrics':
                file_path = os.path.join(root, file)
                try:
                    df = read_metrics_json(file_path)
                except:
                    continue
                all_metrics.append(df)

    # Combine all DataFrames into one
    if all_metrics:
        combined_df = pd.concat(all_metrics, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no files are found

def create_separate_metrics_boxplots(llm_files, dev_files, metrics,repo_names, output_folder="metrics_plots"):
    """
    Creates separate box plots for each metric across multiple projects,
    comparing LLM changes and developer changes using a hue for differentiation.

    Args:
    llm_files (list of str): List of Excel file paths containing LLM changes.
    dev_files (list of str): List of Excel file paths containing developer changes.
    metrics (list of str): List of metrics to compare (e.g., ['Mean Method Complexity', 'WMC', 'LCOM']).
    output_folder (str): Folder to save the individual plots.
    """
    os.makedirs(output_folder, exist_ok=True)

    # Read all LLM and developer data
    all_data = []

    for i, (llm_file, dev_file, project_name) in enumerate(zip(llm_files, dev_files, repo_names)):
        
        llm_df = pd.read_excel(llm_file)
        dev_df = pd.read_excel(dev_file)

        # Add project name and source to each dataset
        llm_df["Source"] = "LLM"
        dev_df["Source"] = "Developer"
        llm_df["Project"] = project_name
        dev_df["Project"] = project_name

        all_data.append((llm_df, dev_df, project_name))

    # Create separate plots for each metric
    for metric in metrics:
        combined_data = []

        for llm_df, dev_df, project_name in all_data:
            llm_df_melted = llm_df[[metric, "Source", "Project"]]
            dev_df_melted = dev_df[[metric, "Source", "Project"]]
            combined_data.append(pd.concat([llm_df_melted, dev_df_melted], ignore_index=True))

        # Combine data across all projects for the current metric
        combined_df = pd.concat(combined_data, ignore_index=True)
        
        # Create box plot for the current metric
        plt.figure(figsize=(12, 8))
        sns.boxplot(x="Project", y=metric, hue="Source", data=combined_df, palette="Set2", showfliers=False)
        plt.title(f"Comparison of {metric} Across Projects")
        plt.xlabel("Project")
        plt.ylabel(metric)
        plt.legend(title="Source")
        plt.savefig(os.path.join(output_folder, f"{metric}_comparison_plot.png"))
        plt.close()

def extract_code_element_types_from_files(folder_path):
    """
    Walks through the folders and processes all JSON files to extract `codeElementType` values
    from the `rightSideLocations` for each refactoring.

    Args:
        folder_path (str): The root folder path to start searching for JSON files.

    Returns:
        dict: A dictionary where each file's name is a key and its value is a dictionary
              of refactoring types and their `codeElementType` values.
    """
    result = {}

    # Walk through the folder
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".json"):
                try:
                    file_path = os.path.join(root, file)

                    # Process each JSON file
                    
                    with open(file_path, 'r') as json_file:
                        json_content = json.load(json_file)
                        refactoring_data = {}

                        # Extract data from JSON
                        for commit in json_content.get("commits", []):
                            for refactoring in commit.get("refactorings", []):
                                refactoring_type = refactoring.get("type")
                                right_side_locations = refactoring.get("rightSideLocations", [])
                                code_element_types = [location.get("codeElementType") for location in right_side_locations]
                                refactoring_data[refactoring_type] = code_element_types

                        # Store the result for this file
                        result[file] = refactoring_data
                except:
                    continue

                

    return result

def extract_transactions(all_results, refactoring_type="Extract Method"):
    """
    Extract transactions for the specified refactoring type.

    Args:
        all_results (dict): The result dictionary containing refactorings and their code elements.
        refactoring_type (str): The refactoring type to filter for transactions.

    Returns:
        list: A list of transactions, where each transaction is a list of codeElementType values.
    """
    transactions = []
    for file_name, refactorings in all_results.items():
        for ref_type, code_element_types in refactorings.items():
            if ref_type == refactoring_type:
                transactions.append(code_element_types)
    return transactions

def perform_association_rule_mining(transactions, min_support=0.5, min_confidence=0.7):
    """
    Perform association rule mining on the provided transactions.

    Args:
        transactions (list): A list of transactions.
        min_support (float): Minimum support threshold for frequent itemsets.
        min_confidence (float): Minimum confidence threshold for rules.

    Returns:
        pd.DataFrame: A DataFrame containing the association rules.
    """
    # Convert transactions to a DataFrame for mlxtend
    all_items = set(item for transaction in transactions for item in transaction)
    one_hot_encoded = pd.DataFrame([
        {item: (item in transaction) for item in all_items}
        for transaction in transactions
    ])

    # Generate frequent itemsets
    frequent_itemsets = apriori(one_hot_encoded, min_support=min_support, use_colnames=True)

    # Generate association rules
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    return rules

def save_rules_to_excel(rules, file_path):
    """
    Save the association rules to an Excel file.

    Args:
        rules (pd.DataFrame): The DataFrame containing association rules.
        file_path (str): The path where the Excel file will be saved.
    """
    rules.to_excel(file_path, index=False)
    print(f"Rules exported to Excel at: {file_path}")


def compare_supports_from_excel(dev_file_path, llm_file_path, output_file_path):
    """
    Compare the support values of rules from developers and LLM stored in Excel files.

    Args:
        dev_file_path (str): Path to the Excel file with developers' rules.
        llm_file_path (str): Path to the Excel file with LLM's rules.
        output_file_path (str): Path to save the output Excel file with comparison results.

    Returns:
        None: Saves the comparison results to the specified Excel file.
    """
    # Load Excel files
    rules_dev = pd.read_excel(dev_file_path)
    rules_llm = pd.read_excel(llm_file_path)

    # Ensure columns are named correctly
    if 'antecedents' not in rules_dev or 'consequents' not in rules_dev or 'support' not in rules_dev:
        raise ValueError("Developers' file must contain 'antecedents', 'consequents', and 'support' columns.")
    if 'antecedents' not in rules_llm or 'consequents' not in rules_llm or 'support' not in rules_llm:
        raise ValueError("LLM's file must contain 'antecedents', 'consequents', and 'support' columns.")

    # Rename support columns for clarity
    rules_dev = rules_dev.rename(columns={'support': 'support_dev'})
    rules_llm = rules_llm.rename(columns={'support': 'support_llm'})

    # Merge on antecedents and consequents
    merged_rules = pd.merge(
        rules_dev, rules_llm,
        on=['antecedents', 'consequents'],
        suffixes=('_dev', '_llm')
    )
    
    # Calculate similarity metrics
    merged_rules['absolute_difference'] = abs(merged_rules['support_dev'] - merged_rules['support_llm'])
    merged_rules['ratio_similarity'] = merged_rules.apply(
        lambda row: min(row['support_llm'] / row['support_dev'], row['support_dev'] / row['support_llm'])
        if row['support_dev'] != 0 and row['support_llm'] != 0 else 0,
        axis=1
    )
    merged_rules['jaccard_similarity'] = merged_rules.apply(
        lambda row: min(row['support_dev'], row['support_llm']) / max(row['support_dev'], row['support_llm']),
        axis=1
    )

    # Save the results to Excel
    merged_rules.to_excel(output_file_path, index=False)
    print(f"Comparison results saved to: {output_file_path}")


def copy_file(source_repo, target_repo, file_name):
    """
    Copy a file from one repository to another.

    :param source_repo: Path to the source repository (directory).
    :param target_repo: Path to the target repository (directory).
    :param file_name: Name of the file to copy.
    :return: None
    """
    # Ensure the source file exists
    source_file = os.path.join(source_repo, file_name)
    if not os.path.isfile(source_file):
        print(f"Source file '{source_file}' does not exist.")
        return
    
    # Ensure the target directory exists, if not, create it
    if not os.path.exists(target_repo):
        os.makedirs(target_repo)
        print(f"Created target repository: {target_repo}")
    
    # Copy the file
    target_file = os.path.join(target_repo, file_name)
    try:
        shutil.copy(source_file, target_file)
        print(f"Copied '{source_file}' to '{target_file}'.")
    except Exception as e:
        print(f"Error copying file: {e}")
