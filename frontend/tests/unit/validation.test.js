import { describe, expect, it } from "vitest";
import {
  FIELD_LIMITS,
  normalizeAluno,
  validateAluno,
} from "../../src/validation.js";

const valid = {
  nome: "Ana Souza",
  email: "ana@exemplo.com",
  curso: "Engenharia",
};

describe("validação de alunos", () => {
  it("aceita dados válidos", () => {
    expect(validateAluno(valid)).toEqual({});
  });
  it("normaliza espaços externos e e-mail", () => {
    expect(
      normalizeAluno({
        nome: " Ana Souza ",
        email: " ANA@EXEMPLO.COM ",
        curso: " Engenharia ",
      }),
    ).toEqual(valid);
  });
  it("rejeita campos vazios e espaços em branco", () => {
    expect(
      Object.keys(validateAluno({ nome: " ", email: "", curso: "  " })),
    ).toEqual(["nome", "email", "curso"]);
  });
  it.each([
    "ana",
    "ana@",
    "@exemplo.com",
    "ana@exemplo",
    "ana @exemplo.com",
    "ana@@exemplo.com",
  ])("rejeita e-mail inválido: %s", (email) => {
    expect(validateAluno({ ...valid, email }).email).toBe(
      "Informe um e-mail válido.",
    );
  });
  it.each(Object.entries(FIELD_LIMITS))(
    "rejeita %s acima do limite",
    (field, limit) => {
      expect(
        validateAluno({ ...valid, [field]: "a".repeat(limit + 1) })[field],
      ).toContain(`no máximo ${limit}`);
    },
  );
  it("aceita os limites do modelo existente", () => {
    expect(
      validateAluno({
        nome: "a".repeat(100),
        email: `${"a".repeat(138)}@exemplo.com`,
        curso: "b".repeat(100),
      }),
    ).toEqual({});
  });
});
