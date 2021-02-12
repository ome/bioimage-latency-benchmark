
import json
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import defaultdict

json_path = os.environ.get("BENCHMARK_DATA", "benchmark_data")
plot_path = os.environ.get("BENCHMARK_PLOT", "benchmark_plot.png")

xy = os.environ.get("XY", "unknown")

# s3+hdf5, s3+tiff, s3+zarr, remote+hdf5, remote+… so I’d color by tiff/hdf5/zarr

print('base_path', json_path)

named_data = defaultdict(list)


test_repeats = int(os.getenv('TEST_REPEATS'))
json_files = ["%s_benchmark_data.json" % r for r in range(test_repeats)]
print('json_files', json_files)

for root, dirs, files in os.walk(json_path):
    for file_name in files:
        if file_name in json_files:
            path = os.path.join(root, file_name)
            print('json path', path)
            with open(path) as json_file:
                benchmarks = json.load(json_file)['benchmarks']

                for bm in benchmarks:
                    label = bm['name'].replace('test_', '')
                    if test_repeats == 1:
                        # Ran tests once: plot every data point
                        named_data[label] = bm['stats']['data']
                    else:
                        # Repeats: take mean value from each
                        named_data[label].append(bm['stats']['mean'])


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
ax1.set_title(f'ngff benchmark ({xy}x{xy}) n={test_repeats}')
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
