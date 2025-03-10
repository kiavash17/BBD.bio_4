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

