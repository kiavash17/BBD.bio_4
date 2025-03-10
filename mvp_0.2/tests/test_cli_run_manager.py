import pytest
import argparse
import os
from unittest.mock import patch
from src.run_management.cli_run_manager import create_run, start_run, main

@pytest.fixture
def mock_base_path():
    """Provide a temporary base path for testing."""
    return "/tmp/test_runs"

@patch("src.run_management.cli_run_manager.log_run", return_value="test-run-id")
@patch("src.run_management.cli_run_manager.setup_run_directory", return_value="/tmp/test_runs/runs/test-run-id")
@patch("src.run_management.cli_run_manager.move_input_files")
def test_create_run(mock_move, mock_setup, mock_log, mock_base_path):
    """Test CLI run creation."""
    input_files = ["sample1.fastq"]
    run_id = create_run(input_files, mock_base_path)

    assert run_id == "test-run-id"
    mock_log.assert_called_with(input_files, os.path.join(mock_base_path, "runs", "test-run-id", "output"))  # First call generates run_id
    mock_log.assert_called_with(input_files, os.path.join(mock_base_path, "runs", "test-run-id", "output"))  # Second call updates the run
    mock_setup.assert_called_once_with(mock_base_path, "test-run-id")
    mock_move.assert_called_once()

@patch("src.run_management.cli_run_manager.get_run", return_value=("test-run-id", "timestamp", "['sample1.fastq']", "/output", "pending"))
@patch("src.run_management.cli_run_manager.execute_run")
def test_start_run(mock_execute, mock_get, mock_base_path):
    """Test CLI run execution."""
    start_run("test-run-id", mock_base_path)

    mock_get.assert_called_once_with("test-run-id")
    mock_execute.assert_called_once()

@patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(
    command="create-run",
    input_files=["sample1.fastq"],
    base_path="/tmp/test_runs"
))
@patch("src.run_management.cli_run_manager.create_run")
def test_main_create_run(mock_create, mock_args):
    """Test CLI argument parsing for creating a run."""
    main()
    mock_create.assert_called_once()

@patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(
    command="start-run",
    run_id="test-run-id",
    base_path="/tmp/test_runs"
))
@patch("src.run_management.cli_run_manager.start_run")
def test_main_start_run(mock_start, mock_args):
    """Test CLI argument parsing for starting a run."""
    main()
    mock_start.assert_called_once()
