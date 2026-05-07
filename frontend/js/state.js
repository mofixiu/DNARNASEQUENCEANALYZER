export const state = {
  token: localStorage.getItem("dna_token") || "",
  lastResult: null,
};

export function setToken(token) {
  state.token = token || "";
  if (state.token) {
    localStorage.setItem("dna_token", state.token);
  } else {
    localStorage.removeItem("dna_token");
  }
}
