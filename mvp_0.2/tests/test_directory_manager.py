import os
import shutil
import pytest
from src.run_management.directory_manager import setup_run_directory, move_input_files

@pytest.fixture(scope="function")
def test_dir():
    """Create a test directory for runs."""
    test_path = "./test_runs"
    os.makedirs(test_path, exist_ok=True)
    yield test_path
    shutil.rmtree(test_path)  # Cleanup after test

def test_setup_run_directory(test_dir):
    """Test that the directory structure is properly created."""
    run_id = "test_run"
    run_path = setup_run_directory(test_dir, run_id)

    assert os.path.exists(run_path)
    assert os.path.exists(os.path.join(run_path, "input"))
    assert os.path.exists(os.path.join(run_path, "output"))
    assert os.path.exists(os.path.join(run_path, "logs"))

def test_move_input_files(test_dir):
    """Test moving input files to the correct directory."""
    input_files = ["test_file1.fastq", "test_file2.fastq"]
    input_dir = os.path.join(test_dir, "input")
    os.makedirs(input_dir, exist_ok=True)

    # Creating dummy files
    for f in input_files:
        with open(f, "w") as file:
            file.write("TEST FILE CONTENT")

    move_input_files(input_files, input_dir)

    for f in input_files:
        assert os.path.exists(os.path.join(input_dir, os.path.basename(f)))

    # Cleanup
    for f in input_files:
        os.remove(f)
