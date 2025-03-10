import os
import uuid
import datetime
import json

def run_fastqc(input_files, base_dir="/workspaces/BBD.bio_4/mvp_0.2/runs"):
    """
    Runs FastQC with structured run tracking.
    
    Parameters:
        input_files (list): List of FASTQ files.
        base_dir (str): Base directory for storing all runs.
    
    Returns:
        run_dir (str): Directory containing the results.
    """
    # Generate unique Run ID
    run_id = str(uuid.uuid4())[:8]  # Short UUID for uniqueness
    today = datetime.datetime.now().strftime("%Y/%m/%d")

    # Define structured run directory
    run_dir = os.path.join(base_dir, today, f"run_{run_id}")
    input_dir = os.path.join(run_dir, "input")
    output_dir = os.path.join(run_dir, "output")
    log_dir = os.path.join(run_dir, "logs")

    # Create directories
    for d in [input_dir, output_dir, log_dir]:
        os.makedirs(d, exist_ok=True)

    # Copy input files to run-specific input directory
    for file in input_files:
        os.system(f"cp {file} {input_dir}/")

    # Run FastQC
    input_files_str = " ".join([os.path.join(input_dir, os.path.basename(f)) for f in input_files])
    os.system(f"fastqc -o {output_dir} {input_files_str}")

    # Store metadata
    metadata = {
        "run_id": run_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "input_files": input_files,
        "output_dir": output_dir,
        "status": "completed"
    }
    with open(os.path.join(run_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)

    return run_dir
