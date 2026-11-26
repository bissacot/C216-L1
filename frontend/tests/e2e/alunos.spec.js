import { randomUUID } from "node:crypto";
import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
});

async function cadastrar(page) {
  const suffix = randomUUID();
  const nome = `Ana Souza ${suffix}`;
  await page.getByLabel("Nome completo").fill(nome);
  await page
    .getByLabel("E-mail", { exact: false })
    .fill(`ana-${suffix}@exemplo.com`);
  await page
    .getByLabel("Curso", { exact: false })
    .fill("Engenharia de Software");
  await page.getByRole("button", { name: /Cadastrar aluno/ }).click();
  await expect(
    page.getByRole("heading", { name: nome, exact: true }),
  ).toBeVisible();
  return nome;
}

test("cadastra, edita e exclui com confirmação", async ({ page }) => {
  const nome = await cadastrar(page);
  const novoNome = nome.replace("Souza", "Silva");
  await expect(page.getByRole("status")).toHaveText(
    "Aluno cadastrado com sucesso.",
  );
  await page.getByRole("button", { name: `Editar ${nome}` }).click();
  await expect(page.getByLabel("Nome completo")).toHaveValue(nome);
  await page.getByLabel("Nome completo").fill(novoNome);
  await page.getByRole("button", { name: /Salvar alterações/ }).click();
  await expect(page.getByRole("status")).toHaveText(
    "Aluno atualizado com sucesso.",
  );
  await page.reload();
  await page.getByRole("button", { name: `Excluir ${novoNome}` }).click();
  await page.getByRole("button", { name: "Cancelar", exact: true }).click();
  await expect(page.getByRole("heading", { name: novoNome })).toBeVisible();
  await page.getByRole("button", { name: `Excluir ${novoNome}` }).click();
  await page.getByRole("button", { name: "Confirmar exclusão" }).click();
  await expect(page.getByRole("status")).toHaveText(
    "Aluno excluído com sucesso.",
  );
  await page.reload();
  await expect(
    page.getByRole("button", { name: /Cadastrar aluno/ }),
  ).toBeEnabled();
  await expect(page.getByRole("heading", { name: novoNome })).toHaveCount(0);
});

test("bloqueia formulário vazio e e-mail inválido", async ({ page }) => {
  const writes = [];
  page.on("request", (request) => {
    if (request.method() === "POST") writes.push(request.url());
  });
  await page.getByRole("button", { name: /Cadastrar aluno/ }).click();
  await expect(page.getByRole("alert")).toHaveCount(3);
  await page.getByLabel("Nome completo").fill("Ana");
  await page.getByLabel("Curso", { exact: false }).fill("Computação");
  await page.getByLabel("E-mail", { exact: false }).fill("invalido");
  await page.getByRole("button", { name: /Cadastrar aluno/ }).click();
  await expect(page.getByRole("alert")).toHaveText("Informe um e-mail válido.");
  expect(writes).toEqual([]);
});

test("busca e recupera o cadastro do PostgreSQL ao recarregar", async ({
  page,
}) => {
  const nome = await cadastrar(page);
  await page.getByRole("searchbox").fill("inexistente");
  await expect(page.getByText("Nenhum resultado encontrado")).toBeVisible();
  await page.getByRole("searchbox").fill("ANA");
  await expect(page.getByRole("heading", { name: nome })).toBeVisible();
  const [response] = await Promise.all([
    page.waitForResponse(
      (res) =>
        new URL(res.url()).pathname === "/alunos/" &&
        res.request().method() === "GET",
    ),
    page.reload(),
  ]);
  expect(response.status()).toBe(200);
  expect(await response.json()).toContainEqual(
    expect.objectContaining({ nome }),
  );
  await expect(page.getByRole("heading", { name: nome })).toBeVisible();
  expect(
    await page.evaluate(() => ({
      local: localStorage.length,
      session: sessionStorage.length,
    })),
  ).toEqual({ local: 0, session: 0 });
});

test("cancela edição e fecha confirmação com Escape mantendo o foco", async ({
  page,
}) => {
  const nome = await cadastrar(page);
  await page.getByRole("button", { name: `Editar ${nome}` }).click();
  await expect(page.getByLabel("Nome completo")).toHaveValue(nome);
  await page.getByLabel("Nome completo").fill("Descartar");
  await page.getByRole("button", { name: "Cancelar edição" }).click();
  await expect(page.getByRole("heading", { name: nome })).toBeVisible();
  const excluir = page.getByRole("button", { name: `Excluir ${nome}` });
  await excluir.click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(excluir).toBeFocused();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});
