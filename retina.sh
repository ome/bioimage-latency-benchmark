#!/usr/bin/env bash
# This script can be used to download an existing IMS file rather
# than generation one.
set -e
set -u
set -x
wget -N https://downloads.openmicroscopy.org/images/Imaris-IMS/eliana/retina_large.ims
test -e tmp || bioformats2raw retina_large.ims tmp --file_type=zarr --dimension-order=XYZCT
test -e retina_large.ome.tiff || raw2ometiff tmp retina_large.ome.tiff
test -e retina_large.ome.zarr || mv tmp/data.zarr/0 retina_large.ome.zarr
test -e 1-byte || dd bs=1 count=1 if=/dev/random of=1-byte
