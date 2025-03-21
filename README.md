
# Multi-agent LLM-based Framework for Automatic Software Refactoring

## Overview
This repository provides a **multi-agent LLM-based framework** for **automatic software refactoring**. The framework leverages **Large Language Models (LLMs)** to suggest and apply refactoring techniques, improving code maintainability and readability. The system integrates multiple agents to analyze, recommend, and validate code transformations automatically.

## Features
- Multi-agent architecture for software refactoring
- Utilization of **LLMs** (e.g., OpenAI, StarCoder, etc.)
- GPU support for faster processing
- Integration with **Refactoring Miner** for detecting and validating refactorings
- Compatibility with GitHub repositories for code retrieval, version control, and committing improvements

## Requirements
Before running the framework, you need to set up the environment.

### Environment Setup
1. **Create a `.env` file** in the project root and add the following environment variables:
    ```env
    API_KEY=""
    GITHUB_API_KEY=""
    MODEL_NAME="gpt-40"
    ```
    Fill in the required API keys before running the framework.

2. **Hardware**:
   - Ideally runs on a **GPU** for efficiency
   - If using **open-source LLMs** (e.g., StarCoder), ensure you are running with GPU support

3. **Refactoring Miner**:
   - Download **Refactoring Miner** from [this GitHub repo](https://github.com/tsantalis/RefactoringMiner)
   - Place it inside a folder named `REFACTORINGMINER` at the project root

4. **Java & Maven**:
   - Make sure **Maven** is installed and accessible via the terminal
   - Required Maven version: **3.0.5**
   - Make sure your **Java version is compatible** with the Maven project being cloned and built
   > ⚠️ **If the Maven build fails**, please ensure you are using a Java version supported by the project (e.g., Java 8, 11, etc.)

## Installation
```bash
# Clone the repository
git clone https://github.com/your-repo/multi-agent-refactoring.git
cd multi-agent-refactoring

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running Experiments

### 1. Full Pipeline (Clone → Build → Refactor)
To run the complete pipeline using a GitHub repo and a specific tag:

```bash
./run_refAgent.sh <org/repo-name> <tag>
```

**Example:**
```bash
./run_refAgent.sh apache/maven v3.8.6
```

This script will:
- Clone the specified repository tag into `projects/before/`
- Copy it into `projects/after/`
- Build it using Maven
- Launch the refactoring pipeline via `refAgent/RefAgent_main.py`

### 2. Running the Python Refactoring Script Directly
If you already have a cloned and built project (e.g., from `run_refAgent.sh`), you can run the main refactoring pipeline directly:

```bash
python refAgent/RefAgent_main.py <project-name>
```

**Example:**
```bash
python refAgent/RefAgent_main.py jclouds
```

## Repository List

Inside the folder `data/repositories`, you will find a list of all the repositories and their corresponding tags used in our experiments. These are ready to be passed into the `setup_and_build.sh` script.

## Documentation
More documentation will be added soon to explain the internal logic of each agent and the LLM prompt strategies.

## License
This project is licensed under the **MIT License**.
