import { afterEach, expect, it, vi } from "vitest";
import {
  atualizarAluno,
  buscarAluno,
  criarAluno,
  excluirAluno,
  listarAlunos,
  substituirAluno,
} from "../../src/services/alunos.js";

afterEach(() => vi.unstubAllGlobals());

const aluno = { nome: "Ana", email: "ana@exemplo.com", curso: "Computação" };
const item = { ...aluno, id: 91 };

it.each([
  ["GET", "/alunos/", () => listarAlunos(), undefined, [item]],
  ["GET", "/alunos/91", () => buscarAluno(91), undefined, item],
  ["POST", "/alunos/", () => criarAluno(aluno), aluno, item],
  ["PUT", "/alunos/91", () => substituirAluno(91, aluno), aluno, item],
  [
    "PATCH",
    "/alunos/91",
    () => atualizarAluno(91, { curso: aluno.curso }),
    { curso: aluno.curso },
    item,
  ],
  ["DELETE", "/alunos/91", () => excluirAluno(91), undefined, undefined],
])(
  "%s %s espelha o contrato HTTP",
  async (method, path, call, body, result) => {
    const response = result
      ? Response.json(result)
      : new Response(null, { status: 204 });
    const http = vi.fn().mockResolvedValue(response);
    vi.stubGlobal("fetch", http);
    expect(await call()).toEqual(result);
    const [url, options] = http.mock.calls[0];
    expect(new URL(url).pathname).toBe(path);
    expect(options.method).toBe(method);
    expect(options.body).toBe(JSON.stringify(body));
    if (body) expect(options.headers["Content-Type"]).toBe("application/json");
  },
);
