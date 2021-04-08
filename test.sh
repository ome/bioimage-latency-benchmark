#!/bin/sh
set -eu

# start
docker-compose up -d
# upload
docker-compose run --rm upload
# run benchmark
docker-compose run --rm benchmark -sv
