import pytest
from src.run_management.status_manager import update_run_status
from src.run_management.run_tracking import log_run, get_run

def test_status_update():
    """Test that a run's status is correctly updated."""
    run_id = log_run(["test.fastq"], "/output")
    update_run_status(run_id, "running")
    assert get_run(run_id)[4] == "running"

    update_run_status(run_id, "completed")
    assert get_run(run_id)[4] == "completed"

    with pytest.raises(ValueError):
        update_run_status(run_id, "invalid_status")  # Should fail
