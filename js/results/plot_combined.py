#!/usr/bin/env python
import argparse

import matplotlib.pyplot as plt
import pandas as pd
import ptitprince as pt

def fmt_name(name: pd.Series) -> pd.Series:
    split = name.str.split('-').str
    return "(X=" + split[1] + ", Y=" + split[1] + ", Z=" + split[3] + ", C=" + split[5] + ", T=" + split[7] + ")"

def plot_combined(
    files: list[str],
    outpath: str,
    font: int = 14,
    width: int = 10,
    height: int = 4,
):
    csv = pd.concat(map(pd.read_csv, files))
    csv.name = fmt_name(csv.name)
    csv.type = csv.type.map({
        'Zarr': 'OME-NGFF (Zarr)',
        'TIFF': 'OME-TIFF',
        'Indexed-TIFF', 'Indexed OME-TIFF',
    })

    f, ax = plt.subplots(figsize=(width, height))
    ax = pt.RainCloud(
        x="name",
        y="seconds",
        hue="type",
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
    for item in (
        [ax.title, ax.xaxis.label, ax.yaxis.label]
        + ax.get_xticklabels()
        + ax.get_yticklabels()
    ):
        item.set_fontsize(font)

    ax.axes.get_yaxis().get_label().set_visible(False)
    handles, labels = ax.get_legend_handles_labels()
    plt.legend(handles[0:3], labels[0:3], loc="lower right", prop={"size": font})
    plt.tight_layout()
    f.savefig(outpath)


if __name__ == "__main__":
    import sys
    plot_combined(sys.argv[1:], 'combined.png')
