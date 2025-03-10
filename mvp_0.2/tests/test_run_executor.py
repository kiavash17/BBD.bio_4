import pytest
import os
import subprocess
from unittest.mock import patch
from src.run_management.run_executor import execute_run

@pytest.fixture
def fake_run():
    """Return a fake run setup."""
    return {
        "run_id": "test_run",
        "input_files": ["test.fastq"],
        "output_dir": "./test_output",
        "log_dir": "./test_logs"
    }

def test_execute_run(fake_run):
    """Test that execute_run correctly transitions statuses."""
    os.makedirs(fake_run["output_dir"], exist_ok=True)
    os.makedirs(fake_run["log_dir"], exist_ok=True)

    with patch("subprocess.run") as mock_subprocess:
        mock_subprocess.return_value.returncode = 0  # Simulate success
        execute_run(fake_run["run_id"], fake_run["input_files"], fake_run["output_dir"], fake_run["log_dir"])

    assert os.path.exists(os.path.join(fake_run["log_dir"], "execution.log"))

def test_execute_run_failure(fake_run):
    """Test handling of execution failure."""
    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "fastqc")):
        execute_run(fake_run["run_id"], fake_run["input_files"], fake_run["output_dir"], fake_run["log_dir"])

    assert os.path.exists(os.path.join(fake_run["log_dir"], "execution.log"))
