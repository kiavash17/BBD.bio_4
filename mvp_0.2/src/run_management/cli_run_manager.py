import argparse
import os
import logging
import sqlite3
from src.run_management.run_tracking import log_run, get_run
from src.run_management.directory_manager import setup_run_directory, move_input_files
from src.run_management.run_executor import execute_run

# Configure logging
logging.basicConfig(
    filename="run_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def create_run(input_files, base_path):
    """Create a new run and set up directories."""
    run_id = log_run(input_files, "")  # First log call
    run_dir = setup_run_directory(base_path, run_id)
    output_path = os.path.join(run_dir, "output")

    log_run(input_files, output_path)  # Second log call

    # Update the database entry with the correct output path
    conn = sqlite3.connect("runs.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE runs SET output_path = ? WHERE run_id = ?", (output_path, run_id))
    conn.commit()
    conn.close()
    
    move_input_files(input_files, os.path.join(run_dir, "input"))  # Move input files

    logging.info(f"Run {run_id} created successfully at {run_dir}")
    print(f"Run {run_id} created successfully! Directory: {run_dir}")
    
    return run_id

def start_run(run_id, base_path):
    """Start execution of a run."""
    run_details = get_run(run_id)
    if not run_details:
        logging.error(f"Run {run_id} not found!")
        print(f"Run {run_id} not found!")
        return
    
    input_files = eval(run_details[2])  # Convert JSON string back to list
    run_dir = os.path.join(base_path, "runs", run_id)
    output_dir = os.path.join(run_dir, "output")
    log_dir = os.path.join(run_dir, "logs")
    execute_run(run_id, input_files, output_dir, log_dir)
    logging.info(f"Run {run_id} execution started!")
    print(f"Run {run_id} execution started!")

def main():
    parser = argparse.ArgumentParser(description="CLI for BBD.bio Run Management")
    subparsers = parser.add_subparsers(dest="command")
    
    # Subcommand: create-run
    create_parser = subparsers.add_parser("create-run", help="Create a new run")
    create_parser.add_argument("--input-files", nargs="+", required=True, help="List of input files")
    create_parser.add_argument("--base-path", required=True, help="Base path for runs")
    
    # Subcommand: start-run
    start_parser = subparsers.add_parser("start-run", help="Start an existing run")
    start_parser.add_argument("--run-id", required=True, help="Run ID to execute")
    start_parser.add_argument("--base-path", required=True, help="Base path for runs")
    
    args = parser.parse_args()
    
    if args.command == "create-run":
        create_run(args.input_files, args.base_path)
    elif args.command == "start-run":
        start_run(args.run_id, args.base_path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
