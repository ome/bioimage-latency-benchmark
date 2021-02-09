# How to use this repository

To get started, clone this repository locally:
```
git clone https://github.com/ome/ngff-latency-benchmark.git
cd ngff-latency-benchmark
```

## Generate sample data

You will likely want to adjust the parameters in `.env` first, then run:

```
./generate.sh
```

which will run several docker-compose commands in a row. This could take
a substantial amount of time depending on your parameters.

## Or, alternatively download a sample file

```
mkdir data
cd data
../retina.sh
```

If you choose to use `retina_large`, you will also need to adjust the parameters in `.env`.


## Then, start S3 and upload the data

Start the various Docker containers.
```
docker-compose up -d
```

Once the containers are up, run:
```
docker-compose run --rm upload
```

## Finally, run the benchmark

```
docker-compose run --rm benchmark -sv
```
