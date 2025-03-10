import os
import subprocess
import json
from src.run_management import update_run_status

def execute_run(run_id, input_files, output_dir, log_dir):
    """Execute a bioinformatics module (e.g., FastQC)."""
    update_run_status(run_id, "running")
    log_file = os.path.join(log_dir, "execution.log")
    

    
    try:
        with open(log_file, "w") as log:
            for file in input_files:
                command = ["fastqc", file, "-o", output_dir]
                process = subprocess.run(command, stdout=log, stderr=log, check=True)
        
        update_run_status(run_id, "completed")
    except subprocess.CalledProcessError:
        update_run_status(run_id, "failed")
