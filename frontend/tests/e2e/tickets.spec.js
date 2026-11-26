import { randomUUID } from "node:crypto";
import { expect, test } from "@playwright/test";

async function register(page, path, kind, name, email) {
  await page.goto(path);
  await page.getByRole("button", { name: `Cadastrar ${kind}` }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Nome").fill(name);
  if (email) await dialog.getByLabel("E-mail").fill(email);
  await dialog.getByRole("button", { name: "Salvar" }).click();
  await expect(dialog).toHaveCount(0);
  await page.getByRole("searchbox").fill(name);
  await page.getByRole("button", { name: "Aplicar filtros" }).click();
  await expect(page.getByRole("cell", { name, exact: true })).toBeVisible();
}

async function openTicket(page, title, person, category) {
  await page.goto("/tickets/new");
  await page.getByLabel("Título").fill(title);
  await page
    .getByLabel("Descrição")
    .fill("Verificar a conexão do laboratório.");
  await page
    .getByRole("combobox", { name: "Solicitante", exact: true })
    .selectOption({ label: person });
  await page
    .getByRole("combobox", { name: "Categoria", exact: true })
    .selectOption({ label: category });
  await page.getByRole("button", { name: "Abrir chamado" }).click();
  await expect(
    page.getByRole("heading", { name: title, exact: true }),
  ).toBeVisible();
  return new URL(page.url()).pathname;
}

test("atende, resolve e preserva um chamado e exclui um segundo cancelado", async ({
  page,
  request,
}) => {
  test.setTimeout(90000);
  const tag = randomUUID().slice(0, 8);
  const person = `Pessoa ${tag}`,
    email = `${tag}@example.invalid`;
  const category = `Laboratório ${tag}`,
    title = `Rede ${tag}`;
  const before = await (await request.get("/api/dashboard")).json();

  await page.goto("/");
  await expect(
    page.getByRole("link", { name: /Total de chamados/ }),
  ).toContainText(String(before.total));
  await register(page, "/requesters", "solicitante", person, email);
  await register(page, "/categories", "categoria", category);
  const option = `${person} · ${email}`;
  const path = await openTicket(page, title, option, category);
  const id = path.split("/").pop();

  await page.getByRole("link", { name: "Central de chamados" }).click();
  await page.getByRole("searchbox").fill(title);
  await page
    .getByRole("combobox", { name: "Status", exact: true })
    .selectOption("OPEN");
  await page
    .getByRole("combobox", { name: "Ordem", exact: true })
    .selectOption("asc");
  await page.getByRole("button", { name: "Aplicar filtros" }).click();
  await page.getByRole("link", { name: new RegExp(title) }).click();
  const deliveries = page.getByRole("article");
  await expect(deliveries).toHaveCount(2);
  await expect(deliveries.filter({ hasText: "E-mail" })).toHaveCount(1);
  await expect(deliveries.filter({ hasText: "Teams" })).toHaveCount(1);
  await page.goto(`/notifications?ticket_id=${id}&channel=TEAMS`);
  await expect(deliveries).toHaveCount(1);
  await expect(deliveries).toContainText("Teams");

  await page.goto(path);
  await page.getByRole("link", { name: "Editar chamado" }).click();
  const edited = `${title} revisada`;
  await page.getByLabel("Título").fill(edited);
  await page.getByRole("button", { name: "Salvar alterações" }).click();
  await expect(page.getByRole("heading", { name: edited })).toBeVisible();
  const dialog = page.getByRole("dialog");
  await page.getByRole("button", { name: "Iniciar atendimento" }).click();
  await dialog.getByLabel("Responsável").fill("Equipe local");
  await dialog.getByRole("button", { name: "Confirmar" }).click();
  await page.getByRole("button", { name: "Resolver chamado" }).click();
  await dialog.getByLabel("Descrição da solução").fill("Cabo substituído");
  await dialog.getByRole("button", { name: "Confirmar" }).click();
  await expect(page.getByText("Em atendimento → Resolvido")).toBeVisible();
  await page.reload();
  await expect(page.getByRole("heading", { name: edited })).toBeVisible();
  await expect(page.getByText("Aberto → Em atendimento")).toBeVisible();
  await expect(
    page.getByText("Cabo substituído", { exact: true }),
  ).toBeVisible();
  await page.goto("/");
  await expect(page.getByRole("link", { name: /Resolvidos/ })).toContainText(
    String(before.by_status.RESOLVED + 1),
  );
  await expect(
    page.getByRole("link", { name: new RegExp(edited) }),
  ).toBeVisible();

  const cancelled = await openTicket(page, `Cancelar ${tag}`, option, category);
  await expect(
    page.getByRole("button", { name: "Excluir chamado" }),
  ).toHaveCount(0);
  await page.getByRole("button", { name: "Cancelar chamado" }).click();
  await dialog.getByRole("button", { name: "Confirmar" }).click();
  await page.getByRole("button", { name: "Excluir chamado" }).click();
  await dialog.getByRole("button", { name: "Confirmar exclusão" }).click();
  await expect(
    page.getByRole("heading", { name: "Central de chamados" }),
  ).toBeVisible();
  await page.goto(cancelled);
  await expect(page.getByRole("alert")).toBeVisible();
  expect((await request.get(`/api${cancelled}`)).status()).toBe(404);
});

test("pesquisa, edita e exclui cadastros e exibe conflitos de unicidade", async ({
  page,
}) => {
  const tag = randomUUID().slice(0, 8);
  for (const [kind, path] of [
    ["solicitante", "/requesters"],
    ["categoria", "/categories"],
  ]) {
    const name = `Cadastro ${tag}`,
      updated = `${name} atualizado`;
    await register(
      page,
      path,
      kind,
      name,
      kind === "solicitante" ? `${tag}@example.invalid` : undefined,
    );
    const dialog = page.getByRole("dialog");
    await page.getByRole("button", { name: `Cadastrar ${kind}` }).click();
    await dialog.getByLabel("Nome").fill(name);
    if (kind === "solicitante")
      await dialog.getByLabel("E-mail").fill(`${tag}@example.invalid`);
    await dialog.getByRole("button", { name: "Salvar" }).click();
    await expect(dialog.getByRole("alert")).toContainText("Já existe");
    await dialog.getByRole("button", { name: "Voltar" }).click();
    await page.getByRole("button", { name: `Editar ${name}` }).click();
    await dialog.getByLabel("Nome").fill(updated);
    await dialog.getByRole("button", { name: "Salvar" }).click();
    await page.getByRole("button", { name: `Excluir ${updated}` }).click();
    await dialog.getByRole("button", { name: "Confirmar exclusão" }).click();
    await expect(page.getByText("Nenhum cadastro encontrado")).toBeVisible();
  }
});

test("ordena e pagina chamados filtrados no PostgreSQL", async ({
  page,
  request,
}) => {
  const tag = randomUUID().slice(0, 8);
  async function create(path, data) {
    const response = await request.post(`/api/${path}`, { data });
    expect(response.status()).toBe(201);
    return response.json();
  }
  const person = await create("requesters", {
    name: tag,
    email: `${tag}@example.invalid`,
  });
  const category = await create("categories", { name: tag });
  for (let index = 1; index <= 11; index++) {
    await create("tickets", {
      title: `${tag} ${String(index).padStart(2, "0")}`,
      description: "Paginação",
      requester_id: person.id,
      category_id: category.id,
      priority: "HIGH",
    });
  }
  await page.goto("/tickets");
  await page.getByRole("searchbox").fill(tag);
  const select = (name) => page.getByRole("combobox", { name, exact: true });
  await select("Categoria").selectOption(String(category.id));
  await select("Solicitante").selectOption(String(person.id));
  await select("Prioridade").selectOption("HIGH");
  await select("Ordenar por").selectOption("title");
  await select("Ordem").selectOption("asc");
  await page.getByRole("button", { name: "Aplicar filtros" }).click();
  const rows = page.locator("tbody tr");
  await expect(rows).toHaveCount(10);
  await expect(rows.first()).toContainText(`${tag} 01`);
  await page.getByRole("button", { name: "Próxima página" }).click();
  await expect(rows).toHaveCount(1);
  await expect(rows.first()).toContainText(`${tag} 11`);
  await page.reload();
  await expect(page.getByText("Página 2 de 2")).toBeVisible();
  await select("Ordem").selectOption("desc");
  await page.getByRole("button", { name: "Aplicar filtros" }).click();
  await expect(page.getByText("Página 1 de 2")).toBeVisible();
  await expect(rows.first()).toContainText(`${tag} 11`);
});
