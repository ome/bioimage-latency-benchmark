#!/usr/bin/env bash

test -e .env && . .env
HOST=${HOST:-localhost}
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
DIR=${DIR:-./data}
set -e
set -u
set -x

mc config host add benchmark http://$HOST:9000 ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}
mc mb -p benchmark/data
mc policy set public benchmark/data

cd $DIR
mc cp -r *.ims benchmark/data/
mc cp -r *.tiff benchmark/data/
mc cp -r *.zarr benchmark/data/
mc cp -r 1-byte benchmark/data/
