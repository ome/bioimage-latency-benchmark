#!/usr/bin/env bash
# generate files

set -e
set -u
set -x

OUTPUT=${1:-ImarisFiles}
THREADS=${THREADS:-8}
BITS=${BITS:-16bit}
echo ********************************************************************
echo Writing ${BITS} data with ${THREADS} threads to: $OUTPUT
echo ********************************************************************

cd ImarisWriterTest/application
mkdir -p ${OUTPUT}

x=$2
z=$3
c=$4
t=$5
xc=$6
zc=$7
./ImarisWriterTestRelease -sizex $x -sizey $x -sizez $z -sizet $t -sizec $c -chunkx $xc -chunky $xc -chunkz $zc -type ${BITS} -threads ${THREADS} -outputpath ${OUTPUT} IMS_XY-$x-Z-$z-T-$t-C-$c-XYC-$xc-ZC-$zc.ims
