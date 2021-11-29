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
snakemake --cores all benchmark_plot.png
```

This will store both the benchmarking results ('benchmark_data.csv') as well as a 
plotted graph ('benchmark_plot.png').
