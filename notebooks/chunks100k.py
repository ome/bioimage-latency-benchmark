from ipywidgets import *
import numpy as np
import matplotlib.pyplot as plt
import math

x = 2**15
y = 2**15
z = 1
t = 1
c = 25
chunkSizes = [32, 1024]
chunkT = 1
chunkZ = 1

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
plt.xlabel('Chunk size (X and Y)')
plt.ylabel('Number of chunks')
plt.title("XYZCT: 32k x 32k x 1 x 25 x 1")

def file_count(i, chunkC=1):
    return math.ceil(x/i) * math.ceil(y/i) * math.ceil(z/1) * math.ceil(t/1) * math.ceil(c/chunkC)


for chunkC in (1, 5, 25):
    numFiles = []
    fileSize = []
    for i in chunkSizes:
        numFiles.__iadd__([file_count(i, chunkC)])
        fileSize.__iadd__([i])
    ax.plot(fileSize, numFiles, linewidth=4.0, label=f"{chunkC}")

plt.legend(loc="lower left", title="Chunk size (C)", frameon=False)

def scale(scale):
    plt.yscale(scale)
    plt.xscale(scale)

scale('log')
ax.annotate('Chosen chunk size\nC: 1, X: 256, Y: 256',
        xy=((256), file_count(256)), xycoords='data',
        xytext=(0, 40), textcoords='offset points',
        arrowprops=dict(facecolor='black', shrink=0.05),
        horizontalalignment='left', verticalalignment='bottom')
fig.savefig("2d-chunks.png", dpi=800)
