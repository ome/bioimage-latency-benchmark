import { load } from "@hms-dbmi/viv/src/loaders/tiff/ome-tiff";
import { createOffsetsProxy } from "@hms-dbmi/viv/src/loaders/tiff/lib/proxies";
import { default as ZarrPixelSource } from "@hms-dbmi/viv/src/loaders/zarr/pixel-source";

import { fromUrl } from "geotiff";
import { HTTPStore, openArray } from "zarr";

import * as csv from "fast-csv";
import fetch from "node-fetch";

import type { Labels } from "@hms-dbmi/viv/src/types";

// @ts-ignore
globalThis.fetch = fetch;

async function loadOmeTiff(href: string, offsets?: number[]) {
  let tiff = await fromUrl(href, { cacheSize: 0 });
  if (offsets) tiff = createOffsetsProxy(tiff, offsets);
  const { data: [base] } = await load(tiff);
  return base;
}

async function loadOmeZarr(href: string) {
  const store = new HTTPStore(href);
  const arr = await openArray({ store, path: "0" });
  const labels = ["t", "c", "z", "y", "x"] as Labels<["t", "c", "z"]>;
  return new ZarrPixelSource(
    arr as any,
    labels,
    arr.chunks[arr.chunks.length - 1],
  );
}

const randInt = (max: number) => Math.floor(Math.random() * max);

interface ChunkCoord {
  x: number;
  y: number;
  z: number;
  t: number;
  c: number;
}

function get_choices(
  xy: number,
  z: number,
  c: number,
  t: number,
  tile_size: number,
  rounds: number,
): [coord: ChunkCoord, chunk_distance: number][] {
  const chunks_xy = Math.floor(xy / tile_size);
  const chunk_shape = [t, c, z, chunks_xy, chunks_xy];
  return Array.from({ length: rounds }, () => {
    const [it, ic, iz, iy, ix] = chunk_shape.map(randInt);
    return [
      { t: it, c: ic, z: iz, y: iy, x: ix },
      it * z * c + ic * z + iz,
    ];
  });
}

async function loadSource(type: "Zarr" | "Indexed-TIFF" | "TIFF", root: URL) {
  if (type === "Zarr") {
    return loadOmeZarr(new URL("out/0", root).href);
  }

  let offsets: number[];
  if (type === "Indexed-TIFF") {
    const url = new URL("data.offsets.json", root);
    offsets = await fetch(url.href).then((res) => res.json()) as number[];
  }

  return loadOmeTiff(new URL("data.ome.tif", root).href, offsets);
}

async function main() {
  const name = process.env.NAME;
  const rounds = Number(process.env.ROUNDS || 10);
  const baseUrl = new URL(`http://localhost:8080/data/${name}/`);

  const stream = csv.format({ headers: true });
  stream.pipe(process.stdout).on("end", () => process.exit());

  const choices = get_choices(
    Number(process.env.XY),
    Number(process.env.Z),
    Number(process.env.C),
    Number(process.env.T),
    Number(process.env.XC),
    rounds,
  );

  for (const type of ["Zarr", "TIFF", "Indexed-TIFF"] as const) {

    for (let [round, [chunk, chunk_distance]] of choices.entries()) {
      let source = await loadSource(type, baseUrl);
      let { x, y, ...selection } = chunk;

      let start = process.hrtime();
      await source.getTile({ x, y, selection });
      let [_, ns] = process.hrtime(start);

      let { t, c, z } = selection;
      stream.write({
        type,
        seconds: ns * 10e-9,
        round,
        chunk_index: `[${t + 1}, ${c + 1}, ${z + 1}, ${y + 1}, ${x + 1}]`,
        chunk_distance,
        name,
      });
    }
  }

  stream.end();
}

main();
