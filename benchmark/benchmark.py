import time

import fsspec
import h5py
import pytest
import requests
import s3fs
import tifffile
import zarr
from os import environ

DIR = environ.get("DIR", "data")
BASE = environ.get("BASE", "retina_large")
HOST = environ.get("HOST", "localhost")


def local(filename: str) -> str:
    return f"{DIR}/{filename}", fsspec.filesystem('file')


def http(filename: str) -> str:
    return f"http://{HOST}:8000/{filename}", fsspec.filesystem('http')


def s3(filename: str) -> str:
    return f"s3://data/{filename}", s3fs.S3FileSystem(
        anon=True, client_kwargs={"endpoint_url": f"http://{HOST}:9000"})


@pytest.mark.parametrize("method", (local, http, s3))
def test_1_byte_overhead(benchmark, method):

    def loader(filename: str, fs):
        with fs.open(filename) as f:
            f.read()
        
    benchmark(loader, *method("1-byte"))


@pytest.mark.parametrize("method", (local, http, s3))
def test_zarr_chunk(benchmark, method):

    def loader(filename: str, fs):
        store = s3fs.S3Map(root=filename, s3=fs, check=False)
        group = zarr.group(store=store)
        data = group["0"]
        chunks = data.chunks
        len(data[0:chunks[0], 0:chunks[1], 0:chunks[2], 0:chunks[3], 0:chunks[4]])

    benchmark(loader, *method(f"{BASE}.ome.zarr"))


@pytest.mark.parametrize("method", (local, http, s3))
def test_tiff_tile(benchmark, method):

    def loader(filename: str, fs):

        with fs.open(filename) as f:
            with tifffile.TiffFile(f) as tif:
                fh = tif.filehandle
                for page in tif.pages:
                    fh.seek(page.dataoffsets[0])
                    fh.read(page.databytecounts[0])
                    return

    benchmark(loader, *method(f"{BASE}.ome.tiff"))


@pytest.mark.parametrize("method", (local, http, s3))
def test_hdf5_chunk(benchmark, method):

    def loader(filename: str, fs):

        with fs.open(filename) as f:
            with h5py.File(f) as ims:
                data = ims["DataSet"]["ResolutionLevel 0"]["TimePoint 0"]["Channel 0"]["Data"]
                chunks = data.chunks
                len(data[0:chunks[0], 0:chunks[1], 0:chunks[2]])

    benchmark(loader, *method(f"{BASE}.ims"))
