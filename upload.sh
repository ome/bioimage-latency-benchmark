#!/usr/bin/env bash

test -e .env && . .env
HOST=${HOST:-localhost}
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
BUCKET=ngff-latency-benchmark
DIR=${DIR:-./data}
set -e
set -u
set -x

# Avoiding nginx for upload
mc config host add benchmark http://minio1:9000 ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}
mc mb -p benchmark/${BUCKET}
mc policy set public benchmark/${BUCKET}

time mc mirror --overwrite ${DIR} benchmark/${BUCKET}/
