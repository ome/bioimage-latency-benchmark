import { loadOmeTiff, loadOmeZarr } from "@hms-dbmi/viv";
import * as csv from "fast-csv";
import fetch from "node-fetch";

// @ts-ignore
globalThis.fetch = fetch;

// @ts-ignore
console.warn = () => {}; // disable console.warn calls in Viv's TIFF loader

let root = new URL(`http://localhost:8080/`);
let randInt = (max: number) => Math.floor(Math.random() * max);

interface ArrayMeta {
  xy: number,
  z: number,
  c: number,
  t: number,
  tilesize: number,
}

async function getArrayMeta(): Promise<ArrayMeta> {
	// use Zarr array metadata (JSON) to determine shape and tilesize
	const response = await fetch(new URL("data.zarr/0/0/.zarray", root).href);
	const meta = await response.json() as { shape: number[], chunks: number[] };
	// assumes 5D, XYZCT
	const [t, c, z, xy] = meta.shape;
	const tilesize = meta.chunks[meta.chunks.length - 1];
	return { xy, c, z, t, tilesize };
}

function getChoices({ xy, z, c, t, tilesize }: ArrayMeta, rounds: number) {
  let chunksXY = Math.floor(xy / tilesize);
  let chunkShape = [t, c, z, chunksXY, chunksXY];
  return Array.from({ length: rounds }, () => {
    let [t, c, z, y, x] = chunkShape.map(randInt);
    return { t, c, z, y, x } as const;
  });
}

async function loadSource(type: "Zarr" | "Indexed-TIFF" | "TIFF") {
  if (type === "Zarr") {
    return loadOmeZarr(new URL("data.zarr/0", root).href, { type: 'multiscales' });
  }

  let offsets: number[];
  if (type === "Indexed-TIFF") {
	let response = await fetch(new URL("data.offsets.json", root).href);
	offsets = await response.json() as number[];
  }

  return loadOmeTiff(new URL("data.ome.tif", root).href, { offsets, pool: false });
}

async function main() {
  let { env } = process;
  let rounds = Number(env.ROUNDS || 10);

  let stream = csv.format({ headers: true });
  stream.pipe(process.stdout).on("end", () => process.exit());

  // determine shape and tilesize
  let meta = await getArrayMeta();
  let choices = getChoices(meta, rounds);

  for (let type of ["TIFF", "Indexed-TIFF", "Zarr"] as const) {
    for (let [round, chunk] of choices.entries()) {
      let { data: [source] } = await loadSource(type);
      let { x, y, ...selection } = chunk;

      let start = process.hrtime();
      await source.getTile({ x, y, selection });
      let [_, ns] = process.hrtime(start);

      stream.write({
        type,
        seconds: ns * 10e-9,
        round,
        tilesize: meta.tilesize,
        name: `(XY=${meta.xy}, Z=${meta.z}, C=${meta.c}, T=${meta.t})`,
        t: selection.t + 1,
        c: selection.c + 1,
        z: selection.z + 1,
        y: y + 1,
        x: x + 1,
      });
    }
  }

  stream.end();
}

main();
