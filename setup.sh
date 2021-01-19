set -e
set -u
set -x
# TODO: move to make
wget -N https://downloads.openmicroscopy.org/images/Imaris-IMS/eliana/retina_large.ims
test -e tmp || bioformats2raw retina_large.ims tmp --file_type=zarr --dimension-order=XYZCT
test -e retina_large.ome.tiff || raw2ometiff tmp retina_large.ome.tiff
test -e retina_large.ome.zarr || mv tmp/data.zarr/0 retina_large.ome.zarr

mc config host add benchmark http://localhost:9000 minioadmin minioadmin
mc mb -p benchmark/data
mc policy set public benchmark/data
mc cp -r *.ims benchmark/data/
mc cp -r *.tiff benchmark/data/
mc cp -r *.zarr benchmark/data/
mc cp -r data/1-byte benchmark/data/
