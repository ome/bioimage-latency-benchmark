import requests
import zarr
import time
import pytest
import s3fs
import boto3
import h5py
from botocore import UNSIGNED
from botocore.client import Config


fs = s3fs.S3FileSystem(
    anon=True,
    client_kwargs={
        'endpoint_url': 'http://localhost:9000'
    }
)

b3 = boto3.client(
    's3',
    endpoint_url="http://localhost:9000",
    config=Config(signature_version=UNSIGNED)
)

def local(filename):
    start = time.time()
    with open(f"data/{filename}", "rb") as o:
        o.read()
    stop = time.time()
    return stop - start

def http(filename):
    elapsed = requests.get(f"http://localhost:8000/{filename}").elapsed
    return elapsed.microseconds / 1000000

def boto3(filename):
    start = time.time()
    content = b3.get_object(Bucket="data", Key=filename)
    stop = time.time()
    return stop - start

def s3fs(filename):
    start = time.time()
    with fs.open(f"data/{filename}") as f:
       f.read()
    stop = time.time()
    return stop -start

@pytest.mark.parametrize("method", (local, http, boto3, s3fs))
def test_1_byte_overhead(benchmark, method):
    benchmark(method, "1-byte")

@pytest.mark.parametrize("method", (local, http, boto3, s3fs))
def test_chunk(benchmark, method):
    benchmark(method, "a.ome.zarr/0/0.0.0.0.0")

@pytest.mark.parametrize("method", (local, http, boto3, s3fs))
def test_chunk(benchmark, method):
    benchmark(method, "a.ome.zarr/0/0.0.0.0.0")
