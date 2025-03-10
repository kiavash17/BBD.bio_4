import sqlite3

def update_run_status(run_id, status):
    """Update the status of a run."""
    if status not in ('pending', 'running', 'completed', 'failed'):
        raise ValueError("Invalid status value")
    
    conn = sqlite3.connect("runs.db")
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE runs SET status = ? WHERE run_id = ?
    ''', (status, run_id))
    conn.commit()
    conn.close()
    
    return f"Run {run_id} updated to {status}"
