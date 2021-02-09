import time

import boto3
import fsspec
import h5py
import pytest
import requests
import s3fs
import tifffile
from botocore import UNSIGNED
from botocore.client import Config
from os import environ

DIR = environ.get("DIR", "data")
BASE = environ.get("BASE", "retina_large")

fs = s3fs.S3FileSystem(
    anon=True, client_kwargs={"endpoint_url": "http://localhost:9000"}
)

b3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    config=Config(signature_version=UNSIGNED),
)


def local(filename, loader=None):
    start = time.time()
    with open(f"{DIR}/{filename}", "rb") as o:
        if loader:
            loader(o)
        else:
            o.read()
    stop = time.time()
    return stop - start


def http(filename, loader=None):
    url = f"http://localhost:8000/{filename}"
    if loader:
        with fsspec.open(url) as f:
            loader(f)
    else:
        elapsed = requests.get(f"http://localhost:8000/{filename}").elapsed
        return elapsed.microseconds / 1000000


def boto3(filename, loader=None):

    if loader is not None:
        pytest.skip()

    start = time.time()
    rsp = b3.get_object(Bucket="data", Key=filename)
    rsp["Body"].read()
    stop = time.time()
    return stop - start


def s3fs(filename, loader=None):
    start = time.time()
    with fs.open(f"data/{filename}") as f:
        if loader:
            loader(f)
        else:
            f.read()
    stop = time.time()
    return stop - start


@pytest.mark.parametrize("method", (local, http, boto3, s3fs))
def test_1_byte_overhead(benchmark, method):
    benchmark(method, "1-byte")


@pytest.mark.parametrize("method", (local, http, boto3, s3fs))
def test_zarr_chunk(benchmark, method):
    benchmark(method, f"{BASE}.ome.zarr/0/0/0/0/0/0")


@pytest.mark.parametrize("method", (local, http, boto3, s3fs))
def test_tiff_tile(benchmark, method):
    def loader(opened_file):
        with tifffile.TiffFile(opened_file) as tif:
            fh = tif.filehandle
            for page in tif.pages:
                fh.seek(page.dataoffsets[0])
                fh.read(page.databytecounts[0])
                return

    benchmark(method, f"{BASE}.ome.tiff", loader)


@pytest.mark.parametrize("method", (local, http, boto3, s3fs))
def test_hdf5_chunk(benchmark, method):
    def loader(opened_file):
        with h5py.File(opened_file) as f:
            data = f["DataSet"]["ResolutionLevel 0"]["TimePoint 0"]["Channel 0"]["Data"]
            chunks = data.chunks
            len(data[0:chunks[0]-1, 0:chunks[1]-1, 0:chunks[2]-1])

    benchmark(method, f"{BASE}.ims", loader)


@pytest.mark.parametrize("method", (local, http, boto3, s3fs))
def test_download_1(benchmark, method):
    def loader(opened_file):
        opened_file.read()

    benchmark(method, f"{BASE}.ims", loader)


@pytest.mark.parametrize("method", (local, http, boto3, s3fs))
def test_download_2(benchmark, method):
    benchmark(method, f"{BASE}.ims")
