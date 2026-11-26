const apiUrl = (
  import.meta.env.VITE_API_URL || "http://localhost:8000"
).replace(/\/+$/, "");

function errorMessage(status, detail) {
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    const labels = { nome: "Nome completo", email: "E-mail", curso: "Curso" };
    const fields = detail
      .map((issue) => labels[issue.loc?.at(-1)])
      .filter(Boolean);
    if (fields.length)
      return `Revise os campos indicados: ${[...new Set(fields)].join(", ")}.`;
    return "A API recusou os dados enviados. Revise o formulário.";
  }
  return `A solicitação falhou (HTTP ${status}). Tente novamente.`;
}

export async function request(path, { method = "GET", data, signal } = {}) {
  let response;
  try {
    response = await fetch(`${apiUrl}${path}`, {
      method,
      signal,
      ...(data !== undefined && {
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }),
    });
  } catch (error) {
    if (signal?.aborted) throw error;
    throw new Error(
      "Não foi possível conectar à API. Verifique a conexão e tente novamente.",
    );
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(errorMessage(response.status, body?.detail));
  }
  if (response.status === 204) return;
  try {
    return await response.json();
  } catch {
    throw new Error(
      "Não foi possível ler a resposta da API. Atualize a página para consultar os dados.",
    );
  }
}
