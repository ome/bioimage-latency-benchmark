import os

import matplotlib.pyplot as plt
import pandas as pd
import ptitprince as pt

data_path = os.environ.get("BENCHMARK_DATA", "./")
plot_path = os.environ.get("BENCHMARK_PLOT", "benchmark_plot.png")
xy = os.environ.get("XY", "unknown")

csv = pd.read_csv(f"{data_path}/0_benchmark_data.csv")

types = ("Overhead", "Zarr", "TIFF", "HDF5")
sources = ("local", "http", "s3")
orders = {"type": types, "source": sources}


f, ax = plt.subplots(figsize=(8, 6))
ax = pt.RainCloud(
    x="type",
    y="seconds",
    hue="source",
    data=csv,
    palette="Set2",
    # bw = .2,
    width_viol=0.6,
    ax=ax,
    orient="h",
    alpha=0.65,
    # dodge = True,
    jitter=0.03,
    move=0.2,
    # pointplot = True,
)

# ax.set(ylim=(0.0002, 5))
ax.set_xscale("log")
ax.set_xlabel("seconds per chunk")
ax.axes.get_yaxis().get_label().set_visible(False)
handles, labels = ax.get_legend_handles_labels()
plt.legend(handles[0:3], labels[0:3], loc="lower left")
plt.tight_layout()
f.savefig(plot_path, dpi=600)
