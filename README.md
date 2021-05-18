[![DOI](https://zenodo.org/badge/329595844.svg)](https://zenodo.org/badge/latestdoi/329595844)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ome/ngff-latency-benchmark/main?filepath=notebooks)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ome/ngff-latency-benchmark/)

# OME-NGFF: latency benchmark

To get started, clone this repository locally:
```
git clone https://github.com/ome/ngff-latency-benchmark.git
cd ngff-latency-benchmark
```

## Generate sample data

You will likely want to adjust the parameters in `.env` first, then run:

```
./generate.sh
```

which will run several docker-compose commands in a row. This could take
a substantial amount of time depending on your parameters.


## Then, start S3 and upload the data

Start the various Docker containers in the background ("detached" mode):
```
docker-compose up -d
```

Once the containers are up, run:
```
docker-compose run --rm upload
```

## Finally, run the benchmark

```
docker-compose run --rm benchmark -sv
```

This will store both the benchmarking results ('benchmark_data.json') as well as a plotted graph
('benchmark_plot.png') in the directory along with the input data.
