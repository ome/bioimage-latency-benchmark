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
        shape = (1, 25, 1, 2 ** 15, 2 ** 15)
        chunkSizesXY = [32, 1024]
        chunkSizesOther = (1, 5, 25)
    else:
        shape = (100, 1, 1024, 1024, 1024)
        chunkSizesXY = (16, 32, 64, 128)
        chunkSizesOther = (1, 10, 100)

    ax.set_ylabel("Number of chunks")
    ax.set_yscale("log")
    ax.set_xscale("log")

    if twoD:
        ax.set_xlabel("Chunk size (X and Y)")
        ax.set_title("XYZCT: 32k x 32k x 1 x 25 x 1")
        chunkDim = "C"
        annTitle = "Chosen chunk size\nC: 1, X: 256, Y: 256"
        xy = ((256), file_count(shape, 256))
    else:
        ax.set_xlabel("Chunk size (XYZ)")
        ax.set_title("XYZCT: 1k x 1k x 1k x 1 x 100")
        chunkDim = "T"
        annTitle = "Chosen chunk size\nT: 1, X: 64, Y: 64, Z: 64"
        xy = ((64), file_count(shape, 64, chunkZ=64))

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
            verticalalignment="bottom",
        )
        ax.legend(loc="lower left", title=f"Chunk size ({chunkDim})", frameon=False)

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("--dpi", type=int, default=800)
    ns = parser.parse_args()
    # fig = plt.figure()
    # ax2D = fig.add_subplot(2, 1, 1)
    # ax3D = fig.add_subplot(2, 1, 2)

    fig, ax = plt.subplots(1, 2)
    plot(ax[0], True)
    plot(ax[1], False)

    plt.savefig(ns.filename, dpi=ns.dpi)
