# Multi-agent LLM-based Framework for Automatic Software Refactoring

## Overview
This repository provides a **multi-agent LLM-based framework** for **automatic software refactoring**. The framework leverages **Large Language Models (LLMs)** to suggest and apply refactoring techniques, improving code maintainability and readability. The system integrates multiple agents to analyze, recommend, and validate code transformations automatically.

## Features
- Multi-agent architecture for software refactoring
- Utilization of **LLMs** (e.g., OpenAI, StarCoder, etc.)
- GPU support for faster processing
- Integration with **Refactoring Miner** for detecting and validating refactorings
- Compatibility with GitHub repositories for code retrieval and version control, and commit improvement

## Requirements
Before running the framework, you need to set up the environment.

### Environment Setup
1. **API Keys**: Obtain the following API keys and set them as environment variables:
   - `OPENAI_API_KEY` (if using OpenAI models)
   - `GITHUB_API_KEY` (for accessing repositories)

2. **Hardware**:
   - Ideally runs on a **GPU** for efficiency
   - If using **open-source LLMs** (e.g., StarCoder), ensure they are properly installed

3. **Refactoring Miner**:
   - Download **Refactoring Miner** from [here](https://github.com/tsantalis/RefactoringMiner)
   - Place it inside a folder named `REFACTORINGMINER` at the project root

### Installation
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
To run the experiments, execute the main script:
```bash
python RefAgent_main.py
```
Ensure that all **API keys** are set and the **Refactoring Miner** folder is correctly placed before running the script.

## Documentation
More documentation to come

## Contributing
Feel free to submit issues and pull requests to improve the framework!

## License
This project is licensed under the MIT License.

