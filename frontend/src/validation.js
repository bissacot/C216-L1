export const FIELD_LIMITS = { nome: 100, email: 150, curso: 100 };

export function normalizeAluno(values) {
  return {
    nome: values.nome.trim(),
    email: values.email.trim().toLowerCase(),
    curso: values.curso.trim(),
  };
}

export function validateAluno(values) {
  const aluno = normalizeAluno(values);
  const errors = {};
  for (const [field, label] of Object.entries({
    nome: "Nome",
    email: "E-mail",
    curso: "Curso",
  })) {
    if (!aluno[field]) errors[field] = `${label} é obrigatório.`;
    else if (aluno[field].length > FIELD_LIMITS[field])
      errors[field] =
        `${label} deve ter no máximo ${FIELD_LIMITS[field]} caracteres.`;
  }
  if (
    aluno.email &&
    !errors.email &&
    !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(aluno.email)
  ) {
    errors.email = "Informe um e-mail válido.";
  }
  return errors;
}
