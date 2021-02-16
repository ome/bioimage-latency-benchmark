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
ROUNDS = int(environ.get("ROUNDS", 10))

fsspec_default_args = {
    "skip_instance_cache": False,
    #"use_listings_cache": False}
}


class Fixture:

    def __init__(self, benchmark):
        benchmark.pedantic(self.run, setup=self.setup, rounds=ROUNDS)

    @classmethod
    def methods(cls):
        return (cls.local, cls.http, cls.s3)

    @staticmethod
    def local(filename: str) -> str:
        return f"{DIR}/{filename}", fsspec.filesystem('file', **fsspec_default_args)

    @staticmethod
    def http(filename: str) -> str:
        return f"http://{HOST}:8000/{filename}", fsspec.filesystem('http', **fsspec_default_args)

    @staticmethod
    def s3(filename: str) -> str:
        return f"s3://data/{filename}", s3fs.S3FileSystem(
            anon=True, client_kwargs={"endpoint_url": f"http://{HOST}:9000"}, **fsspec_default_args)

    def setup(self):
        pass

    def run(self):
        raise NotImplemented()


@pytest.mark.parametrize("method", Fixture.methods())
def test_1_byte_overhead(benchmark, method):

    filename, fs = method("1-byte")

    class ByteFixture(Fixture):

        def setup(self):
            self.f = fs.open(filename)

        def run(self):
            self.f.read()
        
    ByteFixture(benchmark)


@pytest.mark.parametrize("method", Fixture.methods())
def test_zarr_chunk(benchmark, method):
 
    filename, fs = method(f"{BASE}.ome.zarr")

    class ZarrFixture(Fixture):

        def setup(self):
            store = zarr.storage.FSStore(
                filename,
                key_separator="/",
                **fs.storage_options)
            self.group = zarr.group(store=store)

        def run(self):
            data = self.group["0"]
            chunks = data.chunks
            len(data[0:chunks[0], 0:chunks[1], 0:chunks[2], 0:chunks[3], 0:chunks[4]])

    ZarrFixture(benchmark)


@pytest.mark.parametrize("method", Fixture.methods())
def test_tiff_tile(benchmark, method):

    filename, fs = method(f"{BASE}.ome.tiff")

    class TiffFixture(Fixture):

        def setup(self):
            self.f = fs.open(filename)

        def run(self):
            self.tif = tifffile.TiffFile(self.f)
            fh = self.tif.filehandle
            for page in self.tif.pages:
                fh.seek(page.dataoffsets[0])
                fh.read(page.databytecounts[0])
                return

    TiffFixture(benchmark)


@pytest.mark.parametrize("method", Fixture.methods())
def test_hdf5_chunk(benchmark, method):

    filename, fs = method(f"{BASE}.ims")

    class HDF5Fixture(Fixture):

       def setup(self):
            self.f = fs.open(filename)

       def run(self):
            self.ims = h5py.File(self.f)
            data = self.ims["DataSet"]["ResolutionLevel 0"]["TimePoint 0"]["Channel 0"]["Data"]
            chunks = data.chunks
            len(data[0:chunks[0], 0:chunks[1], 0:chunks[2]])

    HDF5Fixture(benchmark)
