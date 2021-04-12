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


def plot(ax, twoD=True):
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
        ax.set_title("XYZCT: 64k x 64k x 1 x 8 x 1")
        chunkDim = "C"
        annTitle = "Chosen chunk size:\n256 x 256 x 1 x 1 x 1"
        xy = ((256), file_count(shape, 256))
    else:
        ax.set_xlabel("Chunk size (XYZ)")
        ax.set_title("XYZCT: 1k x 1k x 1k x 1 x 100")
        chunkDim = "T"
        annTitle = "Chosen chunk size:\n32 x 32 x 32 x 1 x 1"
        xy = ((32), file_count(shape, 32, chunkZ=32))

    for chunkOther in chunkSizesOther:
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
        ax.plot(fileSize, numFiles, linewidth=4.0, label=f"{chunkOther}")

        ax.annotate(
            annTitle,
            xy=xy,
            xycoords="data",
            xytext=(0, 40),
            textcoords="offset points",
            arrowprops=dict(facecolor="black", shrink=0.05),
            horizontalalignment="left",
            verticalalignment="center",
        )
        ax.legend(loc="lower left", title=f"Chunk size ({chunkDim})", frameon=False)

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("--dpi", type=int, default=600)
    ns = parser.parse_args()
    # fig = plt.figure()
    # ax2D = fig.add_subplot(2, 1, 1)
    # ax3D = fig.add_subplot(2, 1, 2)

    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    plot(ax[0], False)
    plot(ax[1], True)

    plt.savefig(ns.filename, dpi=ns.dpi)
