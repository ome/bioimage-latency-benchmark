How to use this repository
--------------------------

Clone this repository:
```
git clone https://github.com/ome/ngff-latency-benchmark.git
cd ngff-latency-benchmark
```

Start the various Docker containers.
```
docker-compose up
```

Open a new terminal and go to ``ngff-latency-benchmark``

Create a conda environment using [environment.yml](environment.yml) file.
```
conda env create -n ngff-latency-benchmark -f environment.yml
```
Activate the conda environment 
```
conda activate ngff-latency-benchmarking
```

Go the ``data`` directory and run the [setup.sh](setup.sh) script to generate the various imaging testing files from an IMARIS file.
```
cd data
../setup.sh
```
