import { state } from "./state.js";

const BASE = "";

async function request(path, options = {}) {
  const headers = {
    ...(options.headers || {}),
  };

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }

  const response = await fetch(`${BASE}${path}`, {
    ...options,
    headers,
  });

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const detail = payload?.detail || "Request failed";
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  return payload;
}

export function register(data) {
  return request("/auth/register", { method: "POST", body: JSON.stringify(data) });
}

export function login(data) {
  return request("/auth/login", { method: "POST", body: JSON.stringify(data) });
}

export function analyzeText(data) {
  return request("/analysis/run", { method: "POST", body: JSON.stringify(data) });
}

export function analyzeFile(file, strandType) {
  const formData = new FormData();
  formData.append("file", file);
  if (strandType) {
    formData.append("strand_type", strandType);
  }
  return request("/analysis/run-file", { method: "POST", body: formData });
}

export function getHistory() {
  return request("/analysis/history", { method: "GET" });
}

export function getHistoryItem(id) {
  return request(`/analysis/history/${id}`, { method: "GET" });
}

export function lookupProtein(proteinSequence) {
  return request(`/analysis/protein-lookup?protein_sequence=${encodeURIComponent(proteinSequence)}`, {
    method: "POST",
  });
}
