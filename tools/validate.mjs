// Internal-consistency validator (no external deps; safe for CI).
// Checks: valid 16-char _id, _key format, embedded effect _key, unique ids,
// and that every internal Compendium.<this-module>.* ItemGrant/ItemChoice reference resolves.
import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, basename } from "node:path";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const SRC = join(ROOT, "src");
const MODULE = JSON.parse(readFileSync(join(ROOT, "module.json"), "utf8")).id;

const ID = /^[A-Za-z0-9]{16}$/;
const errors = [];
const docIds = new Map();      // _id -> name
const featureIds = new Set();  // ids living in the features pack
const allDocs = [];

function walk(dir) {
  for (const d of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, d.name);
    if (d.isDirectory()) walk(p);
    else if (d.name.endsWith(".json")) {
      const doc = JSON.parse(readFileSync(p, "utf8"));
      allDocs.push({ doc, pack: basename(dir), file: p });
    }
  }
}
walk(SRC);

for (const { doc, pack, file } of allDocs) {
  if (!ID.test(doc._id)) errors.push(`bad _id in ${file}`);
  if (doc._key !== `!items!${doc._id}`) errors.push(`bad _key in ${file}`);
  if (docIds.has(doc._id)) errors.push(`duplicate _id ${doc._id} (${file})`);
  docIds.set(doc._id, doc.name);
  if (pack === "features") featureIds.add(doc._id);
  for (const e of doc.effects ?? []) {
    if (!ID.test(e._id)) errors.push(`bad effect _id in ${file}`);
    if (e._key !== `!items.effects!${doc._id}.${e._id}`)
      errors.push(`bad effect _key in ${file} (${e.name})`);
  }
}

// resolve internal references (own-module features only; external UUIDs like Laaru are not checked here)
for (const { doc, file } of allDocs) {
  const advs = doc.system?.advancement ?? [];
  for (const a of advs) {
    const refs = [
      ...(a.configuration?.items ?? []),
      ...(a.configuration?.pool ?? []),
    ];
    for (const it of refs) {
      const uuid = it.uuid ?? "";
      if (uuid.includes(`Compendium.${MODULE}.features.`)) {
        const fid = uuid.split(".").pop();
        if (!featureIds.has(fid))
          errors.push(`${doc.name}: grant -> missing feature ${uuid} (${file})`);
      }
    }
  }
}

console.log(`Validated ${allDocs.length} documents across packs.`);
if (errors.length) {
  console.error(`\n${errors.length} error(s):`);
  for (const e of errors) console.error("  ✗ " + e);
  process.exit(1);
}
console.log("✓ All internal checks passed.");
