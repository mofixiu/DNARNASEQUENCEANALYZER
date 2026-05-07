# CSC 442 Project 2: DNA & RNA Sequence Analyzer

A web-based analyzer that accepts DNA/RNA sequence input, detects sequence type, performs transcription and translation, builds the amino-acid chain, characterizes the resulting protein, and queries external protein databases.

## Implemented Features (Starter Version)

- Three sequence input modes:
  - Type/paste in textarea
  - File upload (`.txt`, `.fasta`, `.fa`)
  - Drag and drop file
- Automatic sequence detection:
  - DNA (`A/C/G/T`)
  - RNA (`A/C/G/U`)
  - Invalid sequence detection (including mixed `T` + `U`)
- DNA strand handling:
  - Non-template (coding)
  - Template (antisense)
- Transcription output with explanation
- Translation output (codon-by-codon) with explanation
- Amino-acid/polypeptide display (full name + abbreviations)
- Protein characterization summary
- External lookup integration:
  - UniProt live query
  - BLAST placeholder endpoint (ready for full polling implementation)
- Authentication + per-user analysis history
- Modern black-and-white custom UI (non-template visual style)

## Project Structure

- `backend/main.py`: FastAPI app entrypoint and static frontend serving
- `backend/app/routers/auth.py`: register/login endpoints
- `backend/app/routers/analysis.py`: analysis, history, and protein lookup endpoints
- `backend/app/services/sequence_pipeline.py`: detection, transcription, translation, explanations
- `backend/app/services/protein_lookup.py`: UniProt + BLAST integration layer
- `frontend/index.html`: app shell
- `frontend/css/*`: design system and responsive layout
- `frontend/js/*`: frontend state, API, and rendering logic

## Run Locally

1. Open terminal in project root.
2. Create and activate a virtual environment.
3. Install dependencies:
   - `pip install -r backend/requirements.txt`
4. (Optional but recommended) copy env:
   - `cp .env.example .env`
5. Start server:
   - `uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000`
6. Open:
   - `http://127.0.0.1:8000`

## API Notes

- Auth token is expected in `Authorization: Bearer <token>`.
- Main analysis endpoints:
  - `POST /analysis/run` (JSON text input)
  - `POST /analysis/run-file` (multipart file input)
  - `GET /analysis/history`
  - `GET /analysis/history/{run_id}`
  - `POST /analysis/protein-lookup?protein_sequence=...`

## Next Improvements

- Complete BLAST async submit/poll workflow
- Add automated tests for pipeline correctness
- Add optional ORF/start-codon mode switch
- Add database migration tooling (Alembic)
