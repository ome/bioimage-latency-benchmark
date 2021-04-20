FROM continuumio/miniconda3:4.9.2
COPY environment.yml /tmp/environment.yml
RUN conda update -n base -c defaults conda
RUN conda env create -n benchmark -f /tmp/environment.yml


# Note: docker-compose.yml mounts this file on each run
#       to prevent stale copies.
COPY benchmark.sh /benchmark/benchmark.sh
COPY benchmark.py /benchmark/benchmark.py
COPY plot_results.py /benchmark/plot_results.py

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "benchmark", "bash", "/benchmark/benchmark.sh"]
