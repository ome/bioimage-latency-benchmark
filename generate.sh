#!/usr/bin/env bash

test -e .env && . .env
DIR=${DIR:-./data}
CLEAN=${CLEAN:-"--rm"}

set -e
set -u
set -x

IMS=IMS_XY-${XY}-Z-${Z}-T-${T}-C-${C}-XYC-${XC}-ZC-${ZC}.ims
ZARR=IMS_XY-${XY}-Z-${Z}-T-${T}-C-${C}-XYC-${XC}-ZC-${ZC}.ome.zarr
TIFF=IMS_XY-${XY}-Z-${Z}-T-${T}-C-${C}-XYC-${XC}-ZC-${ZC}.ome.tiff

BF2RAW=bioformats2raw
RAW2OMETIFF=raw2ometiff

echo IMS
time docker-compose run ${CLEAN} -v $DIR:$DIR \
	generate $DIR \
	$XY $Z $C $T $XC $ZC

echo ZARR
time docker-compose run ${CLEAN} -v $DIR:$DIR \
	convert $BF2RAW \
		--nested \
		--chunk_depth $ZC \
		--compression=raw \
		$DIR/$IMS \
		$DIR/out \
	-w $XC -h $XC

echo TIFF
time docker-compose run ${CLEAN} -v $DIR:$DIR \
	convert $RAW2OMETIFF \
		--compression=raw \
		$DIR/out \
		$DIR/$TIFF

docker-compose run ${CLEAN} -v $DIR:$DIR \
	convert mv \
		$DIR/out/data.zarr/0 \
		$DIR/$ZARR

docker-compose run ${CLEAN} -v $DIR:$DIR \
	convert dd bs=1 count=1 if=/dev/random of=$DIR/1-byte
