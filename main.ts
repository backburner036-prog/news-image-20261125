// main.ts — news-image-20261125 entrypoint (Node 22, no network).
//
// render.py draws the front page into entry.png next to this file; this
// program only checks that image and copies it to the output directory
// make.fun grades (MAKEFUN_OUTPUT_DIR, or /output by default).
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  statSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const LIMIT_BYTES = 1048576;
const SIDE = 1024;

function fail(message: string): never {
  throw new Error(`entry.png rejected: ${message}`);
}

function checkPng(buf: Buffer): void {
  const signature = Buffer.from([
    0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
  ]);
  if (!buf.subarray(0, 8).equals(signature)) {
    fail("not a PNG file");
  }
  const width = buf.readUInt32BE(16);
  const height = buf.readUInt32BE(20);
  if (width !== SIDE || height !== SIDE) {
    fail(`must be ${SIDE}x${SIDE}, got ${width}x${height}`);
  }
}

function main(): void {
  const here = dirname(fileURLToPath(import.meta.url));
  const src = join(here, "entry.png");
  if (!existsSync(src)) {
    fail("missing — run render.py first");
  }
  const bytes = statSync(src).size;
  if (bytes > LIMIT_BYTES) {
    fail(`${bytes} bytes exceeds the ${LIMIT_BYTES} byte limit`);
  }
  checkPng(readFileSync(src));
  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
  mkdirSync(outDir, { recursive: true });
  const dest = join(outDir, "entry.png");
  copyFileSync(src, dest);
  console.log(`wrote ${dest} (${bytes} bytes, ${SIDE}x${SIDE})`);
}

main();
