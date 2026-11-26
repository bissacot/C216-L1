import { spawnSync } from "node:child_process";
import { randomUUID } from "node:crypto";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const frontend = fileURLToPath(new URL("../../", import.meta.url));
const root = fileURLToPath(new URL("../../../", import.meta.url));
const playwright = createRequire(import.meta.url).resolve(
  "@playwright/test/cli",
);
const composeArgs = [
  "compose",
  "-p",
  `c216-e2e-${randomUUID()}`,
  "-f",
  "docker-compose.yml",
  "-f",
  "docker-compose.e2e.yml",
];

function run(command, args, cwd) {
  const result = spawnSync(command, args, { cwd, stdio: "inherit" });
  if (result.error) console.error(result.error.message);
  return result.status ?? 1;
}

function compose(...args) {
  return run("docker", [...composeArgs, ...args], root);
}

try {
  process.exitCode = compose(
    "up",
    "--build",
    "-d",
    "--wait",
    "--wait-timeout",
    "120",
  );
  if (process.exitCode === 0) {
    process.exitCode = run(
      process.execPath,
      [playwright, "test", ...process.argv.slice(2)],
      frontend,
    );
  }
  if (process.exitCode !== 0) compose("logs", "--tail", "80");
} finally {
  const cleanup = compose("down", "--rmi", "local");
  if (cleanup !== 0) process.exitCode = cleanup;
}
