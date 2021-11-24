#! /bin/sh

IDR_ID=idr0077
# IDR_NAME="2018-12-18 ASY H2B bud 05 3D 8 angles_Maximum intensity projection.czi"
# IDR_PATH="/20200429-ftp/$SIMPLE"
# NAME="XY-1920-Z-1-C-4-T-1"

IDR_NAME="2018-12-18 ASY H2B bud 05 3D 8 angles.czi"
IDR_PATH="/20191219-disk01/figure 02/3D flower/$IDR_NAME"
NAME="XY-1920-Z-259-C-4-T-1"
XY=256

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
