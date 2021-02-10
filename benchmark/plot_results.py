
import json
import matplotlib.pyplot as plt
import numpy as np
import os

json_path = os.environ.get("BENCHMARK_DATA", "benchmark_data.json")
plot_path = os.environ.get("BENCHMARK_PLOT", "benchmark_plot.png")

# s3+hdf5, s3+tiff, s3+zarr, remote+hdf5, remote+… so I’d color by tiff/hdf5/zarr

named_data = {}

with open(json_path) as json_file:
    benchmarks = json.load(json_file)['benchmarks']

    for bm in benchmarks:
        label = bm['name'].replace('test_', '')
        named_data[label] = bm['stats']['data']

# print(named_data.keys())
# ['1_byte_overhead[local]', '1_byte_overhead[http]', '1_byte_overhead[boto3]', '1_byte_overhead[s3]',
# 'zarr_chunk[local]', 'zarr_chunk[http]', 'zarr_chunk[boto3]', 'zarr_chunk[s3]',
# 'tiff_tile[local]', 'tiff_tile[http]', 'tiff_tile[s3]',
# 'hdf5_chunk[local]', 'hdf5_chunk[http]', 'hdf5_chunk[s3]',
# 'download_1[local]', 'download_1[http]', 'download_1[s3]',
# 'download_2[local]', 'download_2[http]', 'download_2[boto3]', 'download_2[3fs]']

# plot [hdf5/tiff/zarr] for s3, remote, local
to_plot = [
    'hdf5_chunk[s3]', 'tiff_tile[s3]', 'zarr_chunk[s3]',
    'hdf5_chunk[http]', 'tiff_tile[http]', 'zarr_chunk[http]',
    'hdf5_chunk[local]', 'tiff_tile[local]', 'zarr_chunk[local]'
]
labels = [
    'hdf5 (s3)', 'tiff (s3)', 'zarr (s3)',
    'hdf5 (remote)', 'tiff (remote)', 'zarr (remote)',
    'hdf5 (local)', 'tiff (local)', 'zarr (local]'
]
data = [named_data[key] for key in to_plot]

def get_color(label):
    if 'hdf5' in label:
        return 'blue'
    if 'tiff' in label:
        return 'green'
    return 'pink'
colors = [get_color(label) for label in labels]

fig1, ax1 = plt.subplots(figsize=(10, 5), dpi=100)
ax1.set_title('ngff benchmark')
boxplot = ax1.boxplot(
    data,
    labels=labels,
    positions=range(len(labels), 0, -1),  # reverse order
    patch_artist=True,  # fill with color
    # showfliers=False,
    vert=False)

for color, patch in zip(colors, boxplot['boxes']):
    patch.set_facecolor(color)
    patch.set_edgecolor('grey')
for feature in ['caps', 'whiskers']:
    for line in boxplot[feature]:
        line.set_color('grey')
for line in boxplot['means']:
    line.set_color('black')
for circle in boxplot['fliers']:
    circle.set_color('grey')
ax1.set_xscale('log')
ax1.set_xlabel('Chunk loading time (secs)')

plt.tight_layout()
plt.savefig(plot_path)
