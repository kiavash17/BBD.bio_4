# BBD.bio Repository

A modular bioinformatics platform for managing and executing NGS workflows with AI-driven automation.

## Features
- **Run Management CLI**: Track, execute, and manage workflows.
- **Automated Directory Handling**: Organizes input, output, and log files per run.
- **Status Tracking**: Monitors workflow execution from pending to completion.
- **NGS Workflow Execution**: Runs preprocessing, alignment, and analysis tasks dynamically.

## Installation
Install dependencies:
```sh
pip install -r requirements.txt
```

## Usage
### Run Management CLI
#### Create a new run:
```sh
python bin/cli_run_manager.py create-run --input-files sample1.fastq sample2.fastq --base-path /path/to/runs
```

#### Start a run:
```sh
python bin/cli_run_manager.py start-run --run-id <run_id> --base-path /path/to/runs
```

### Running Tests
Run unit tests:
```sh
pytest tests/ --disable-warnings -v
```

## Repository Structure
```
📂 BBD.bio
 ┣ 📂 src
 ┃ ┣ 📂 run_management  # Run tracking, directory handling, execution
 ┃ ┣ 📂 bioinformatics  # Workflow modules (alignment, QC, analysis)
 ┣ 📂 tests             # Unit tests
 ┣ 📂 bin               # CLI scripts
 ┣ 📜 requirements.txt  # Dependencies
 ┣ 📜 runs.db           # SQLite database for run tracking
 ┣ 📜 README.md         # This document
```

## Notes
- Runs are tracked in `runs.db`.
- Logs are saved in `run_management.log`.
- Output files are stored in `runs/{run_id}/output/`.

For development or debugging, ensure SQLite and dependencies are installed properly.


------------update on 3/12/2025---------------
# BBD.bio Lab AI Orchestrator

### **📌 Update on 3/12/2025**

## **Project Overview**
- **Project Name:** BBD.bio Lab AI Orchestrator  
- **Goal:** Automate and streamline NGS bioinformatics workflow generation, refinement, and execution using AI.  
- **Why?** Reduce manual workflow configuration, optimize computational resource usage, and improve accessibility for non-experts.

---

## **🛠️ System Architecture Overview**
### **📌 Components and Responsibilities**

| **Component**       | **Role** |
|---------------------|---------|
| **AIOrchestrator** | Generates, refines, and executes bioinformatics workflows using OpenAI API. |
| **Run Management** | Manages workflow execution, logging, tracking, and directory setup. |
| **Module Database** | Stores available workflow modules and syncs missing module requests. |
| **User Interface (CLI/API)** | Provides a user interface for interacting with the orchestrator. |

---

## **📂 Codebase Structure**
```bash
/src
  ├── ai_orchestrator/               # AI-driven workflow orchestration
  │     ├── ai_orchestrator.py       # Main AI-based workflow generator
  ├── run_management/                 # Execution and tracking system
  │     ├── run_executor.py           # Handles running workflows
  │     ├── run_tracking.py           # Logs workflow execution
  │     ├── directory_manager.py      # Manages file structure for runs
  │     ├── cli_run_manager.py        # Handles CLI interactions
/tests
  ├── test_ai_orchestrator.py          # Unit tests for AI workflow generator
  ├── test_run_management.py           # Tests for workflow execution

