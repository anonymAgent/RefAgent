import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the Excel file and the correct sheet with headers in the second row (index 1)
file_path = "data/QMood_Analysis.xlsx"
df = pd.read_excel(file_path, sheet_name="single agent", header=1)

# Extract the relevant columns
categories = df['Unnamed: 0'].tolist()
qMood_gain_gpt = df['QMOOD Gain GPT'].tolist()
qMood_gain_starcoder = df['QMOOD Gain Starcoder'].tolist()
pass3_gpt = df['Pass@3 GPT'].tolist()
pass3_starcoder = df['Pass@3 Starcoder'].tolist()
pass1_gpt = df['Pass@1 GPT'].tolist()
pass1_starcoder = df['Pass@1 Starcoder'].tolist()

# Define pastel color palette
colors = {
    "Improvement": "#ffb3ba",  # Pastel Red-Pink
    "Pass@3": "#bae1ff",       # Pastel Blue
    "Pass@1": "#F7D08A"        # Pastel Peach
}

# Plot setup
fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
bar_width = 0.2
x = np.arange(len(categories))

# Plot for GPT
axes[0].bar(x - bar_width, qMood_gain_gpt, bar_width, label="RefAgent-GPT", color=colors["Improvement"])
axes[0].bar(x, pass3_gpt, bar_width, label="GPT Pass@3", color=colors["Pass@3"])
axes[0].bar(x + bar_width, pass1_gpt, bar_width, label="GPT Pass@1", color=colors["Pass@1"])
axes[0].set_title("RefAgent-GPT vs. Single Agent", fontsize=16)
axes[0].set_ylabel("QMOOD IR", fontsize=16)
axes[0].set_xticks(x)
axes[0].set_xticklabels(categories, rotation=45, ha="right", fontsize=20)
axes[0].tick_params(axis="y", labelsize=16)
axes[0].legend(fontsize=12, loc="upper right", bbox_to_anchor=(1, 1.2))
axes[0].grid(axis="y", linestyle="--", alpha=0.7)

# Plot for Starcoder
axes[1].bar(x - bar_width, qMood_gain_starcoder, bar_width, label="RefAgent-Starcoder", color=colors["Improvement"])
axes[1].bar(x, pass3_starcoder, bar_width, label="Starcoder Pass@3", color=colors["Pass@3"])
axes[1].bar(x + bar_width, pass1_starcoder, bar_width, label="Starcoder Pass@1", color=colors["Pass@1"])
axes[1].set_title("RefAgent-Starcoder vs. Single Agent", fontsize=16)
axes[1].set_ylabel("QMOOD IR", fontsize=16)
axes[1].set_xticks(x)
axes[1].set_xticklabels(categories, rotation=45, ha="right", fontsize=20)
axes[1].tick_params(axis="y", labelsize=16)
axes[1].legend(fontsize=12, loc="upper right", bbox_to_anchor=(1, 1.2))
axes[1].grid(axis="y", linestyle="--", alpha=0.7)

# Display the plot
plt.tight_layout()
plt.show()


##F1-score:
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the Excel file
file_path = "data/F1_score_recall.xlsx"  # Update path if needed
df_excel = pd.read_excel(file_path)

# Clean and rename the header
df = df_excel.copy()
df.columns = df.iloc[0]  # Set first row as column headers
df = df[1:]              # Drop the first row
df = df.reset_index(drop=True)

# Convert metric columns to float
df["precision"] = df["precision"].astype(float)
df["recall"] = df["recall"].astype(float)
df["f1_score"] = df["f1_score"].astype(float)

# Melt the DataFrame to long format
melted_df = pd.melt(
    df,
    id_vars=["Project", "Model", "Type"],
    value_vars=["precision", "recall", "f1_score"],
    var_name="Metric",
    value_name="Score"
)

# Set pastel color palette
sns.set_palette("pastel")

# Create 2x2 subplot
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Helper function to plot each subplot
def plot_boxplot(ax, data, title):
    sns.boxplot(data=data, x="Metric", y="Score", ax=ax)
    ax.set_title(title, fontsize=18)
    ax.set_xticklabels([])  # Remove x-tick labels
    ax.set_xlabel("")
    ax.tick_params(axis='y', labelsize=16)

# Top left: Developers vs. RefAgent-GPT
plot_boxplot(
    axes[0, 0],
    melted_df[(melted_df["Model"] == "GPT") & (melted_df["Type"] == "Developer")],
    "Developers vs. RefAgent-GPT"
)

# Top right: Developers vs. RefAgent-starcoder
plot_boxplot(
    axes[0, 1],
    melted_df[(melted_df["Model"] == "Starcoder") & (melted_df["Type"] == "Developer")],
    "Developers vs. RefAgent-starcoder"
)

# Bottom left: RefAgent-GPT vs. RefGen
plot_boxplot(
    axes[1, 0],
    melted_df[melted_df["Model"] == "GPT"],
    "RefAgent-GPT vs. RefGen"
)

# Bottom right: RefAgent-starcoder vs. RefGen
plot_boxplot(
    axes[1, 1],
    melted_df[melted_df["Model"] == "Starcoder"],
    "RefAgent-starcoder vs. RefGen"
)

# Add single legend
handles = [
    plt.Line2D([0], [0], color=sns.color_palette("pastel")[0], lw=4, label="Precision"),
    plt.Line2D([0], [0], color=sns.color_palette("pastel")[1], lw=4, label="Recall"),
    plt.Line2D([0], [0], color=sns.color_palette("pastel")[2], lw=4, label="F1-score")
]
fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.02), fontsize=20, ncol=3)

# Final layout adjustments
plt.tight_layout()
plt.show()
