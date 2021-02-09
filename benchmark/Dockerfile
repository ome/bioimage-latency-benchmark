FROM continuumio/miniconda3
COPY environment.yml /tmp/environment.yml
RUN conda update -n base -c defaults conda
RUN conda env create -n benchmark -f /tmp/environment.yml
COPY benchmark.py /tmp
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "benchmark", "pytest", "/tmp/benchmark.py"]
