## Results

These files are the output of running the benchmark on Nov 30, 2021 a MacBook Pro (16-inch, 2019):

- **Operating System** macOS Monterey
- **Processor** 2.3 GHz 8-Core Intel Core i9
- **Memory** 32 GB 2667 MHz DDR4
- **Graphics** AMD Radeon Pro 5500M 4 GB; Intel UHD Graphics 630 1536 MB;

From the root directory:

```
source .env-Z-1 && snakemake --cores all results/XY-1920-Z-1-C-4-T-1-XC-256.csv
source .env-Z-259 && snakemake --cores all results/XY-1920-Z-259-C-4-T-1-XC-256.csv
python ./scripts/plot_combined.py
```
