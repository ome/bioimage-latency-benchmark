import sys
import os
from pathlib import Path

envvars:
	"IDR_ID",
	"IDR_PATH",
	"XY",
	"Z",
	"C",
	"T",
	"XC"

def get_name() -> str:
	dims = ["XY", "Z", "C", "T", "XC"]
	return "-".join(map(lambda d: f"{d}-{os.environ[d]}", dims))

DIR = Path.cwd().absolute() / "data"
NAME = get_name()

rule plot:
	input: "benchmark_data.csv"
	output: "benchmark_plot.png"
	shell: "python ./plot_results.py {input} {output}"

rule benchmark:
	input: 
		DIR / NAME / "data.zarr",
		DIR / NAME / "data.ome.tif",
		DIR / NAME / "data.offsets.json",
		"node_modules"
	output: "benchmark_data.csv"
	params:
		dir=DIR
	shell: """
	docker run --name web_server --rm -d -p 8080:80 -v {params.dir}:/usr/share/nginx/html nginx
	sleep 10
	npm start --silent > {output}; docker stop web_server
	"""

rule install_node_modules:
	output: directory("node_modules")
	shell: "npm install"

rule download:
	output: DIR / "tmp" / Path(os.environ["IDR_PATH"]).name
	params:
		outdir=DIR / "tmp",
		idr_id=os.environ["IDR_ID"],
		idr_path=os.environ["IDR_PATH"]
	shell: """
	docker run -ti --rm -v {params.outdir}:/data imagedata/download {params.idr_id} "{params.idr_path}" /data
	"""

rule bioformats2raw:
	output: directory(DIR / NAME / "data.zarr")
	input: DIR / "tmp" / Path(os.environ["IDR_PATH"]).name
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
	output: DIR / NAME / "data.ome.tif"
	input: DIR / NAME / "data.zarr"
	params: tile_size=os.environ["XC"]
	shell: "raw2ometiff --compression=raw  {input}  {output}"

rule tiffoffsets:
	input: DIR / NAME / "data.ome.tif"
	output: DIR / NAME / "data.offsets.json"
	shell: "generate_tiff_offsets --input_file {input}"
