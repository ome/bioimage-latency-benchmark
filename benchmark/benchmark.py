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
NAME = environ.get("NAME", "data")
HOST = environ.get("HOST", "localhost")
ROUNDS = int(environ.get("ROUNDS", 10))
S3ARGS = json.loads(environ.get("S3ARGS", "{}"))
BUCKET = environ.get("BUCKET", "ngff-latency-benchmark")


fsspec_default_args = {
    "skip_instance_cache": False,
    # "use_listings_cache": False,
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
        chunks = list()
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
                            chunks.append((chunk_index,
                                          [chunk_distance, None]))

        self.chunk_choices = list()
        for idx, choice in enumerate(random.sample(chunks, ROUNDS)):
            choice[1][1] = idx
            self.chunk_choices.append(choice)

    def __iter__(self):
        return iter(self.chunk_choices)

    def pop(self):
        return self.chunk_choices.pop()


@pytest.fixture(params=ChunkChoices(), ids=range(ROUNDS))
def chunk_choice(request):
    return request.param


class Fixture:
    def __init__(self, src):
        self.src = src
        self.setup()

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
            f"s3://{BUCKET}/{NAME}/{filename}",
            s3fs.S3FileSystem(**kwargs),
        )

    def setup(self):
        pass

    def run(self, chunk_index) -> int:
        """
        Calls load and returns the chunk distance.
        """
        raise NotImplementedError()



@pytest.fixture(params=(Fixture.local, Fixture.http, Fixture.s3),
                ids=("local", "http", "s3"))
def source(request):
    return request.param


@pytest.fixture(params=("overhead", "zarr", "tiff", "hdf5"))
def file_type(request, source):

    if request.param == "overhead":

        filename, fs = source("1-byte")

        class Overhead(Fixture):
            def setup(self):
                self.f = fs.open(filename)

            def run(self, chunk_index):
                self.f.read()
                return 0

        return Overhead(source)

    elif request.param == "zarr":

        filename, fs = source(f"{BASE}.ome.zarr")

        class Zarr(Fixture):
            def setup(self):
                store = zarr.storage.FSStore(
                    filename, key_separator="/", **fs.storage_options
                )
                self.group = zarr.group(store=store)

            def run(self, chunk_index):
                data = self.group["0"]
                chunks = data.chunks
                return self.load(data, chunks, chunk_index)

        return Zarr(source)

    elif request.param == "tiff":

        filename, fs = source(f"{BASE}.ome.tiff")

        class TIFF(Fixture):
            def setup(self):
                self.f = fs.open(filename)

            def run(self, chunk_index):
                with tifffile.TiffFile(self.f) as tif:
                    store = tif.aszarr()
                    data = zarr.open(store, mode="r")
                    chunks = data.chunks
                    return self.load(data, chunks, chunk_index)

        return TIFF(source)

    elif request.param == "hdf5":

        filename, fs = source(f"{BASE}.ims")

        class HDF5(Fixture):
            def setup(self):
                self.f = fs.open(filename)
                self.file = h5py.File(self.f)

            def run(self, chunk_index):
                t, c, *idx = chunk_index
                data = self.file["DataSet"]["ResolutionLevel 0"][f"TimePoint {t-1}"][
                    f"Channel {c-1}"
                ]["Data"]
                chunks = data.chunks
                return self.load(data, chunks, idx)

        return HDF5(source)

    else:

        raise NotImplementedError(request.param)

def test_benchmark(file_type, chunk_choice, record_property):

    chunk_index, chunk_meta = chunk_choice
    chunk_distance, chunk_record = chunk_meta

    start = time.time()
    file_type.run(chunk_index)
    stop = time.time()

    record_property("source", file_type.src.__name__)
    record_property("type", file_type.__class__.__name__)
    record_property("seconds", (stop - start))
    record_property("round", chunk_record)
    record_property("chunk_index", chunk_index)
    record_property("chunk_distance", chunk_distance)
