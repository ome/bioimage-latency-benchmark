#!/usr/bin/env bash
#generate files

set -e
set -u

OUTPUT=${1:-ImarisFiles}
echo **********************************
echo Writing data to: $OUTPUT
echo **********************************

cd ImarisWriterTest/application
mkdir ${OUTPUT}

convert(){
    ./ImarisWriterTestRelease -sizex $x -sizey $x -sizez $z -sizet $t -sizec $c -chunkx $xc -chunky $xc -chunkz $zc -type 16bit -threads 8 -outputpath ${OUTPUT}  IMS_XY-$x-Z-$z-T-$t-C-$c-XYC-$xc-ZC-$zc.ims
}

# https://github.com/ome/ngff-latency-benchmark/issues/5
x=131072
z=131072
c=32
t=1
xc=1024
zc=1024
convert

# https://github.com/ome/ngff-latency-benchmark/issues/6
x=512
z=512
c=2
t=512
xc=64
zc=64
convert
