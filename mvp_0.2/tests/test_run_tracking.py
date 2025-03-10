import sqlite3
import os
import pytest
from src.run_management.run_tracking import initialize_db, log_run, get_all_runs, get_run, update_run_status

@pytest.fixture(scope="function")
def setup_db():
    """Setup an in-memory SQLite DB for testing."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE runs (
            run_id TEXT PRIMARY KEY,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            input_files TEXT,
            output_path TEXT,
            status TEXT CHECK(status IN ('pending', 'running', 'completed', 'failed'))
        )
    ''')
    conn.commit()
    yield conn
    conn.close()

def test_log_run(setup_db):
    """Test logging a new run."""
    run_id = log_run(["file1.fastq", "file2.fastq"], "/output")
    assert run_id is not None
    assert isinstance(run_id, str)

def test_update_run_status(setup_db):
    """Test updating a run's status."""
    run_id = log_run(["file1.fastq"], "/output")
    update_run_status(run_id, "completed")
    run = get_run(run_id)
    assert run[4] == "completed"  # Status column
