import os
import pytest
import psycopg2
from fastqc_module.fastqc import run_fastqc

def test_fastqc():
    """
    Unit test for FastQC with run-specific output management and database logging.
    """
    input_files = ["test_data/SRR12345678_1.fastq.gz", "test_data/SRR12345678_2.fastq.gz"]
    
    # Run FastQC
    run_id, run_dir = run_fastqc(input_files)
    
    # Check expected output
    output_dir = os.path.join(run_dir, "output")
    for file in input_files:
        base_name = os.path.basename(file).replace(".fastq.gz", "")
        assert os.path.exists(f"{output_dir}/{base_name}_fastqc.html"), f"FastQC report for {base_name} is missing!"
        assert os.path.exists(f"{output_dir}/{base_name}_fastqc.zip"), f"FastQC ZIP archive for {base_name} is missing!"
    
    # Verify the run was logged in the database
    conn = psycopg2.connect("dbname=bioinformatics user=admin password=secure")
    cur = conn.cursor()
    cur.execute("SELECT status FROM runs WHERE run_id = %s", (run_id,))
    status = cur.fetchone()
    conn.close()
    
    assert status is not None, "Run ID not found in database!"
    assert status[0] == "completed", "Run status is incorrect!"