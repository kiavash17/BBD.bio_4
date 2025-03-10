import json
import pytest
import os
import subprocess

def generate_module_metadata(name, version, language, dependencies, input_files, output_files, execution, test_case):
    """Generate standardized metadata for a bioinformatics module."""
    metadata = {
        "name": name,
        "version": version,
        "language": language,
        "dependencies": dependencies,
        "input": input_files,
        "output": output_files,
        "execution": execution,
        "test_case": test_case
    }
    return metadata

# Define metadata for each module
modules = [
    generate_module_metadata(
        name="FastQC",
        version="0.11.9",
        language="Java",
        dependencies=["Java >= 8"],
        input_files=["raw_reads.fastq.gz"],
        output_files=["fastqc_report.html", "fastqc_data.txt"],
        execution="fastqc raw_reads.fastq.gz",
        test_case="test_data/example_reads.fastq.gz"
    ),
    generate_module_metadata(
        name="BWA",
        version="0.7.17",
        language="C",
        dependencies=["bwa"],
        input_files=["reference.fasta", "reads.fastq.gz"],
        output_files=["aligned_reads.sam"],
        execution="bwa mem reference.fasta reads.fastq.gz > aligned_reads.sam",
        test_case="test_data/example_reads.fastq.gz"
    ),
    generate_module_metadata(
        name="GATK",
        version="4.2.0.0",
        language="Java",
        dependencies=["Java >= 8", "gatk"],
        input_files=["aligned_reads.bam", "reference.fasta"],
        output_files=["variants.vcf"],
        execution="gatk HaplotypeCaller -I aligned_reads.bam -R reference.fasta -O variants.vcf",
        test_case="test_data/example_aligned_reads.bam"
    ),
    generate_module_metadata(
        name="Biopython",
        version="1.81",
        language="Python",
        dependencies=["biopython"],
        input_files=["sequences.fasta"],
        output_files=["parsed_sequences.json"],
        execution="python parse_sequences.py sequences.fasta",
        test_case="test_data/example_sequences.fasta"
    ),
    generate_module_metadata(
        name="Bioconductor",
        version="3.15",
        language="R",
        dependencies=["R >=4.0", "BiocManager"],
        input_files=["expression_matrix.csv"],
        output_files=["differential_expression_results.csv"],
        execution="Rscript run_bioconductor.R expression_matrix.csv",
        test_case="test_data/example_expression_matrix.csv"
    )
]

# Save module metadata to JSON file
with open("module_metadata.json", "w") as f:
    json.dump(modules, f, indent=4)

print("Module metadata saved to module_metadata.json")

# Unit tests for module execution
def run_module_test(module):
    try:
        print(f"Testing {module['name']}...")
        subprocess.run(module["execution"], shell=True, check=True)
        for output in module["output"]:
            assert os.path.exists(output), f"Output file {output} missing!"
        print(f"{module['name']} test passed.\n")
    except Exception as e:
        print(f"{module['name']} test failed: {str(e)}\n")
        raise

@pytest.mark.parametrize("module", modules)
def test_modules(module):
    run_module_test(module)

print("Unit tests ready.")