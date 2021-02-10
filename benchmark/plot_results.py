
import json
import matplotlib.pyplot as plt
import numpy as np
import os

json_path = os.environ.get("BENCHMARK_DATA", "benchmark_data.json")
plot_path = os.environ.get("BENCHMARK_PLOT", "benchmark_plot.png")

xy = os.environ.get("XY", "unknown")

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
    'hdf5_chunk[s3]', 'tiff_tile[s3]', 'zarr_chunk[s3]', '1_byte_overhead[s3]',
    'hdf5_chunk[http]', 'tiff_tile[http]', 'zarr_chunk[http]', '1_byte_overhead[http]',
    'hdf5_chunk[local]', 'tiff_tile[local]', 'zarr_chunk[local]', '1_byte_overhead[local]',
]
labels = [
    'hdf5 (s3)', 'tiff (s3)', 'zarr (s3)', 'overhead (s3)',
    'hdf5 (remote)', 'tiff (remote)', 'zarr (remote)', 'overhead (remote)',
    'hdf5 (local)', 'tiff (local)', 'zarr (local]', 'overhead (local)',
]
data = [named_data[key] for key in to_plot]

def get_color(label):
    if 'hdf5' in label:
        return 'blue'
    elif 'tiff' in label:
        return 'green'
    elif 'overhead' in label:
        return 'yellow'
    else:
        return 'pink'
colors = [get_color(label) for label in labels]

fig1, ax1 = plt.subplots(figsize=(10, 5), dpi=100)
ax1.set_title(f'ngff benchmark ({xy}x{xy})')
ax1.set_yticklabels(labels)
vplot = ax1.violinplot(
    data,
    positions=range(len(labels), 0, -1),  # reverse order
    vert=False)

ax1.set_xscale('log')
ax1.set_xlabel('Chunk loading time (secs)')

plt.tight_layout()
plt.savefig(plot_path)
