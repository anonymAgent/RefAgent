import json
import random
import pandas as pd

# Path to your JSON file
file_path = 'accumulo/accumulo_files.json'

# Read and parse the JSON file
with open(file_path, 'r') as file:
    data = json.load(file)

# Ensure the top-level element is a list
if not isinstance(data, list):
    print("The JSON file does not contain a top-level list.")
    exit()

# Filter out paths containing 'test' (case-insensitive)
filtered_data = [path for path in data if 'test' not in path.lower()]

print(f"Total number of filtered class paths: {len(filtered_data)}")

# Set sample size
sample_size = 370 # adjust as needed

# Take a random sample
sample = random.sample(filtered_data, sample_size)

# Convert sample to DataFrame
df = pd.DataFrame(sample, columns=["ClassPath"])

# Export to Excel
excel_path = 'accumulo_class_sample.xlsx'
df.to_excel(excel_path, index=False)