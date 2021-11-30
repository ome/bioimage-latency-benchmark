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

HERE = Path.cwd().absolute()
NAME = get_name()

rule plot:
	input: "{dataset}.csv"
	output: "{dataset}.png"
	shell: "python ./plot_results.py {input} {output}"

rule benchmark:
	input: 
		HERE / "data" / NAME / "data.zarr",
		HERE / "data" / NAME / "data.ome.tif",
		HERE / "data" / NAME / "data.offsets.json",
		"benchmark/node_modules"
	output: "{dataset}.csv"
	params:
		dir=HERE / "data" / NAME
	shell: """
	docker run --rm \
		--name nginx-server \
		--detach \
		--publish 8080:80 \
		--volume {params.dir}:/usr/share/nginx/html:ro \
		nginx
	sleep 10
	npm --silent --prefix ./benchmark start > {output}; docker stop nginx-server
	"""

rule install_node_modules:
	output: directory("benchmark/node_modules")
	shell: "cd ./benchmark && npm install"

rule download:
	output: HERE / "data" / "tmp" / Path(os.environ["IDR_PATH"]).name
	params:
		outdir=HERE / "data" / "tmp",
		idr_id=os.environ["IDR_ID"],
		idr_path=os.environ["IDR_PATH"]
	shell: """
	docker run -ti --rm -v {params.outdir}:/data imagedata/download {params.idr_id} "{params.idr_path}" /data
	"""

rule bioformats2raw:
	output: directory(HERE / "data" / NAME / "data.zarr")
	input: HERE / "data" / "tmp" / Path(os.environ["IDR_PATH"]).name
	params: tile_size=os.environ["XC"]
	# -s=0 to extract just the first series
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
	output: HERE / "data" / NAME / "data.ome.tif"
	input: HERE / "data" / NAME / "data.zarr"
	params: tile_size=os.environ["XC"]
	shell: "raw2ometiff --compression=raw  {input}  {output}"

rule tiffoffsets:
	input: HERE / "data" / NAME / "data.ome.tif"
	output: HERE / "data" / NAME / "data.offsets.json"
	shell: "generate_tiff_offsets --input_file {input}"
