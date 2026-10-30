import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import AlunoList from "../../src/components/AlunoList.jsx";

it("orienta o cadastro inicial", () => {
  render(<AlunoList alunos={[]} hasAlunos={false} />);
  expect(screen.getByText("Sua próxima turma começa aqui")).toBeVisible();
});

it("mostra os dados e direciona as ações ao aluno correto", async () => {
  const aluno = {
    id: 1,
    nome: "Ana",
    email: "ana@exemplo.com",
    curso: "Computação",
  };
  const onEdit = vi.fn();
  const onDelete = vi.fn();
  render(
    <AlunoList
      alunos={[aluno]}
      hasAlunos
      onEdit={onEdit}
      onDelete={onDelete}
    />,
  );
  expect(screen.getByText(aluno.email)).toBeVisible();
  await userEvent.click(screen.getByRole("button", { name: "Editar Ana" }));
  await userEvent.click(screen.getByRole("button", { name: "Excluir Ana" }));
  expect(onEdit).toHaveBeenCalledWith(aluno);
  expect(onDelete).toHaveBeenCalledWith(aluno);
});
