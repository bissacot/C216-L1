export default function AlunoList({ alunos, hasAlunos, onEdit, onDelete }) {
  if (!alunos.length)
    return (
      <div className="flex min-h-72 flex-col items-center justify-center px-6 text-center">
        <span
          aria-hidden="true"
          className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-[#eef2e6] text-2xl"
        >
          ♧
        </span>
        <h3 className="font-semibold">
          {hasAlunos
            ? "Nenhum resultado encontrado"
            : "Sua próxima turma começa aqui"}
        </h3>
        <p className="mt-2 max-w-xs text-sm leading-6 text-stone-500">
          {hasAlunos
            ? "Tente buscar por outro nome, e-mail ou curso."
            : "Cadastre o primeiro aluno no formulário. Ele aparecerá nesta lista."}
        </p>
      </div>
    );
  return (
    <ul className="divide-y divide-stone-100" aria-label="Alunos cadastrados">
      {alunos.map((aluno) => (
        <li
          key={aluno.id}
          className="flex flex-wrap items-center gap-4 px-5 py-5 sm:px-7"
        >
          <span
            aria-hidden="true"
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[#eef2e6] text-sm font-semibold text-emerald-900"
          >
            {aluno.nome
              .split(/\s+/)
              .slice(0, 2)
              .map((part) => part[0])
              .join("")
              .toUpperCase()}
          </span>
          <div className="min-w-0 flex-1 break-words">
            <h3 className="font-semibold text-stone-800">{aluno.nome}</h3>
            <p className="mt-1 text-sm text-stone-500">{aluno.email}</p>
            <p className="mt-2 text-xs font-medium text-emerald-800">
              {aluno.curso}
            </p>
          </div>
          <div className="flex w-full justify-end gap-2 sm:w-auto">
            <button
              type="button"
              onClick={() => onEdit(aluno)}
              aria-label={`Editar ${aluno.nome}`}
              className="rounded-lg border border-stone-200 px-3 py-2 text-xs font-medium hover:bg-stone-100"
            >
              Editar
            </button>
            <button
              type="button"
              onClick={() => onDelete(aluno)}
              aria-label={`Excluir ${aluno.nome}`}
              className="rounded-lg px-3 py-2 text-xs font-medium text-red-700 hover:bg-red-50"
            >
              Excluir
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}
