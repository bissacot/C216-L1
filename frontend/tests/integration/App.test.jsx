import { act, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import App from "../../src/App.jsx";

const ana = {
  id: 23,
  nome: "Ana Souza",
  email: "ana@exemplo.com",
  curso: "Engenharia",
};
const bruno = { ...ana, id: 87, nome: "Bruno", email: "bruno@exemplo.com" };
const editada = { ...ana, nome: "Ana Silva" };
const http = vi.fn();
const responder = (body, status = 200) =>
  http.mockResolvedValueOnce(
    body === null
      ? new Response(null, { status })
      : Response.json(body, { status }),
  );

beforeEach(() => {
  http.mockReset();
  vi.stubGlobal("fetch", http);
  responder([]);
});
afterEach(() => vi.unstubAllGlobals());

async function cadastrar(user, { nome, email } = ana) {
  await waitFor(() =>
    expect(screen.getByLabelText(/Nome completo/)).toBeEnabled(),
  );
  await user.type(screen.getByLabelText(/Nome completo/), nome);
  await user.type(screen.getByLabelText("E-mail", { exact: false }), email);
  await user.type(
    screen.getByLabelText("Curso", { exact: false }),
    "Engenharia",
  );
  await user.click(screen.getByRole("button", { name: /Cadastrar aluno/ }));
}

it("integra cadastro, edição, cancelamento e exclusão confirmada", async () => {
  responder(ana, 201);
  responder(ana);
  responder(editada);
  responder(null, 204);
  const user = userEvent.setup();
  render(<App />);
  await cadastrar(user);
  expect(screen.getByRole("status")).toHaveTextContent(
    "Aluno cadastrado com sucesso.",
  );
  await user.click(screen.getByRole("button", { name: "Editar Ana Souza" }));
  await user.clear(screen.getByLabelText(/Nome completo/));
  await user.type(screen.getByLabelText(/Nome completo/), "Ana Silva");
  await user.click(screen.getByRole("button", { name: /Salvar alterações/ }));
  expect(screen.getByText("Ana Silva")).toBeVisible();
  expect(screen.getByRole("status")).toHaveTextContent(
    "Aluno atualizado com sucesso.",
  );
  await user.click(screen.getByRole("button", { name: "Excluir Ana Silva" }));
  await user.click(
    within(screen.getByRole("dialog")).getByRole("button", {
      name: "Cancelar",
      exact: true,
    }),
  );
  expect(screen.getByText("Ana Silva")).toBeVisible();
  await user.click(screen.getByRole("button", { name: "Excluir Ana Silva" }));
  await user.click(screen.getByRole("button", { name: "Confirmar exclusão" }));
  expect(screen.queryByText("Ana Silva")).not.toBeInTheDocument();
  expect(screen.getByRole("status")).toHaveTextContent(
    "Aluno excluído com sucesso.",
  );
});

it("filtra por nome, e-mail e curso sem remover dados", async () => {
  responder(ana, 201);
  const user = userEvent.setup();
  render(<App />);
  await cadastrar(user);
  const search = screen.getByRole("searchbox");
  for (const query of ["ANA", "ana@", "engenharia"]) {
    await user.clear(search);
    await user.type(search, query);
    expect(screen.getByText("Ana Souza")).toBeVisible();
  }
  await user.clear(search);
  await user.type(search, "inexistente");
  expect(screen.getByText("Nenhum resultado encontrado")).toBeVisible();
  await user.clear(search);
  expect(screen.getByText("Ana Souza")).toBeVisible();
});

it("descarta edição cancelada e mantém os outros alunos ao excluir", async () => {
  responder(ana, 201);
  responder(bruno, 201);
  responder(ana);
  responder(null, 204);
  const user = userEvent.setup();
  render(<App />);
  await cadastrar(user);
  await cadastrar(user, bruno);
  await user.click(screen.getByRole("button", { name: "Editar Ana Souza" }));
  await user.clear(screen.getByLabelText(/Nome completo/));
  await user.type(screen.getByLabelText(/Nome completo/), "Descartar");
  await user.click(screen.getByRole("button", { name: "Cancelar edição" }));
  expect(screen.getByText("Ana Souza")).toBeVisible();
  expect(screen.getByLabelText(/Nome completo/)).toHaveValue("");
  await user.click(screen.getByRole("button", { name: "Excluir Ana Souza" }));
  await user.click(screen.getByRole("button", { name: "Confirmar exclusão" }));
  expect(screen.getByText("Bruno")).toBeVisible();
});

it("consulta a API novamente ao abrir uma nova instância da página", async () => {
  responder(ana, 201);
  responder([ana]);
  const user = userEvent.setup();
  const view = render(<App />);
  await cadastrar(user);
  view.unmount();
  render(<App />);
  expect(await screen.findByText("Ana Souza")).toBeVisible();
  expect(http).toHaveBeenLastCalledWith(
    expect.stringMatching(/\/alunos\/$/),
    expect.objectContaining({ method: "GET" }),
  );
});

it("indica carregamento até a listagem responder", async () => {
  let resolve;
  http.mockReset().mockReturnValueOnce(
    new Promise((done) => {
      resolve = done;
    }),
  );
  render(<App />);
  expect(screen.getByRole("status")).toHaveTextContent("Carregando alunos");
  expect(
    screen.getByRole("button", { name: /Cadastrar aluno/ }),
  ).toBeDisabled();
  await act(async () => resolve(Response.json([ana])));
  expect(screen.getByText(ana.nome)).toBeVisible();
});

it("permite repetir a consulta quando a API está indisponível", async () => {
  http.mockReset().mockRejectedValueOnce(new TypeError("Failed to fetch"));
  responder([ana]);
  render(<App />);
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Não foi possível conectar à API",
  );
  expect(
    screen.queryByText("Sua próxima turma começa aqui"),
  ).not.toBeInTheDocument();
  await userEvent.click(
    screen.getByRole("button", { name: /Tentar carregar/ }),
  );
  expect(await screen.findByText(ana.nome)).toBeVisible();
});

it("preserva os valores após validação HTTP 422 e permite corrigir o cadastro", async () => {
  responder(
    { detail: [{ loc: ["body", "email"], msg: "Invalid input" }] },
    422,
  );
  responder(ana, 201);
  const user = userEvent.setup();
  render(<App />);
  await cadastrar(user);
  expect(await screen.findByRole("alert")).toHaveTextContent("E-mail");
  expect(screen.getByLabelText(/Nome completo/)).toHaveValue(ana.nome);
  expect(
    screen.queryByRole("heading", { name: ana.nome }),
  ).not.toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: /Cadastrar aluno/ }));
  expect(await screen.findByText(ana.nome)).toBeVisible();
});

it("mantém o aluno na lista quando a consulta ou exclusão falha", async () => {
  http.mockReset();
  responder([ana]);
  responder({ detail: "Aluno não encontrado" }, 404);
  http.mockResolvedValueOnce(
    new Response("Internal Server Error", { status: 500 }),
  );
  render(<App />);
  await userEvent.click(
    await screen.findByRole("button", { name: `Editar ${ana.nome}` }),
  );
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Aluno não encontrado",
  );
  await userEvent.click(
    screen.getByRole("button", { name: `Excluir ${ana.nome}` }),
  );
  const dialog = within(screen.getByRole("dialog"));
  await userEvent.click(
    dialog.getByRole("button", { name: "Confirmar exclusão" }),
  );
  expect(await dialog.findByRole("alert")).toHaveTextContent("HTTP 500");
  await userEvent.click(dialog.getByRole("button", { name: "Cancelar" }));
  expect(screen.getByRole("heading", { name: ana.nome })).toBeVisible();
});
