#!/usr/bin/env bash
DIR=${DIR:-/uod/idr-scratch/ngff-latency-benchmark/2021-02-09-quick}
set -e
set -u
set -x

mc config host add benchmark http://localhost:9000 minioadmin minioadmin
mc mb -p benchmark/data
mc policy set public benchmark/data

cd $DIR
mc cp -r *.ims benchmark/data/
mc cp -r *.tiff benchmark/data/
mc cp -r *.zarr benchmark/data/
mc cp -r 1-byte benchmark/data/
