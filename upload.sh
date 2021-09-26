#!/usr/bin/env bash

test -e .env && . .env
HOST=${HOST:-localhost}
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
BUCKET=${BUCKET:-bioimage-latency-benchmark}
NAME=${NAME:-data}
DIR=${DIR:-./data}
set -e
set -u
set -x

if [ $# -eq 0 ]
then

    # Avoiding nginx for upload
    mc config host add benchmark http://minio1:9000 ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}
    mc mb -p benchmark/${BUCKET}
    mc policy set public benchmark/${BUCKET}

    time mc mirror --overwrite  \
	--exclude "out/*" \
	--exclude "*.csv" \
	--exclude ".*bfmemo"  \
	${DIR} benchmark/${BUCKET}/${NAME}/
elif [ "$1" = "tiff" ];
then
	time aws s3 cp ${DIR}/*.tiff s3://${BUCKET}/${NAME}/
elif [ "$1" = "ims" ];
then
	time aws s3 cp ${DIR}/*.ims s3://${BUCKET}/${NAME}/
elif [ "$1" = "zarr" ];
then
	time aws s3 cp --recursive ${DIR}/*.zarr/ s3://${BUCKET}/${NAME}/IMS_XY-${NAME}.ome.zarr/
else
    echo unknown upload: $1
    exit 1
fi
