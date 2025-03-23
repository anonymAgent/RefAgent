import pandas as pd
import matplotlib.pyplot as plt

##Ablation study 
# Load the Excel file and read the "Ablation study" sheet
file_path = "data/performance metrics.xlsx"
df_ablation = pd.read_excel(file_path, sheet_name="Ablation study")

# Display the first few rows of the data to understand its structure
df_ablation.head()

# Clean the column names using the first row of the DataFrame
df_ablation.columns = df_ablation.iloc[0]
df_ablation = df_ablation.drop(index=0).reset_index(drop=True)

# Convert all values to numeric
df_ablation = df_ablation.apply(pd.to_numeric)

# Split columns by category
test_pass_cols = [
    "Test pass rate RefAgent-GPT",
    "Test pass rate RefAgent-GPT without context",
    "Test pass rate -starcoder",
    "Test pass rate RefAgent-StarCoder wihtout context"
]

compilation_pass_cols = [
    "Compilation Pass Rate RefAgent-GPT",
    "Compilation Pass Rate RefAgent-GPT without context",
    "Compilation Pass Rate RefAgent-Starcoder",
    "Compilation Pass Rate RefAgent-Starcoder without context"
]

# Plot
fig, axes = plt.subplots(2, 1, figsize=(10, 10), sharex=True)

# Common boxplot style
boxprops = dict(color="black", linewidth=1.5)
whiskerprops = dict(color="black", linewidth=1.5)
capprops = dict(color="black", linewidth=1.5)
medianprops = dict(color="red", linewidth=2)

# Test Pass Rate
df_ablation[test_pass_cols].boxplot(ax=axes[0], boxprops=boxprops, whiskerprops=whiskerprops,
                                    capprops=capprops, medianprops=medianprops)
axes[0].set_ylabel("Test Pass Rate", fontsize=14, color="black")
axes[0].tick_params(axis='y', colors='black', labelsize=12)
axes[0].grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
axes[0].set_xticklabels([])  # hide x-axis labels on top plot

# Compilation Pass Rate
df_ablation[compilation_pass_cols].boxplot(ax=axes[1], boxprops=boxprops, whiskerprops=whiskerprops,
                                           capprops=capprops, medianprops=medianprops)
axes[1].set_ylabel("Compilation Pass Rate", fontsize=14, color="black")
axes[1].tick_params(axis='y', colors='black', labelsize=12)
axes[1].grid(True, linestyle="--", linewidth=0.5, alpha=0.7)

# X-axis labels for the bottom plot
x_labels = [
    r"$\bf{RefAgent-GPT}$", "RefAgent-GPT\nwithout context",
    r"$\bf{RefAgent-Starcoder}$", "RefAgent-Starcoder\nwithout context"
]
axes[1].set_xticks(range(1, len(x_labels) + 1))
axes[1].set_xticklabels(x_labels, rotation=30, ha="right", fontsize=14, color="black")

plt.tight_layout()
plt.show()



# Load Excel files
test_file = "data/test_pass_rate_over_itteration.xlsx"
compilation_file = "data/compilation_pass_rate_over_itteration.xlsx"

# Load sheets for both models
test_pass_gpt_df = pd.read_excel(test_file, sheet_name="RefAgent-GPT")
test_pass_starcoder_df = pd.read_excel(test_file, sheet_name="RefAgent-Starcoder")
comp_pass_gpt_df = pd.read_excel(compilation_file, sheet_name="RefAgent-GPT")
comp_pass_starcoder_df = pd.read_excel(compilation_file, sheet_name="RefAgent-Starcoder")

# Compute row-wise medians (each row = 1 iteration)
gpt_test_pass_medians = test_pass_gpt_df.median(axis=1)
starcoder_test_pass_medians = test_pass_starcoder_df.median(axis=1)
gpt_comp_pass_medians = comp_pass_gpt_df.median(axis=1)
starcoder_comp_pass_medians = comp_pass_starcoder_df.median(axis=1)

# Create iteration labels
iterations = [f"Iter {i}" for i in range(1, len(gpt_test_pass_medians) + 1)]

# Plot configuration
fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 8), sharex=True)

# --- Test Pass Rate Plot ---
axes[0].plot(iterations, gpt_test_pass_medians, marker="o", linestyle="-", color="blue", label="RefAgent-GPT")
axes[0].plot(iterations, starcoder_test_pass_medians, marker="s", linestyle="-", color="green", label="RefAgent-Starcoder")
axes[0].set_ylabel("Median Test Pass Rate", fontsize=12)
axes[0].legend(fontsize=12, loc="lower right")
axes[0].grid(axis="y", linestyle="--", alpha=0.7)
axes[0].set_ylim(50, 100)  # same y-axis range
axes[0].set_yticks(range(50, 101, 10))  # consistent ticks

# --- Compilation Pass Rate Plot ---
axes[1].plot(iterations, gpt_comp_pass_medians, marker="o", linestyle="--", color="blue", label="RefAgent-GPT")
axes[1].plot(iterations, starcoder_comp_pass_medians, marker="s", linestyle="--", color="green", label="RefAgent-Starcoder")
axes[1].set_xlabel("Iteration", fontsize=12)
axes[1].set_ylabel("Median Compilation Pass Rate", fontsize=12)
axes[1].legend(fontsize=12, loc="lower right")
axes[1].grid(axis="y", linestyle="--", alpha=0.7)
axes[1].set_ylim(50, 100)
axes[1].set_yticks(range(50, 101, 10))

plt.tight_layout()
plt.show()
