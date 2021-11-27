#! /bin/sh

# download
# docker run -ti --rm -v `pwd`/$IDR_ID:/data imagedata/download $IDR_ID $IDR_PATH /data
# docker run -ti --rm -v `pwd`/$IDR_ID:/data imagedata/download $IDR_ID $ND_PATH /data

# convert, just pick first series (-s=0)
bioformats2raw \
	--nested \
	--compression=raw \
	-w $XY \
	-h $XY \
	-s=0 \
	"$IDR_ID/$IDR_NAME" \
	$NAME/out

# create  OME-TFF
raw2ometiff \
	--compression=raw \
	$NAME/out \
	$NAME/data.ome.tif

# generate offsets file
generate_tiff_offsets --input_file $NAME/data.ome.tif
