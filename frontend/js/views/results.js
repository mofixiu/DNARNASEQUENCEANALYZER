import { lookupProtein } from "../api.js";

function card(title, body) {
  return `<article class="result-card"><h3>${title}</h3>${body}</article>`;
}

function codonTable(rows) {
  if (!rows.length) return "<p>No complete codons were found.</p>";
  const tableRows = rows
    .map(
      (row) =>
        `<tr><td>${row.codon}</td><td>${row.amino_acid_name}</td><td>${row.three_letter}</td><td>${row.one_letter}</td></tr>`
    )
    .join("");
  return `<table class="table"><thead><tr><th>Codon</th><th>Amino Acid</th><th>3-Letter</th><th>1-Letter</th></tr></thead><tbody>${tableRows}</tbody></table>`;
}

export async function renderResults(result, target) {
  const detection = card(
    "Detection",
    `<p><strong>Type:</strong> ${result.sequence_type.toUpperCase()}</p><p>${result.detection_explanation}</p>`
  );

  const transcription = card(
    "Transcription",
    `<p>${result.transcription_explanation}</p>
     <p><strong>Input:</strong></p><div class="code-line">${result.normalized_input}</div>
     <p><strong>mRNA:</strong></p><div class="code-line">${result.mrna_sequence}</div>`
  );

  const translation = card(
    "Translation",
    `<p>${result.translation_explanation}</p>${codonTable(result.codon_rows)}`
  );

  const chain = card(
    "Amino Acids (Polypeptide Chain)",
    `<p>${result.amino_acid_explanation}</p>${codonTable(result.polypeptide_chain)}`
  );

  const protein = card(
    "Protein Characterization",
    `<p>${result.protein_explanation}</p>
     <p><strong>Protein Sequence:</strong> ${result.protein_sequence || "No protein generated"}</p>
     <p><strong>Length:</strong> ${result.protein_characterization.length}</p>`
  );

  target.innerHTML = detection + transcription + translation + chain + protein + card("Protein Database Search", "<p>Searching UniProt and BLAST...</p>");

  const lookup = await lookupProtein(result.protein_sequence);
  const lookupBody = lookup
    .map((source) => {
      const hits = source.hits.length
        ? source.hits
            .map(
              (hit) =>
                `<li><strong>${hit.protein_name}</strong> (${hit.organism})<br /><em>${hit.function}</em></li>`
            )
            .join("")
        : "<li>No detailed hits available.</li>";
      return `<div class="result-card"><h4>${source.source}</h4><p>${source.message}</p><ul>${hits}</ul></div>`;
    })
    .join("");

  target.innerHTML = detection + transcription + translation + chain + protein + card("Protein Database Search", lookupBody);
}
