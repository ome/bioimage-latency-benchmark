
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import seaborn as sns
from collections import defaultdict

json_path = os.environ.get("BENCHMARK_DATA", "benchmark_data")
plot_path = os.environ.get("BENCHMARK_PLOT", "benchmark_plot.png")

xy = os.environ.get("XY", "unknown")

# s3+hdf5, s3+tiff, s3+zarr, remote+hdf5, remote+… so I’d color by tiff/hdf5/zarr

print('base_path', json_path)


three_col = []
two_col = []

test_repeats = int(os.getenv('TEST_REPEATS', "1"))
json_files = ["%s_benchmark_data.json" % r for r in range(test_repeats)]
print('json_files', json_files)

for root, dirs, files in os.walk(json_path):
    for file_name in files:
        if file_name in json_files:
            path = os.path.join(root, file_name)
            print('json path', path)
            with open(path) as json_file:
                benchmarks = json.load(json_file)['benchmarks']

                for bm in benchmarks:
                    m = re.match(r"test_(1_byte|\w+)_(\w+)\[(\w+)\]", bm['name'])
                    if not m:
                        raise Exception(bm['name'])
                    typ = m.group(1).replace("1_byte", "overhead")
                    src = m.group(3)

                    if typ == "overhead" and src == "local":
                        # 10e-5 skews the view.
                        continue

                    if test_repeats == 1:
                        # Ran tests once: plot every data point
                        vals = bm['stats']['data']
                        for run, val in enumerate(vals):
                            three_col.append(
                                {
                                    "type": typ,
                                    "source": src,
                                    "seconds": val,
                                }
                            )
                            two_col.append(
                                {
                                    "name": f"{typ}-{src}",
                                    "seconds": val,
                                }
                            )
                    else:
                        # Repeats: take mean value from each
                        val = bm['stats']['mean']
                        three_col.append(
                            {
                                "type": typ,
                                "source": src,
                                "seconds": val,
                            }
                        )
                        two_col.append(
                            {
                                "name": f"{typ}-{src}",
                                "seconds": val,
                            }
                        )

df3 = pd.DataFrame.from_dict(three_col)
df2 = pd.DataFrame.from_dict(two_col)

types = ("overhead", "zarr", "tiff", "hdf5")
sources = ("local", "http", "s3")
orders = {"type": types, "source": sources}

pal_points = "colorblind"
pal_violins = "pastel"

g = sns.FacetGrid(
    df3,
    col="source",
    col_order=sources,
    sharey=False,
    height=5,
    aspect=0.6,
)

g = g.map(
    sns.boxenplot,
    "type",
    "seconds",
    order=types,
    width=0.6,
    k_depth=2,
    palette=pal_violins,
    dodge=True,
    showfliers=False,
)

g = g.map(
    sns.stripplot,
    "type",
    "seconds",
    dodge=True,
    order=types,
    jitter=0.2,
    size=3,
    palette=pal_points,
)

g.despine(left=True)
g.set(yscale ='log', ylim=(0.00001, 1.5))

# Set axis labels & ticks #
for ax in g.fig.get_axes():
    label = ax.get_title().replace("source =", "")
    ax.set_xlabel(label)
    ax.set_xticklabels(types)
    ax.set_title("")
    for col in ax.collections:
        # Remove outline of violins
        col.set_edgecolor("white")

g.fig.get_axes()[0].set_ylabel("Seconds")
g.fig.get_axes()[0].spines["left"].set_visible(True)

g.savefig(plot_path, dpi=600)
