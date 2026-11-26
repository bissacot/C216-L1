import { request } from "./api.js";

const collection = "/alunos/";

export const listarAlunos = (signal) => request(collection, { signal });
export const buscarAluno = (id) => request(`${collection}${id}`);
export const criarAluno = (data) =>
  request(collection, { method: "POST", data });
export const substituirAluno = (id, data) =>
  request(`${collection}${id}`, { method: "PUT", data });
export const atualizarAluno = (id, data) =>
  request(`${collection}${id}`, { method: "PATCH", data });
export const excluirAluno = (id) =>
  request(`${collection}${id}`, { method: "DELETE" });
