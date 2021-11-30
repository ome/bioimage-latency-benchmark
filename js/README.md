# Bioimage Latency Benchmark

This benchmark measures the time taken to retrieve chunks
from OME-NGFF, OME-TIFF, and Indexed OME-TIFF.

## Quick start

To get started, clone this repository locally:
```
git clone https://github.com/manzt/bioimage-latency-benchmark.git
cd bioimage-latency-benchmark
```

## Generate sample data

You will likely want to adjust the parameters in `.env` first, then run:

```
snakemake --cores all results.png
```

This will store both the benchmarking results ('results.csv') as well as a 
plotted graph ('results.png').


## Results

The contents of `results/` were generated with the following:

```
source .env-Z-1   && snakemake --cores all results/XY-1920-Z-1-C-4-T-1-XC-256.csv
source .env-Z-259 && snakemake --cores all results/XY-1920-Z-259-C-4-T-1-XC-256.csv
jupyter execute results plots.ipynb
```
