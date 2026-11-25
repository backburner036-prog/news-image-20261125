// main.ts — news-image-20261125 entrypoint (Node 22, no network).
// The image is rendered by render.py (same repo) into entry.png;
// this program only verifies it and copies it to the output directory.
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoDir = dirname(fileURLToPath(import.meta.url));
const src = join(repoDir, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const out = join(outDir, "entry.png");

if (!existsSync(src)) {
  throw new Error("entry.png missing — run render.py first");
}
const size = statSync(src).size;
if (size > 1048576) {
  throw new Error(`entry.png too large: ${size} bytes (limit 1048576)`);
}
const buf = readFileSync(src);
// Minimal PNG check: signature + IHDR dimensions must be 1024x1024.
const pngSig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!buf.subarray(0, 8).equals(pngSig)) {
  throw new Error("entry.png is not a PNG");
}
const width = buf.readUInt32BE(16);
const height = buf.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png must be 1024x1024, got ${width}x${height}`);
}
mkdirSync(outDir, { recursive: true });
copyFileSync(src, out);
console.log(`wrote ${out} (${size} bytes, 1024x1024)`);
