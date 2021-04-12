import json
import os
import re

import matplotlib.collections as clt
import matplotlib.pyplot as plt
import pandas as pd
import ptitprince as pt
import seaborn as sns

data_path = os.environ.get("BENCHMARK_DATA", "./")
plot_path = os.environ.get("BENCHMARK_PLOT", "benchmark_plot.png")
xy = os.environ.get("XY", "unknown")

csv = pd.read_csv(f"{data_path}/0_benchmark_data.csv")

types = ("Overhead", "Zarr", "TIFF", "HDF5")
sources = ("local", "http", "s3")
orders = {"type": types, "source": sources}


f, ax = plt.subplots(figsize=(8, 10))
ax = pt.RainCloud(
    x="type",
    y="seconds",
    hue="source",
    data=csv,
    palette="Set2",
    # bw = .2,
    width_viol=0.4,
    ax=ax,
    # orient = "h",
    alpha=0.65,
    # dodge = True,
    jitter=0.02,
    move=0.2,
    # pointplot = True,
)

# ax.set(ylim=(0.0002, 5))
ax.set_yscale("log")
ax.set_title("")
handles, labels = ax.get_legend_handles_labels()
plt.legend(handles[0:3], labels[0:3], loc="lower right")
plt.tight_layout()
f.savefig(plot_path, dpi=600)
1 / 0

pal_points = "colorblind"
pal_violins = "pastel"

g = sns.FacetGrid(
    csv, col="source", col_order=sources, sharey=False, height=5, aspect=0.6,
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
    "type",  # was type
    "seconds",
    dodge=True,
    order=types,
    jitter=0.2,
    size=3,
    palette=pal_points,
)

g.despine(left=True)
g.set(yscale="log", ylim=(0.0009, 1))

# Set axis labels & ticks #
for ax in g.fig.get_axes():
    label = ax.get_title().replace("source =", "")
    ax.set_xlabel(label)
    ax.set_xticklabels(types)
    ax.set_title("")
    for col in ax.collections:
        # Remove outline of violins
        col.set_edgecolor("white")

# Only show on far left plot
g.fig.get_axes()[0].set_ylabel("Seconds")
g.fig.get_axes()[0].spines["left"].set_visible(True)

# Add annotations
g.fig.get_axes()[0].text(0.0001, 0.001, "off-\nscale")

g.savefig(plot_path, dpi=600)
