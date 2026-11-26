import { execFileSync } from "node:child_process";
import { randomUUID } from "node:crypto";
import { fileURLToPath } from "node:url";

export default function setup() {
  if (process.env.E2E_BASE_URL) return;
  const project = `helpdesk-e2e-${randomUUID()}`;
  const cwd = fileURLToPath(new URL("../../", import.meta.url));
  function compose(args, stdio = "inherit") {
    return execFileSync(
      "docker",
      [
        "compose",
        "-p",
        project,
        "--env-file",
        ".env.example",
        "-f",
        "compose.yaml",
        ...args,
      ],
      {
        cwd,
        stdio,
        encoding: "utf8",
        env: {
          ...process.env,
          WEB_PORT: "0",
          API_PORT: "0",
          POSTGRES_PORT: "0",
          COMPOSE_PROFILES: "",
          EMAIL_MODE: "DISABLED",
          TEAMS_MODE: "DISABLED",
        },
      },
    );
  }
  // O nome aleatório identifica exclusivamente o volume criado por esta execução.
  const teardown = () => compose(["down", "--volumes", "--rmi", "local"]);
  try {
    compose(["up", "-d", "--build", "--wait", "web"]);
    const address = compose(["port", "web", "80"], "pipe").trim();
    process.env.E2E_BASE_URL = `http://${address}`;
  } catch (error) {
    teardown();
    throw error;
  }
  return teardown;
}
