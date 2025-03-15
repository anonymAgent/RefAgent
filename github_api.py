import requests
import random
import json
import subprocess
import os
from utilities import *
from tqdm import tqdm  # Import tqdm for the progress bar

class GitHubAPI:
    def __init__(self, tokens):
        """
        Initialize the GitHubAPI class with a list of tokens.
        
        :param tokens: List of GitHub API tokens
        """
        self.tokens = tokens
        self.token = None

    def set_random_token(self):
        """
        Set a random token from the list of tokens.
        """
        self.token = random.choice(self.tokens)

    def get_commit_ids(self, repo_owner, repo_name, per_page=30, since=None, until=None, file_path=None):
        """
        Retrieve the list of commit IDs from a given repository, with optional date filtering.
        
        :param repo_owner: GitHub username or organization name of the repository owner
        :param repo_name: Name of the repository
        :param per_page: Number of commits per page (default is 30)
        :param since: ISO 8601 date string (YYYY-MM-DDTHH:MM:SSZ) to get commits after this date (inclusive)
        :param until: ISO 8601 date string (YYYY-MM-DDTHH:MM:SSZ) to get commits before this date (inclusive)
        :return: List of commit IDs
        """
        commit_ids = []
        page = 1  # Start with the first page

        while True:
            # Set a new random token for each page request
            self.set_random_token()

            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json',
            }
            
            # Construct the URL with page, since, and until parameters
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits?page={page}&per_page={per_page}"
            if since:
                url += f"&since={since}"
            if until:
                url += f"&until={until}"
            if file_path:
                url += f"&path={file_path}"
            
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                commits = response.json()

                if not commits:
                    # No more commits to retrieve, exit the loop
                    break

                commit_ids.extend([commit['sha'] for commit in commits])
                page += 1  # Move to the next page
            else:
                raise Exception(f"Failed to fetch commits: {response.status_code}, {response.text}")
        
        return commit_ids
    
    def export_commits_to_json(self, repo_name, commit_ids, filename):
        """
        Export the commit IDs to a JSON file in the format { "repo_name": ["commit_id_1", "commit_id_2", ...] }.

        :param repo_name: Name of the repository
        :param commit_ids: List of commit IDs
        :param filename: The name of the JSON file to export the data to
        """
        data = {repo_name: commit_ids}

        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Commit IDs exported to {filename}")

    def run_refactoring_miner(self, repo_owner, repo_name, commit_ids, output_folder):
        """
        Execute the RefactoringMiner command for each commit ID.

        :param repo_url: The repository URL
        :param commit_ids: List of commit IDs to process
        :param output_folder: Folder to store the JSON output for each commit
        """
        # Ensure the output directory exists
        os.makedirs(output_folder, exist_ok=True)
        for commit_id in commit_ids:
            output_file = f"{output_folder}/refactoring_{commit_id}.json"
            repo_url = f"https://github.com/{repo_owner}/{repo_name}.git"
            command = [
                "./RefactoringMiner/RefactoringMiner-3.0.9/bin/RefactoringMiner",
                "-gc",
                repo_url,
                commit_id,
                "10",
                "-json",
                output_file
            ]
            
            try:
                print(f"Running RefactoringMiner for commit {commit_id}...")
                subprocess.run(command, check=True)
                print(f"RefactoringMiner completed for commit {commit_id}, output saved to {output_file}")
            except subprocess.CalledProcessError as e:
                print(f"Error running RefactoringMiner for commit {commit_id}: {e}")

# Example usage:
tokens = [
          ]  # List of your GitHub API tokens
github_api = GitHubAPI(tokens)


### Developers changes
# Get the commit IDs for developers changes from a repository with pagination and rotating tokens 
# repo_owner = "google"
# repo_names = [ 
#              "gson"]
    
# for repo_name in repo_names:   
#     files = read_json_file(f"data/paths/{repo_name}/{repo_name}_files.json")
#     files = find_non_test_files(files)
#     commits = []
#     for path in tqdm(files, desc=f"Processing files of repo {repo_name}"):
#         path = path.replace(f"projects/{repo_name}/","")
#         commit_ids = github_api.get_commit_ids(repo_owner, repo_name, per_page=50, since=2023, file_path=path)
#         commits+=commit_ids

#         output_folder = f"data/refactoring_types/developers/{repo_name}"  # Specify the folder where the JSON files will be saved
#         github_api.run_refactoring_miner(repo_owner, repo_name, commit_ids, output_folder)


    # Output the list of commit IDs
    # github_api.export_commits_to_json(repo_name, commits, f"data/commits/{repo_name}_developers_commits.json")
