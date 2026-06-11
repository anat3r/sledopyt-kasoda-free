// Compile src/<pack>/*.json -> packs/<pack> (LevelDB) using the official Foundry CLI.
import { compilePack } from "@foundryvtt/foundryvtt-cli";
import { readdirSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const SRC = join(ROOT, "src");
const OUT = join(ROOT, "packs");

const packs = readdirSync(SRC, { withFileTypes: true })
  .filter((d) => d.isDirectory())
  .map((d) => d.name);

if (existsSync(OUT)) rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });

for (const p of packs) {
  await compilePack(join(SRC, p), join(OUT, p), { log: true });
  console.log(`packed ${p}`);
}
console.log("Done.");
