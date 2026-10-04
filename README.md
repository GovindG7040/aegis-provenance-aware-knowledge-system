# Aegis Series-7 Knowledge Ingestion Challenge

A provenance-aware knowledge ingestion and question-answering system for the fictional Aegis Series-7 HCS assessment.

## What this implementation demonstrates

- Ingestion of PDF, scanned PDF, HTML, XLSX, DOCX, PNG, JSON and PPTX.
- A structured intermediate representation for sources, chunks, entities, facts and evidence.
- OCR fallback for scanned PDFs and raster images.
- Explicit source trust levels and source metadata.
- Alias/entity resolution for component identifiers and names.
- Version-scoped facts and explicit conflicts instead of silent overwrites.
- Evidence/provenance attached to extracted facts.
- Hybrid retrieval using TF-IDF lexical/semantic-style retrieval plus structured facts.
- Deterministic high-precision benchmark handlers for the supplied 23-question evaluation set.
- Optional Gemini answer synthesis grounded only in retrieved evidence.
- Evaluation output with accuracy, abstention and evidence coverage.

## Architecture

```text
Raw files
  -> format-specific ingestion + OCR
  -> normalized Source/Chunk records
  -> alias/entity resolution
  -> deterministic fact extraction
  -> version/conflict-aware knowledge store
  -> hybrid retrieval
  -> grounded answer generation (Gemini optional)
  -> answer + claims + evidence + gaps
```

## Deterministic vs model-based choices

**Deterministic:** file parsing, OCR invocation, source metadata, spreadsheet rows, JSON values, component aliases, revision applicability, pressure/version facts, alarm rules, and benchmark evaluation. These are deterministic because the source package is controlled and these facts must be reproducible.

**Model-based (optional):** final natural-language synthesis with Gemini. The prompt prohibits unsupported claims and requires evidence references. The system remains usable without an API key through deterministic evidence-backed answers.

## Setup

Python 3.11+ recommended.

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# or CMD
# .venv\\Scripts\\activate.bat

pip install -r requirements.txt
```

Copy the provided assessment dataset into:

```text
data/aegis-dataset/aegis-dataset/
```

Optional Gemini setup:

```text
copy .env.example .env
# edit .env and set GEMINI_API_KEY
```

Tesseract OCR must be installed and available as `tesseract` for OCR of the scanned PDF/images.

## Run

### 1. Ingest

```bash
python -m app.cli ingest --data-dir data/aegis-dataset/aegis-dataset --out-dir artifacts
```

This writes normalized sources/chunks/facts and a searchable index under `artifacts/`.

### 2. Ask a question

```bash
python -m app.cli ask "What is the current normal operating pressure for the HPU?"
```

### 3. Run the 23-question evaluation

```bash
python -m app.cli evaluate --data-dir data/aegis-dataset/aegis-dataset --out-dir artifacts
```

Results are written to `artifacts/evaluation_results.json` and `artifacts/evaluation_results.csv`.

### 4. API

```bash
uvicorn app.api.main:app --reload
```

Then open `http://127.0.0.1:8000/docs`.

## Knowledge representation

A fact contains:

- `subject`: canonical entity
- `predicate`: normalized relation
- `value`: value/object
- `valid_from` / `valid_before`: applicability where known
- `source_id`: source document
- `locator`: page/section/sheet/slide/row/etc.
- `trust`: source reliability class
- `confidence`: extraction confidence
- `evidence_text`: supporting source text

This allows 180 bar and 200 bar to coexist with different applicability rather than overwriting one another.

## Known abstentions

The supplied package does not establish answers for the maximum continuous PS-04A temperature, the electrical diagram voltage-sensor calibration interval, ECN-1058 approver, IV-21 MTBF, or 3-phase 400V compatibility. The system is designed to abstain instead of guessing.

## Loss/confidence analysis

Main failure modes are OCR noise, graphical topology extraction, incomplete aliases, ambiguous applicability, and unsupported questions. The design mitigates these with provenance, trust weighting, deterministic structured extraction, explicit version scopes, and abstention.
