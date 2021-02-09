
import json
import matplotlib.pyplot as plt
import numpy as np

json_path = ".benchmarks/Darwin-CPython-3.9-64bit/0005_ngff_benchmark.json"



with open(json_path) as json_file:
    benchmarks = json.load(json_file)['benchmarks']

    data = [bm['stats']['data'] for bm in benchmarks]
    labels = [bm['name'].replace('test_', '') for bm in benchmarks]


fig1, ax1 = plt.subplots(figsize=(10, 5), dpi=100)
ax1.set_title('ngff benchmark')
boxplot = ax1.boxplot(data,
    labels=labels,
    patch_artist=True,  # fill with color
    vert=False)
for patch in boxplot['boxes']:
    patch.set_facecolor('blue')
ax1.set_xscale('log')
ax1.set_xlabel('Chunk loading time (secs)')

plt.tight_layout()
plt.savefig('benchmark_plot.png')
