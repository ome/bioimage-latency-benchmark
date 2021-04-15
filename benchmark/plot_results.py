#!/usr/bin/env python
import argparse

import matplotlib.pyplot as plt
import pandas as pd
import ptitprince as pt


def plot_csv(filename: str, pngpath: str):
    csv = pd.read_csv(filename)

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
    f.savefig(pngpath, dpi=600)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", help="input csv file")
    parser.add_argument("png", help="output png file")
    ns = parser.parse_args()
    plot_csv(ns.csv, ns.png)
