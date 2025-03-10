import sqlite3
import json
import uuid
from datetime import datetime

def initialize_db():
    """Create the SQLite database and runs table."""
    conn = sqlite3.connect("runs.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            input_files TEXT,
            output_path TEXT,
            status TEXT CHECK(status IN ('pending', 'running', 'completed', 'failed'))
        )
    ''')
    conn.commit()
    conn.close()

def log_run(input_files, output_path):
    """Log a new run in the database."""
    run_id = str(uuid.uuid4())
    input_files_json = json.dumps(input_files)
    
    conn = sqlite3.connect("runs.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO runs (run_id, input_files, output_path, status)
        VALUES (?, ?, ?, 'pending')
    ''', (run_id, input_files_json, output_path))
    conn.commit()
    conn.close()
    
    return run_id

def update_run_status(run_id, status):
    """Update the status of a run."""
    conn = sqlite3.connect("runs.db")
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE runs SET status = ? WHERE run_id = ?
    ''', (status, run_id))
    conn.commit()
    conn.close()

def get_all_runs():
    """Retrieve all runs from the database."""
    conn = sqlite3.connect("runs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM runs")
    runs = cursor.fetchall()
    conn.close()
    return runs

def get_run(run_id):
    """Retrieve details of a specific run."""
    conn = sqlite3.connect("runs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
    run = cursor.fetchone()
    conn.close()
    return run

if __name__ == "__main__":
    initialize_db()
