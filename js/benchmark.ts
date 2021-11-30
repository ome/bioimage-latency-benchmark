import { loadOmeTiff, loadOmeZarr } from "@hms-dbmi/viv";
import * as csv from "fast-csv";
import fetch from "node-fetch";

// @ts-ignore
globalThis.fetch = fetch;

// @ts-ignore
console.warn = () => {}; // disable console.warn calls in Viv's TIFF loader

let randInt = (max: number) => Math.floor(Math.random() * max);

function getChoices(
  xy: number,
  z: number,
  c: number,
  t: number,
  tileSize: number,
  rounds: number,
) {
  let chunksXY = Math.floor(xy / tileSize);
  let chunkShape = [t, c, z, chunksXY, chunksXY];
  return Array.from({ length: rounds }, () => {
    let [t, c, z, y, x] = chunkShape.map(randInt);
    return { t, c, z, y, x } as const;
  });
}

async function loadSource(type: "Zarr" | "Indexed-TIFF" | "TIFF", root: URL) {
  if (type === "Zarr") {
    return loadOmeZarr(new URL("data.zarr/0", root).href, { type: 'multiscales' });
  }

  let offsets: number[];
  if (type === "Indexed-TIFF") {
    let url = new URL("data.offsets.json", root);
    offsets = await fetch(url.href).then((res) => res.json()) as number[];
  }

  return loadOmeTiff(new URL("data.ome.tif", root).href, { offsets, pool: false });
}

async function main() {
  let { env } = process;
  let name = `XY-${env.XY}-Z-${env.Z}-C-${env.C}-T-${env.T}-XC-${env.XC}`;
  let rounds = Number(env.ROUNDS || 10);
  let baseUrl = new URL(`http://localhost:8080/${name}/`);

  let stream = csv.format({ headers: true });
  stream.pipe(process.stdout).on("end", () => process.exit());

  let choices = getChoices(
    Number(env.XY),
    Number(env.Z),
    Number(env.C),
    Number(env.T),
    Number(env.XC),
    rounds,
  );

  for (let type of ["Zarr", "TIFF", "Indexed-TIFF"] as const) {
    for (let [round, chunk] of choices.entries()) {
      let { data: [source] } = await loadSource(type, baseUrl);
      let { x, y, ...selection } = chunk;

      let start = process.hrtime();
      await source.getTile({ x, y, selection });
      let [_, ns] = process.hrtime(start);

      stream.write({
        type,
        seconds: ns * 10e-9,
        round,
        name,
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
