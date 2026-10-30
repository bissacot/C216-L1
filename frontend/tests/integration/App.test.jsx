import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it } from "vitest";
import App from "../../src/App.jsx";

async function cadastrar(user, nome = "Ana Souza", email = "ana@exemplo.com") {
  await user.type(screen.getByLabelText(/Nome completo/), nome);
  await user.type(screen.getByLabelText("E-mail", { exact: false }), email);
  await user.type(
    screen.getByLabelText("Curso", { exact: false }),
    "Engenharia",
  );
  await user.click(screen.getByRole("button", { name: /Cadastrar aluno/ }));
}

it("integra cadastro, edição, cancelamento e exclusão confirmada", async () => {
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
  const user = userEvent.setup();
  render(<App />);
  await cadastrar(user);
  await cadastrar(user, "Bruno", "bruno@exemplo.com");
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

it("reinicia os cadastros em uma nova instância da página", async () => {
  const user = userEvent.setup();
  const view = render(<App />);
  await cadastrar(user);
  view.unmount();
  render(<App />);
  expect(screen.queryByText("Ana Souza")).not.toBeInTheDocument();
  expect(screen.getByText("Sua próxima turma começa aqui")).toBeVisible();
});
