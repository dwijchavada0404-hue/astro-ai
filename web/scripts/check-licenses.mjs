import { readFile } from "node:fs/promises";

const lock = JSON.parse(await readFile(new URL("../node_modules/.package-lock.json", import.meta.url), "utf8"));
const blocked = /(?:^|[-,(\s])(AGPL|GPL|SSPL)(?:[-),\s]|$)/i;
const failures = [];

for (const [path, metadata] of Object.entries(lock.packages || {})) {
  if (!path || !path.startsWith("node_modules/")) continue;
  const license = typeof metadata.license === "string" ? metadata.license.trim() : "";
  if (!license) failures.push(`${path}: missing license metadata`);
  else if (blocked.test(license)) failures.push(`${path}: ${license} requires explicit review`);
}

if (failures.length) {
  console.error(`Frontend dependency license check failed:\n${failures.join("\n")}`);
  process.exit(1);
}

console.log(`Checked ${Object.keys(lock.packages || {}).length - 1} frontend dependency packages.`);
