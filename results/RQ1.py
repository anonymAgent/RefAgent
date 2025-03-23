import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the Excel file with two sheets
file_path = "data/Code_Smells.xlsx"
design_df = pd.read_excel(file_path, sheet_name="design")
impl_df = pd.read_excel(file_path, sheet_name="implimentation", header=1)

# Extract data from design sheet
design_labels = design_df["Design Code Smells"].tolist()
refagent_gpt_design = design_df["RefAgent-GPT"].tolist()
refagent_starcoder_design = design_df["RefAgent—starcoder"].tolist()

# Extract data from implementation sheet
impl_labels = impl_df["Implementation Code Smells"].tolist()
refagent_gpt_impl = impl_df["RefAgent-GPT"].tolist()
refagent_starcoder_impl = impl_df["RefAgent-Starcoder"].tolist()

# Function to modify labels for readability
def modify_labels(labels):
    modified = []
    for label in labels:
        words = label.split()
        if len(words) > 2:
            modified.append(" ".join(words[:2]) + "\n" + " ".join(words[2:]))
        else:
            modified.append(label)
    return modified

# Modified labels
modified_design_labels = modify_labels(design_labels)
modified_impl_labels = modify_labels(impl_labels)

# Plotting parameters
bar_width = 0.35
axis_label_size = 16
tick_label_size = 14
x_label_size = 16

# Create subplots
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# Plot Design Code Smells
x_design = np.arange(len(design_labels))
axes[0].bar(x_design - bar_width/2, refagent_gpt_design, bar_width, label='RefAgent-GPT', color='lightblue', alpha=0.7)
axes[0].bar(x_design + bar_width/2, refagent_starcoder_design, bar_width, label='RefAgent—starcoder', color='lightcoral', alpha=0.7)
axes[0].set_ylabel('SRR', fontsize=axis_label_size)
axes[0].set_xticks(x_design)
axes[0].set_xticklabels(modified_design_labels, rotation=45, ha='right', fontsize=x_label_size)
axes[0].legend(loc='upper right', fontsize=tick_label_size)
axes[0].set_title("Design Smell Reduction", fontsize=axis_label_size)
axes[0].set_ylim(0, 0.75)
axes[0].tick_params(axis='y', labelsize=tick_label_size)

# Plot Implementation Code Smells
x_impl = np.arange(len(impl_labels))
axes[1].bar(x_impl - bar_width/2, refagent_gpt_impl, bar_width, label='RefAgent-GPT', color='lightblue', alpha=0.7)
axes[1].bar(x_impl + bar_width/2, refagent_starcoder_impl, bar_width, label='RefAgent-Starcoder', color='lightcoral', alpha=0.7)
axes[1].set_ylabel('SRR', fontsize=axis_label_size)
axes[1].set_xticks(x_impl)
axes[1].set_xticklabels(modified_impl_labels, rotation=45, ha='right', fontsize=x_label_size)
axes[1].legend(loc='upper right', fontsize=tick_label_size)
axes[1].set_title("Implementation Smell Reduction", fontsize=axis_label_size)
axes[1].set_ylim(0, 0.75)
axes[1].tick_params(axis='y', labelsize=tick_label_size)

# Final layout adjustments
plt.tight_layout()
plt.show()
