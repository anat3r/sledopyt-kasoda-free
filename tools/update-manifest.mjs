// Stamp module.json with version + distribution URLs at release time.
// Reads the tag and repo from the CI environment so you never hardcode your username.
//   RELEASE_TAG     = "v0.3.0"                      (pass from the workflow)
//   DIST_REPOSITORY = "owner/sledopyt-kasoda-dist"  (PUBLIC distribution repo — where users install from)
//   GITHUB_REPOSITORY = "owner/repo"                (fallback; the repo running the workflow)
// All public URLs (url/readme/bugs/manifest/download) point at DIST_REPOSITORY, because the
// source repo may be private — users must reach the public distribution repo instead.
// Local use: node tools/update-manifest.mjs v0.3.0 owner/sledopyt-kasoda-dist
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const file = join(ROOT, "module.json");

const tag = process.argv[2] || process.env.RELEASE_TAG || "";
const repo = process.argv[3] || process.env.DIST_REPOSITORY || process.env.GITHUB_REPOSITORY || "";
if (!tag || !repo) {
  console.error("Usage: update-manifest.mjs <tag vX.Y.Z> <owner/dist-repo>  (or set RELEASE_TAG / DIST_REPOSITORY)");
  process.exit(1);
}
const version = tag.replace(/^v/, "");
const base = `https://github.com/${repo}`;

const m = JSON.parse(readFileSync(file, "utf8"));
m.version = version;
m.url = base;
m.readme = `${base}/blob/main/README.md`;
m.bugs = `${base}/issues`;
m.manifest = `${base}/releases/latest/download/module.json`;
m.download = `${base}/releases/download/${tag}/module.zip`;

writeFileSync(file, JSON.stringify(m, null, 2) + "\n");
console.log(`module.json stamped: version=${version}`);
console.log(`  manifest = ${m.manifest}`);
console.log(`  download = ${m.download}`);
