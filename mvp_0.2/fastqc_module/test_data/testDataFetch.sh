# fetching SRR12345678
prefetch SRR12345678
fasterq-dump SRR12345678.sra
gzip SRR12345678_*.fastq
zcat SRR12345678_1.fastq.gz | head -n 8
