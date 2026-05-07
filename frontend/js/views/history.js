import { getHistory, getHistoryItem } from "../api.js";
import { renderResults } from "./results.js";

export async function refreshHistory(listEl, resultsEl, statusEl) {
  try {
    const items = await getHistory();
    listEl.innerHTML = "";

    if (!items.length) {
      listEl.innerHTML = "<li>No saved runs yet.</li>";
      return;
    }

    items.forEach((item) => {
      const li = document.createElement("li");
      const btn = document.createElement("button");
      btn.textContent = `${item.sequence_type.toUpperCase()} · ${new Date(item.created_at).toLocaleString()}`;
      btn.addEventListener("click", async () => {
        const full = await getHistoryItem(item.id);
        await renderResults(full, resultsEl);
        statusEl.textContent = "Loaded history item.";
      });
      li.appendChild(btn);
      listEl.appendChild(li);
    });
  } catch (error) {
    statusEl.textContent = error.message;
  }
}
