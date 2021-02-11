#!/usr/bin/env bash

DIR=${DIR:-./data}
export BENCHMARK_DATA=${DIR}
export BENCHMARK_PLOT=${DIR}/benchmark_plot.png

set -e
set -u
set -x

cd /benchmark  # TODO: should work without docker

for i in 0{..${TEST_REPEATS}}
do
    pytest benchmark.py "$@" --benchmark-json=${BENCHMARK_DATA}/${i}_benchmark_data.json
done

python plot_results.py
