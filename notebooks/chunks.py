#!/usr/bin/env python
import argparse
import math

import matplotlib.pyplot as plt


def file_count(shape, chunkXY, chunkZ=1, chunkT=1, chunkC=1):
    t, c, z, y, x = shape
    return (
        math.ceil(x / chunkXY)
        * math.ceil(y / chunkXY)
        * math.ceil(z / chunkZ)
        * math.ceil(t / chunkT)
        * math.ceil(c / chunkC)
    )


def plot(ax, twoD=True, font=16):
    if twoD:
        shape = (1, 8, 1, 2 ** 16, 2 ** 16)
        chunkSizesXY = [32, 1024]
        chunkSizesOther = (1, 2, 4, 8)
    else:
        shape = (100, 1, 1024, 1024, 1024)
        chunkSizesXY = (16, 32, 64, 128)
        chunkSizesOther = (1, 10, 100)

    ax.set_ylabel("Number of chunks")
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.set(xlim=(10, 2 * 10 ** 3), ylim=(10, 10 ** 8))

    if twoD:
        ax.set_xlabel("Chunk size (X and Y)")
        ax.set_title("XYZCT: (64k, 64k, 1, 8, 1)")
        chunkDim = "C"
        annTitle = "Chosen chunk size:\n(256, 256, 1, 1, 1)"
        xy = ((256), file_count(shape, 256))
    else:
        ax.set_xlabel("Chunk size (XYZ)")
        ax.set_title("XYZCT: (1k, 1k, 1k, 1, 100)")
        chunkDim = "T"
        annTitle = "Chosen chunk size:\n(32, 32, 32, 1, 1)"
        xy = ((32), file_count(shape, 32, chunkZ=32))

    for item in (
        [ax.title, ax.xaxis.label, ax.yaxis.label]
        + ax.get_xticklabels()
        + ax.get_yticklabels()
    ):
        item.set_fontsize(font)

    styles = ["solid", "dashed", "dashdot", "dotted"]
    for whichChunk, chunkOther in enumerate(chunkSizesOther):
        numFiles = []
        fileSize = []
        for i in chunkSizesXY:
            if twoD:
                count = file_count(shape, i, **{f"chunk{chunkDim}": chunkOther})
            else:
                # Could be simpler
                count = file_count(
                    shape, i, chunkZ=i, **{f"chunk{chunkDim}": chunkOther}
                )
            numFiles.append(count)
            fileSize.append(i)
        ax.plot(
            fileSize,
            numFiles,
            linewidth=0.5,
            label=f"{chunkOther}",
            linestyle=styles.pop(0),
        )

        ax.annotate(
            annTitle,
            xy=xy,
            xycoords="data",
            xytext=(0, 40),
            textcoords="offset points",
            arrowprops=dict(facecolor="black", shrink=0.05),
            horizontalalignment="left",
            verticalalignment="center",
            fontsize=font - 4,
        )
        leg = ax.legend(
            loc="lower left",
            title=f"Chunk size ({chunkDim})",
            frameon=False,
            prop={"size": font},
        )
        for legobj in leg.legendHandles:
            legobj.set_linewidth(0.5)

        for axis in ["top", "bottom", "left", "right"]:
            ax.spines[axis].set_linewidth(0.5)

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    ns = parser.parse_args()
    # fig = plt.figure()
    # ax2D = fig.add_subplot(2, 1, 1)
    # ax3D = fig.add_subplot(2, 1, 2)

    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    plot(ax[1], False)
    plot(ax[0], True)

    plt.savefig(ns.filename)
