
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import seaborn as sns
from collections import defaultdict

json_path = os.environ.get("BENCHMARK_DATA", "benchmark_data")
plot_path = os.environ.get("BENCHMARK_PLOT", "benchmark_plot.png")

xy = os.environ.get("XY", "unknown")

# s3+hdf5, s3+tiff, s3+zarr, remote+hdf5, remote+… so I’d color by tiff/hdf5/zarr

print('base_path', json_path)


named_data = []


test_repeats = int(os.getenv('TEST_REPEATS', "1"))
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
                    m = re.match(r"test_(1_byte|\w+)_(\w+)\[(\w+)\]", bm['name'])
                    if not m:
                        raise Exception(bm['name'])
                    typ = m.group(1).replace("1_byte", "overhead")
                    src = m.group(3)
                    
                    if test_repeats == 1:
                        # Ran tests once: plot every data point
                        vals = bm['stats']['data']
                        for run, val in enumerate(vals):
                            named_data.append(
                                {
                                    "type": typ,
                                    "source": src,
                                    "milliseconds": val,
                                }
                        )
                    else:
                        # Repeats: take mean value from each
                        named_data.append(
                            {
                                "type": typ,
                                "source": src,
                                "milliseconds": bm['stats']['mean'],
                            }
                        )

df = pd.DataFrame.from_dict(named_data)
sns.set(style="ticks", palette="colorblind")
g = sns.FacetGrid(df, col="source", size=8, aspect=0.5)
g = g.map(sns.violinplot, "type", "milliseconds",
#          inner=None, linewidth=1,
#          scale="area", split=True, width=0.75
)
g.set(yscale ='log', ylim=(0.000001, 1))
g.despine(left=True)
g.add_legend(title="Latency")
g.savefig(plot_path)
