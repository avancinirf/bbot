const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function handleResponse(res) {
  // DELETE /bots/{id} retorna 204 (sem corpo)
  if (res.status === 204) {
    return null;
  }

  const contentType = res.headers.get("content-type") || "";
  let data = null;

  try {
    if (contentType.includes("application/json")) {
      data = await res.json();
    } else {
      const text = await res.text();
      data = text === "" ? null : text;
    }
  } catch (e) {
    // Se der erro ao parsear, segue com data = null
    data = null;
  }

  if (!res.ok) {
    const msg =
      (data && data.detail) ||
      (typeof data === "string" ? data : "Erro na requisição");
    const error = new Error(msg);
    error.status = res.status;
    error.data = data;
    throw error;
  }

  return data;
}

export async function apiGet(path) {
  const res = await fetch(`${API_BASE_URL}${path}`);
  return handleResponse(res);
}

export async function apiPost(path, body) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : null,
  });
  return handleResponse(res);
}

export async function apiDelete(path) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "DELETE",
  });
  return handleResponse(res);
}
