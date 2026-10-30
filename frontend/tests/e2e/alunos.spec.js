import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
});

async function cadastrar(page) {
  await page.getByLabel("Nome completo").fill("Ana Souza");
  await page.getByLabel("E-mail", { exact: false }).fill("ana@exemplo.com");
  await page
    .getByLabel("Curso", { exact: false })
    .fill("Engenharia de Software");
  await page.getByRole("button", { name: /Cadastrar aluno/ }).click();
}

test("cadastra, edita e exclui com confirmação", async ({ page }) => {
  await cadastrar(page);
  await expect(page.getByRole("status")).toHaveText(
    "Aluno cadastrado com sucesso.",
  );
  await page.getByRole("button", { name: "Editar Ana Souza" }).click();
  await page.getByLabel("Nome completo").fill("Ana Silva");
  await page.getByRole("button", { name: /Salvar alterações/ }).click();
  await expect(page.getByRole("status")).toHaveText(
    "Aluno atualizado com sucesso.",
  );
  await page.getByRole("button", { name: "Excluir Ana Silva" }).click();
  await page.getByRole("button", { name: "Cancelar", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Ana Silva" })).toBeVisible();
  await page.getByRole("button", { name: "Excluir Ana Silva" }).click();
  await page.getByRole("button", { name: "Confirmar exclusão" }).click();
  await expect(page.getByRole("status")).toHaveText(
    "Aluno excluído com sucesso.",
  );
  await expect(page.getByText("Sua próxima turma começa aqui")).toBeVisible();
});

test("bloqueia formulário vazio e e-mail inválido", async ({ page }) => {
  await page.getByRole("button", { name: /Cadastrar aluno/ }).click();
  await expect(page.getByRole("alert")).toHaveCount(3);
  await page.getByLabel("Nome completo").fill("Ana");
  await page.getByLabel("Curso", { exact: false }).fill("Computação");
  await page.getByLabel("E-mail", { exact: false }).fill("invalido");
  await page.getByRole("button", { name: /Cadastrar aluno/ }).click();
  await expect(page.getByRole("alert")).toHaveText("Informe um e-mail válido.");
  await expect(
    page.getByRole("list", { name: "Alunos cadastrados" }),
  ).toHaveCount(0);
});

test("busca e reinicia os dados ao recarregar, sem persistência ou chamadas de API", async ({
  page,
}) => {
  const apiRequests = [];
  page.on("request", (request) => {
    if (["fetch", "xhr"].includes(request.resourceType()))
      apiRequests.push(request.url());
  });
  await cadastrar(page);
  await page.getByRole("searchbox").fill("inexistente");
  await expect(page.getByText("Nenhum resultado encontrado")).toBeVisible();
  await page.getByRole("searchbox").fill("ANA");
  await expect(page.getByRole("heading", { name: "Ana Souza" })).toBeVisible();
  await page.reload();
  await expect(page.getByText("Sua próxima turma começa aqui")).toBeVisible();
  expect(apiRequests).toEqual([]);
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
  await cadastrar(page);
  await page.getByRole("button", { name: "Editar Ana Souza" }).click();
  await page.getByLabel("Nome completo").fill("Descartar");
  await page.getByRole("button", { name: "Cancelar edição" }).click();
  await expect(page.getByRole("heading", { name: "Ana Souza" })).toBeVisible();
  const excluir = page.getByRole("button", { name: "Excluir Ana Souza" });
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
