import os
import shutil

def setup_run_directory(base_path, run_id):
    """Create a unique directory structure for a run."""
    run_dir = os.path.join(base_path, "runs", run_id)
    os.makedirs(os.path.join(run_dir, "input"), exist_ok=True)
    os.makedirs(os.path.join(run_dir, "output"), exist_ok=True)
    os.makedirs(os.path.join(run_dir, "logs"), exist_ok=True)
    return run_dir

def move_input_files(input_files, destination_dir):
    """Move input files to the designated input directory."""
    os.makedirs(destination_dir, exist_ok=True)
    for file_path in input_files:
        if os.path.exists(file_path):
            shutil.copy(file_path, os.path.join(destination_dir, os.path.basename(file_path)))
    return destination_dir
