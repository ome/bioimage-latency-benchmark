#!/usr/bin/env bash

DIR=${DIR:-./data}
export BENCHMARK_DATA=${DIR}/benchmark_data.json
export BENCHMARK_PLOT=${DIR}/benchmark_plot.png

set -e
set -u
set -x

cd /benchmark  # TODO: should work without docker
pytest benchmark.py "$@" --benchmark-json=${BENCHMARK_DATA}
python plot_results.py
