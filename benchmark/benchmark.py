import time
import fsspec
import h5py
import pytest
import random
import requests
import s3fs
import tifffile
import zarr
from copy import deepcopy
from os import environ

# for product
from functools import reduce  # Required in Python 3
import operator

DIR = environ.get("DIR", "data")
BASE = environ.get("BASE", "retina_large")
HOST = environ.get("HOST", "localhost")
ROUNDS = int(environ.get("ROUNDS", 10))

fsspec_default_args = {
    "skip_instance_cache": False,
    #"use_listings_cache": False}
}


class ChunkChoices:

    def __init__(self):
        self.z = int(environ.get("Z"))
        self.t = int(environ.get("T"))
        self.zc = int(environ.get("ZC"))
        self.xy = int(environ.get("XY"))
        self.c = int(environ.get("C"))
        self.xc = int(environ.get("XC"))
        chunk_indexes = list()
        for ix in range(self.xy // self.xc):
            for iy in range(self.xy // self.xc):
                for iz in range(self.z // self.zc):
                    for ic in range(self.c):
                        for it in range(self.t):
                            chunk_indexes.append((it+1, ic+1, iz+1, iy+1, ix+1))
        self.chunk_choices = random.sample(chunk_indexes, ROUNDS)

    def pop(self):
        return self.chunk_choices.pop()


CHOICES = ChunkChoices()


class Fixture:

    def __init__(self, benchmark):
        self.choices = deepcopy(CHOICES)
        benchmark.pedantic(self.run, setup=self.setup, rounds=ROUNDS)

    def prod(self, seq):
        return reduce(operator.mul, seq, 1)

    def load(self, data, chunk_shape, chunk_index):
            X = list()  # eXtents
            for i in range(len(chunk_shape)):  # zarr=5, HDF5=3
                shape = chunk_shape[i]
                index = chunk_index[i]
                X.append(slice(shape*(index-1), shape*index))
            return len(data[tuple(X)]) == self.prod(chunk_shape)

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
        return f"s3://ngff-latency-benchmark/2048-Z-1-T-1-C-3-XYC-256-ZC-1/{filename}", s3fs.S3FileSystem(
            anon=False, **fsspec_default_args)

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
            self.load(data, chunks, self.choices.pop())

    ZarrFixture(benchmark)


@pytest.mark.parametrize("method", Fixture.methods())
def test_tiff_tile(benchmark, method):

    filename, fs = method(f"{BASE}.ome.tiff")

    class TiffFixture(Fixture):

        def setup(self):
            self.f = fs.open(filename)

        def run(self):
            with tifffile.TiffFile(self.f) as tif:
                store = tif.aszarr()
                group = zarr.group(store=store)
                data = group["0"]
                chunks = data.chunks
                self.load(data, chunks, self.choices.pop())

    TiffFixture(benchmark)


@pytest.mark.parametrize("method", Fixture.methods())
def test_hdf5_chunk(benchmark, method):

    filename, fs = method(f"{BASE}.ims")

    class HDF5Fixture(Fixture):

       def setup(self):
            self.f = fs.open(filename)
            self.file = h5py.File(self.f)

       def run(self):
            t, c, *idx = self.choices.pop()
            data = self.file["DataSet"]["ResolutionLevel 0"][f"TimePoint {t-1}"][f"Channel {c-1}"]["Data"]
            chunks = data.chunks
            self.load(data, chunks, idx)

    HDF5Fixture(benchmark)
