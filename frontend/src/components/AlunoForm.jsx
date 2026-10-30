import { useEffect, useRef, useState } from "react";
import { normalizeAluno, validateAluno } from "../validation.js";

const emptyAluno = { nome: "", email: "", curso: "" };

export default function AlunoForm({ aluno, onSave, onCancel }) {
  const [values, setValues] = useState(aluno ?? emptyAluno);
  const [errors, setErrors] = useState({});
  const formRef = useRef(null);

  useEffect(() => {
    if (aluno) formRef.current.elements.namedItem("nome").focus();
  }, [aluno]);

  function handleSubmit(event) {
    event.preventDefault();
    const nextErrors = validateAluno(values);
    setErrors(nextErrors);
    const firstError = Object.keys(nextErrors)[0];
    if (firstError) {
      formRef.current.elements.namedItem(firstError).focus();
      return;
    }
    onSave(normalizeAluno(values));
    if (!aluno) setValues(emptyAluno);
  }

  return (
    <section
      className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm sm:p-8"
      aria-labelledby="form-title"
    >
      <p className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-emerald-800">
        {aluno ? "Atualizar cadastro" : "Um novo começo"}
      </p>
      <h2 id="form-title" className="text-2xl font-semibold tracking-tight">
        {aluno ? "Editar aluno" : "Novo aluno"}
      </h2>
      <p className="mt-2 text-sm leading-6 text-stone-500">
        Preencha os dados para{" "}
        {aluno ? "atualizar o cadastro" : "adicionar um aluno à sua lista"}.
      </p>
      <form
        ref={formRef}
        onSubmit={handleSubmit}
        noValidate
        className="mt-7 space-y-5"
      >
        {[
          ["nome", "Nome completo", "Ex.: Ana Souza", "text"],
          ["email", "E-mail", "ana@exemplo.com", "email"],
          ["curso", "Curso", "Ex.: Engenharia de Software", "text"],
        ].map(([field, label, placeholder, type]) => (
          <div key={field}>
            <label className="mb-2 block text-sm font-medium" htmlFor={field}>
              {label}{" "}
              <span className="text-emerald-700" aria-hidden="true">
                *
              </span>
            </label>
            <input
              id={field}
              name={field}
              type={type}
              required
              autoComplete={
                field === "nome" ? "name" : field === "email" ? "email" : "off"
              }
              value={values[field]}
              placeholder={placeholder}
              aria-invalid={Boolean(errors[field])}
              aria-describedby={errors[field] ? `${field}-error` : undefined}
              onChange={(event) =>
                setValues({ ...values, [field]: event.target.value })
              }
              className="w-full rounded-lg border border-stone-300 bg-stone-50/50 px-3.5 py-3 text-sm text-stone-800 transition focus:border-emerald-700 focus:outline-emerald-700 aria-invalid:border-red-600"
            />
            {errors[field] && (
              <p
                id={`${field}-error`}
                role="alert"
                className="mt-2 text-sm text-red-700"
              >
                {errors[field]}
              </p>
            )}
          </div>
        ))}
        <p className="text-xs text-stone-500">
          * Todos os campos são obrigatórios.
        </p>
        <button
          type="submit"
          className="w-full rounded-lg bg-[#213f35] px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-900"
        >
          {aluno ? "Salvar alterações" : "Cadastrar aluno"}{" "}
          <span aria-hidden="true">↗</span>
        </button>
        {aluno && (
          <button
            type="button"
            onClick={onCancel}
            className="w-full rounded-lg border border-stone-300 px-4 py-3 text-sm font-medium hover:bg-stone-100"
          >
            Cancelar edição
          </button>
        )}
      </form>
    </section>
  );
}
