import sys
import os
from pathlib import Path

envvars:
    "IDR_ID",
    "IDR_PATH",
    "IDR_NAME",
    "XY",
    "Z",
    "C",
    "T",
    "XC",
    "NAME"

DATADIR = Path.cwd().absolute() / 'data'
SOURCE = DATADIR / os.environ['IDR_ID']
TARGET = DATADIR / os.environ["NAME"]

rule plot:
	input: "benchmark_data.csv"
	output: "benchmark_plot.png"
	shell: "python ./plot_results.py {input} {output}"

rule benchmark:
	input: 
		directory(TARGET / "data.zarr"),
		TARGET / 'data.ome.tif',
		TARGET / 'data.offsets.json'
	output: "benchmark_data.csv"
	shell: "npm start --silent > {output}"

rule download:
	output: SOURCE / os.environ["IDR_NAME"]
	params:
		outdir= str(SOURCE),
		idr_id=os.environ["IDR_ID"],
		idr_path=os.environ["IDR_PATH"]
	shell: """
	docker run -ti --rm -v {params.outdir}:/data imagedata/download {params.idr_id} "{params.idr_path}" /data
	"""

rule bioformats2raw:
	output: directory(TARGET / "data.zarr")
	input: SOURCE / os.environ["IDR_NAME"]
	params: tile_size=os.environ["XC"]
	shell: """
	bioformats2raw \
		--nested \
		--compression=raw \
		-w {params.tile_size} \
		-h {params.tile_size} \
		-s=0 \
		"{input}" \
		{output}
	"""

rule raw2ometiff:
	output: TARGET / 'data.ome.tif'
	input: directory(TARGET / "data.zarr")
	params: tile_size=os.environ["XC"]
	shell: "raw2ometiff --compression=raw  {input}  {output}"

rule tiffoffsets:
	input: TARGET / 'data.ome.tif'
	output: TARGET / 'data.offsets.json'
	shell: "generate_tiff_offsets --input_file {input}"
