import operator
import random
import time
from copy import deepcopy

# for product
from functools import reduce  # Required in Python 3
from os import environ

import h5py
import json
import pytest
import s3fs
import tifffile
import zarr

import fsspec

DIR = environ.get("DIR", "data")
BASE = environ.get("BASE", "retina_large")
NAME = environ.get("BASE", "data")
HOST = environ.get("HOST", "localhost")
ROUNDS = int(environ.get("ROUNDS", 10))
S3ARGS = json.loads(environ.get("S3ARGS", "{}"))

fsspec_default_args = {
    "skip_instance_cache": False,
    # "use_listings_cache": False}
}


def prod(seq):
    return reduce(operator.mul, seq, 1)


class ChunkChoices:
    def __init__(self):
        self.z = int(environ.get("Z"))
        self.t = int(environ.get("T"))
        self.zc = int(environ.get("ZC"))
        self.xy = int(environ.get("XY"))
        self.c = int(environ.get("C"))
        self.xc = int(environ.get("XC"))
        chunk_indexes = list()
        chunks_z = self.z // self.zc
        chunks_xy = self.xy // self.xc
        shape = (self.t, self.c, chunks_z, chunks_xy, chunks_xy)
        for ix in range(chunks_xy):
            for iy in range(chunks_xy):
                for iz in range(chunks_z):
                    for ic in range(self.c):
                        for it in range(self.t):
                            chunk_index = [it + 1, ic + 1, iz + 1, iy + 1, ix + 1]
                            chunk_distance = ix
                            chunk_distance += it * prod(shape[1:])
                            chunk_distance += ic * prod(shape[2:])
                            chunk_distance += iz * prod(shape[3:])
                            chunk_distance += iy * prod(shape[4:])
                            chunk_index.append(chunk_distance)
                            chunk_indexes.append(tuple(chunk_index))
        self.chunk_choices = random.sample(chunk_indexes, ROUNDS)

    def pop(self):
        return self.chunk_choices.pop()


CHOICES = ChunkChoices()


class Fixture:
    def __init__(self, src, typ, record_property):
        self.choices = deepcopy(CHOICES)
        for r in range(ROUNDS):
            self.setup()
            start = time.time()
            chunk_distance = self.run()
            stop = time.time()
            record_property("source", src.__name__)
            record_property("type", typ)
            record_property("seconds", (stop - start))
            record_property("round", r)
            record_property("chunk", chunk_distance)

    def load(self, data, chunk_shape, chunk_index):
        X = list()  # eXtents
        for i in range(len(chunk_shape)):  # zarr=5, HDF5=3
            shape = chunk_shape[i]
            index = chunk_index[i]
            X.append(slice(shape * (index - 1), shape * index))
        len(data[tuple(X)]) == prod(chunk_shape)
        return chunk_index[-1]

    @classmethod
    def methods(cls):
        return (cls.local, cls.http, cls.s3)

    @staticmethod
    def local(filename: str) -> str:
        return f"{DIR}/{filename}", fsspec.filesystem("file", **fsspec_default_args)

    @staticmethod
    def http(filename: str) -> str:
        return (
            f"http://{HOST}:8000/{filename}",
            fsspec.filesystem("http", **fsspec_default_args),
        )

    @staticmethod
    def s3(filename: str) -> str:
        kwargs = dict()
        kwargs.update(S3ARGS)
        kwargs.update(fsspec_default_args)
        return (
            f"s3://data/{filename}",
            s3fs.S3FileSystem(**kwargs),
        )

    def setup(self):
        pass

    def run(self) -> int:
        """
        Calls load and returns the chunk distance.
        """
        raise NotImplementedError()


@pytest.mark.parametrize("method", Fixture.methods())
def test_1_byte_overhead(method, record_property):

    filename, fs = method("1-byte")

    class ByteFixture(Fixture):
        def setup(self):
            self.f = fs.open(filename)

        def run(self):
            self.f.read()
            return 0

    ByteFixture(method, "overhead", record_property)


@pytest.mark.parametrize("method", Fixture.methods())
def test_zarr_chunk(method, record_property):

    filename, fs = method(f"{BASE}.ome.zarr")

    class ZarrFixture(Fixture):
        def setup(self):
            store = zarr.storage.FSStore(
                filename, key_separator="/", **fs.storage_options
            )
            self.group = zarr.group(store=store)

        def run(self):
            data = self.group["0"]
            chunks = data.chunks
            return self.load(data, chunks, self.choices.pop())

    ZarrFixture(method, "zarr", record_property)


@pytest.mark.parametrize("method", Fixture.methods())
def test_tiff_tile(method, record_property):

    filename, fs = method(f"{BASE}.ome.tiff")

    class TiffFixture(Fixture):
        def setup(self):
            self.f = fs.open(filename)

        def run(self):
            with tifffile.TiffFile(self.f) as tif:
                store = tif.aszarr()
                try:
                    group = zarr.group(store=store)
                    data = group["0"]
                except KeyError:
                    # This likely happens due to dim
                    data = zarr.open(store, mode="r")
                chunks = data.chunks
                return self.load(data, chunks, self.choices.pop())

    TiffFixture(method, "tiff", record_property)


@pytest.mark.parametrize("method", Fixture.methods())
def test_hdf5_chunk(method, record_property):

    filename, fs = method(f"{BASE}.ims")

    class HDF5Fixture(Fixture):
        def setup(self):
            self.f = fs.open(filename)
            self.file = h5py.File(self.f)

        def run(self):
            t, c, *idx = self.choices.pop()
            data = self.file["DataSet"]["ResolutionLevel 0"][f"TimePoint {t-1}"][
                f"Channel {c-1}"
            ]["Data"]
            chunks = data.chunks
            return self.load(data, chunks, idx)

    HDF5Fixture(method, "hdf5", record_property)
