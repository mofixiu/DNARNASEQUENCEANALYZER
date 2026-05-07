import { analyzeFile, analyzeText, login, register } from "./api.js";
import { setToken, state } from "./state.js";
import { refreshHistory } from "./views/history.js";
import { renderResults } from "./views/results.js";

const usernameEl = document.getElementById("username");
const emailEl = document.getElementById("email");
const passwordEl = document.getElementById("password");
const authStatusEl = document.getElementById("authStatus");

const registerBtn = document.getElementById("registerBtn");
const loginBtn = document.getElementById("loginBtn");
const logoutBtn = document.getElementById("logoutBtn");

const sequenceInputEl = document.getElementById("sequenceInput");
const fileInputEl = document.getElementById("fileInput");
const analyzeTextBtn = document.getElementById("analyzeTextBtn");
const dropZoneEl = document.getElementById("dropZone");
const strandWrapEl = document.getElementById("strandWrap");
const strandTypeEl = document.getElementById("strandType");
const inputStatusEl = document.getElementById("inputStatus");

const resultsEl = document.getElementById("results");
const historyListEl = document.getElementById("historyList");
const refreshHistoryBtn = document.getElementById("refreshHistoryBtn");

function authRequired() {
  if (!state.token) {
    throw new Error("Please log in first.");
  }
}

async function doAnalyzeWithText() {
  authRequired();
  inputStatusEl.textContent = "Analyzing...";
  try {
    const sequence = sequenceInputEl.value;
    const firstPass = await analyzeText({ sequence, strand_type: strandTypeEl.value });

    if (firstPass.sequence_type === "dna") {
      strandWrapEl.classList.remove("hidden");
    } else {
      strandWrapEl.classList.add("hidden");
    }

    await renderResults(firstPass, resultsEl);
    inputStatusEl.textContent = "Analysis complete.";
    await refreshHistory(historyListEl, resultsEl, inputStatusEl);
  } catch (error) {
    inputStatusEl.textContent = error.message;
  }
}

async function doAnalyzeWithFile(file) {
  authRequired();
  inputStatusEl.textContent = "Uploading and analyzing file...";
  try {
    const result = await analyzeFile(file, strandTypeEl.value);
    if (result.sequence_type === "dna") {
      strandWrapEl.classList.remove("hidden");
    } else {
      strandWrapEl.classList.add("hidden");
    }
    await renderResults(result, resultsEl);
    inputStatusEl.textContent = "File analysis complete.";
    await refreshHistory(historyListEl, resultsEl, inputStatusEl);
  } catch (error) {
    inputStatusEl.textContent = error.message;
  }
}

registerBtn.addEventListener("click", async () => {
  try {
    const payload = {
      username: usernameEl.value.trim(),
      email: emailEl.value.trim(),
      password: passwordEl.value,
    };
    await register(payload);
    authStatusEl.textContent = "Registration successful. You can now log in.";
  } catch (error) {
    authStatusEl.textContent = error.message;
  }
});

loginBtn.addEventListener("click", async () => {
  try {
    const payload = {
      username: usernameEl.value.trim(),
      password: passwordEl.value,
    };
    const response = await login(payload);
    setToken(response.access_token);
    authStatusEl.textContent = "Logged in.";
    await refreshHistory(historyListEl, resultsEl, inputStatusEl);
  } catch (error) {
    authStatusEl.textContent = error.message;
  }
});

logoutBtn.addEventListener("click", () => {
  setToken("");
  authStatusEl.textContent = "Logged out.";
  historyListEl.innerHTML = "";
});

analyzeTextBtn.addEventListener("click", doAnalyzeWithText);

fileInputEl.addEventListener("change", async (event) => {
  const file = event.target.files?.[0];
  if (file) {
    await doAnalyzeWithFile(file);
  }
});

["dragenter", "dragover"].forEach((name) => {
  dropZoneEl.addEventListener(name, (event) => {
    event.preventDefault();
    dropZoneEl.classList.add("active");
  });
});

["dragleave", "drop"].forEach((name) => {
  dropZoneEl.addEventListener(name, (event) => {
    event.preventDefault();
    dropZoneEl.classList.remove("active");
  });
});

dropZoneEl.addEventListener("drop", async (event) => {
  const file = event.dataTransfer?.files?.[0];
  if (file) {
    await doAnalyzeWithFile(file);
  }
});

refreshHistoryBtn.addEventListener("click", async () => {
  authRequired();
  await refreshHistory(historyListEl, resultsEl, inputStatusEl);
});

if (state.token) {
  authStatusEl.textContent = "Session restored.";
  refreshHistory(historyListEl, resultsEl, inputStatusEl).catch(() => {});
}
