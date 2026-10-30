import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import AlunoForm from "../../src/components/AlunoForm.jsx";

it("exibe erros, foca o primeiro campo e impede envio inválido", async () => {
  const onSave = vi.fn();
  render(<AlunoForm onSave={onSave} />);
  await userEvent.click(
    screen.getByRole("button", { name: /Cadastrar aluno/ }),
  );
  expect(screen.getAllByRole("alert")).toHaveLength(3);
  expect(screen.getByLabelText(/Nome completo/)).toHaveFocus();
  expect(onSave).not.toHaveBeenCalled();
});

it("envia dados normalizados e limpa o cadastro", async () => {
  const user = userEvent.setup();
  const onSave = vi.fn();
  render(<AlunoForm onSave={onSave} />);
  await user.type(screen.getByLabelText(/Nome completo/), " Ana ");
  await user.type(screen.getByLabelText(/E-mail/), "ANA@EXEMPLO.COM");
  await user.type(screen.getByLabelText(/Curso/), " Computação ");
  await user.click(screen.getByRole("button", { name: /Cadastrar aluno/ }));
  expect(onSave).toHaveBeenCalledWith({
    nome: "Ana",
    email: "ana@exemplo.com",
    curso: "Computação",
  });
  expect(screen.getByLabelText(/Nome completo/)).toHaveValue("");
});

it("preenche a edição e permite cancelamento", async () => {
  const onCancel = vi.fn();
  render(
    <AlunoForm
      aluno={{ nome: "Ana", email: "ana@exemplo.com", curso: "Computação" }}
      onCancel={onCancel}
    />,
  );
  expect(screen.getByLabelText(/Nome completo/)).toHaveValue("Ana");
  await userEvent.click(
    screen.getByRole("button", { name: "Cancelar edição" }),
  );
  expect(onCancel).toHaveBeenCalledOnce();
});
