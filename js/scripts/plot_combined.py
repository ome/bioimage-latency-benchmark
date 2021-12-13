#!/usr/bin/env python
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import ptitprince as pt


def plt_raincloud(ax, df, cmap):
    pt.RainCloud(
        x="type",
        y="seconds",
        hue="type",
        data=df,
        palette=cmap.name,
        width_viol=0.6,
        ax=ax,
        orient="h",
        alpha=0.65,
        jitter=0.03,
        move=0.2,
    )
    ax.legend().set_visible(False)
    ax.axes.get_yaxis().get_label().set_visible(False)
    ax.set_title(df["name"][0])
    ax.set_xscale("log")
    ax.set_xlabel("seconds per chunk")
    return ax


def scatter_channel_index(ax, df, cmap, fontsize):
    ax.set_title(df["name"][0])
    ax.set_ylabel("Z index")
    ax.set_xlabel("seconds per chunk")
    ax.set_xscale("log")

    for i in range(1, 5):
        types = list(df["type"].unique())
        subset = df[df["c"] == i]
        ax.scatter(
            subset.seconds,
            subset.z,
            marker={1: "D", 2: "o", 3: "v", 4: "x"}[i],
            c=subset["type"].map(
                {name: cmap.colors[i] for i, name in enumerate(types)}
            ),
            label=str(i),
            s=60,
        )

    ax.legend(
        *ax.get_legend_handles_labels(),
        title="C index",
        ncol=2,
        loc=(0.32, 0.65),
        fontsize=fontsize,
        title_fontsize=fontsize,
    )
    for handle in ax.get_legend().legendHandles:
        handle.set_color("black")


if __name__ == "__main__":
    font = 16
    fontlarge = 22
    cmap = plt.get_cmap("Dark2")

    results_dir = Path.cwd() / "results"
    z259 = pd.read_csv(results_dir / "XY-1920-Z-259-C-4-T-1-XC-256.csv")
    z1 = pd.read_csv(results_dir / "XY-1920-Z-1-C-4-T-1-XC-256.csv")

    f = plt.figure(constrained_layout=True, figsize=(20, 9))
    gs = f.add_gridspec(2, 2)

    top_left = f.add_subplot(gs[0, 0])
    bottom_left = f.add_subplot(gs[1, 0], sharex=top_left)
    right = f.add_subplot(gs[:, 1:2])

    plt_raincloud(top_left, z259, cmap)
    plt_raincloud(bottom_left, z1, cmap)
    handles, labels = bottom_left.get_legend_handles_labels()
    bottom_left.legend(handles[0:3], labels[0:3], loc="lower right", fontsize=fontlarge)

    scatter_channel_index(right, z259, cmap, fontsize=fontlarge)

    # bump fontsize for each element
    for ax in [top_left, bottom_left, right]:
        ax.title.set_fontsize(fontlarge)
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        for item in (
            [ax.xaxis.label, ax.yaxis.label]
            + ax.get_xticklabels()
            + ax.get_yticklabels()
        ):
            item.set_fontsize(font)

    f.savefig(results_dir / "supp_fig2.png", dpi=300, transparent=False)
