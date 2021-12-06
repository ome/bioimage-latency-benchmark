# Bioimage Latency Benchmark

This benchmark measures the time taken to retrieve chunks
from OME-NGFF, OME-TIFF, and Indexed OME-TIFF. The workflow is
described and executed by [Snakemake](https://snakemake.readthedocs.io/en/stable/),
a management system for scalable reproducible analysis pipelines.

## Requirements

- [`conda`](https://docs.conda.io/en/latest/)
- [Docker](https://www.docker.com/)

## Quick start

To get started, clone this repository locally and create a `conda` environment:

```
git clone https://github.com/js/bioimage-latency-benchmark.git
cd bioimage-latency-benchmark/js

conda env create -n viv-bench -f environment.yml
conda activate viv-bench
```

## Generate sample data

You will likely want to adjust the parameters in `.env` first, then run:

```
snakemake --cores all results.png
```

This will store both the benchmarking results ('results.csv') as well as a
plotted graph ('results.png').
