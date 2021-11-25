#!/usr/bin/env bash

OUT="../results"

set -e
set -u
set -x

pnpm bench --reporter=silent > "$OUT/$NAME.csv"
./plot_results.py "$OUT/$NAME.csv" "$OUT/$NAME.png"
