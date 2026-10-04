# Aegis AI Assessment — Final Report

## 1. Executive Summary

This project implements a provenance-aware knowledge ingestion and retrieval system for the Aegis Series-7 HCS documentation corpus.

Rather than treating the corpus as a simple flat RAG collection, the system separates ingestion, normalization, entity/alias resolution, structured facts, version applicability, provenance, retrieval, trust, answer generation, and abstention.

The system is designed to answer from supplied evidence, preserve historical/current values separately, identify the source of changes, and abstain when the corpus does not establish the requested fact.

## 2. Problem Understanding

The assessment corpus contains heterogeneous technical sources, including PDF, scanned/visual material, HTML, XLSX, DOCX, PNG, JSON, and PPTX.

The main challenges are:

- Different document formats and extraction methods.
- Multiple names/aliases for the same entity.
- Component identifiers that change across revisions.
- Historical and current values that must not be incorrectly merged.
- Different source trust levels.
- Questions for which the supplied corpus contains no answer.
- Need for source-level provenance.

A naive RAG pipeline could retrieve both historical and current facts without understanding applicability. This implementation therefore treats version and provenance as first-class retrieval information.

## 3. Architecture

```text
                 Heterogeneous Source Documents
          PDF / HTML / XLSX / DOCX / PNG / JSON / PPTX
                              |
                              v
                    Ingestion / Loaders
                              |
                              v
                  Normalization + Chunking
                              |
                              v
                    Metadata / Provenance
                              |
                              v
                  Knowledge Extraction
                     /              \
                    v                v
              Entity/Alias         Structured
               Resolution           Facts
                    \                /
                     \              /
                      v            v
                   Knowledge / Fact Store
                              |
                              v
                     Provenance-Aware
                         Retrieval
                              |
                  +-----------+-----------+
                  |                       |
                  v                       v
             Evidence Ranking       Trust / Version
                  |                   Applicability
                  +-----------+-----------+
                              |
                              v
                       Gemini Answer Layer
                              |
                              v
                 Answer + Claims + Evidence
                              |
                              v
                 Abstain when evidence
                    is insufficient
```

## 4. Ingestion and Normalization

The ingestion layer uses format-specific loaders and converts source material into a common internal representation.

Extracted chunks retain provenance metadata such as:

- source identifier
- document type/name
- page, sheet, row, or HTML locator where available
- extracted text
- source/trust classification

This allows answers to be tied back to source evidence.

The working knowledge base successfully ingests the 20-source assessment corpus and generates structured chunks/facts for retrieval.

## 5. Entity Resolution and Aliases

Known aliases are normalized before fact matching.

Examples:

| Alias / form | Canonical entity |
|---|---|
| HPU | HPU |
| Hydraulic Power Unit | HPU |
| Hydraulic Unit | HPU |
| HP unit | HPU |
| Hydraulic Power Pack | HPU |
| PS04 / P04 / PS-04 | PS-04 |
| PS04A / P04A / P.S.04-A | PS-04A |

A critical distinction is maintained between:

- **PS-04** — legacy pressure sensor
- **PS-04A** — successor/superseding pressure sensor
- **PS-40** — separate component

This prevents superficially similar identifiers from being merged.

## 6. Version and Conflict Handling

Historical and current facts are represented as separate applicable facts instead of overwriting the old value.

For example:

- Before software revision 3.2: normal HPU discharge pressure = **180 bar**.
- Software revision 3.2 and later: normal HPU discharge pressure = **200 bar**.

Likewise:

- PS-04 is associated with revisions before 3.2.
- PS-04A is associated with revision 3.2 and later.
- ECN-1042 records the change.

This prevents an old value from being incorrectly treated as the current universal value.

## 7. Provenance and Trust

Evidence is retained with source identity and a locator.

The implementation distinguishes source trust levels, with official manuals, engineering change notices, and component references receiving higher trust than lower-authority supporting material.

A response can therefore establish both the answer and its applicability, for example:

> The current normal HPU discharge pressure is 200 bar for software revision 3.2 and later.

with supporting evidence from the relevant official source.

## 8. Retrieval and Answer Generation

The retrieval/answer flow is:

1. Interpret the question.
2. Resolve entity aliases.
3. Retrieve relevant structured facts and evidence.
4. Apply version/applicability information.
5. Rank evidence by relevance and trust.
6. Generate an answer constrained by retrieved evidence.
7. Return claims and supporting evidence.
8. Abstain when the corpus does not establish the requested fact.

Gemini is used as a controlled answer-generation layer rather than as the source of truth.

## 9. Abstention

Abstention is an explicit system behavior.

When the supplied corpus does not establish the requested information, the system returns an uncertainty/insufficient-evidence response instead of fabricating a value.

This was verified for Q19–Q23.

Examples include:

- maximum continuous operating temperature of PS-04A
- approver of ECN-1058
- IV-21 MTBF
- 3-phase 400V compatibility

## 10. Evaluation

The full automated evaluation was run across all 23 supplied questions.

```text
Questions:                    23
Mean keyword coverage:       1.0
Correct abstention Q19-Q23:  1.0
```

The keyword-coverage value is a transparent baseline metric, **not a claim of 100% semantic accuracy**. Evidence coverage, exactness, provenance, version applicability, and abstention behavior were also manually reviewed.

### Manual validation

**Current pressure**

> What is the current normal operating pressure for the HPU?

The system returned 200 bar for software revision 3.2 and later and preserved 180 bar for earlier revisions.

**Entity resolution**

> Is PS-04 the same component as PS-04A?

The system correctly identified PS-04A as the successor/superseding sensor rather than treating it as the same entity.

**Change provenance**

> Which document introduced the change from PS-04 to PS-04A?

The system correctly identified **ECN-1042**.

**Procedure**

> What happens if alarm A17 persists for more than 10 seconds?

The system correctly returned **Shutdown Procedure 4.7**.

**Unsupported information**

> What is the maximum continuous operating temperature of PS-04A?

The system correctly abstained because the supplied documentation does not establish the value.

## 11. Key Design Decisions

### Do not overwrite historical facts

180 bar was not replaced by 200 bar. Both remain represented with their applicable software revisions.

### Do not merge similar component identifiers

PS-04, PS-04A, and PS-40 remain distinct.

### Treat provenance as part of the answer

Evidence is returned with source identifiers and locators.

### Treat missing evidence as a valid outcome

The system can explicitly state that a fact is not established by the supplied corpus.

### Use the LLM after retrieval

Gemini formulates the response from retrieved evidence rather than acting as the underlying knowledge base.

## 12. Limitations

- The automated metric is keyword coverage and should not be interpreted as complete semantic evaluation.
- OCR/extraction quality depends on source quality.
- The structured knowledge model is tailored to the entities and fact types represented in this assessment corpus.
- Unsupported facts cannot be recovered when no supplied source establishes them.
- The current Gemini SDK usage emits an advisory AFC warning, but the calls complete successfully. This is non-blocking for the demonstrated workflow.

## 13. Reproducibility

From the project root:

```powershell
python -m app.cli evaluate
```

Example:

```powershell
python -m app.cli ask "What is the current normal operating pressure for the HPU?"
```

The project is intended to run inside the supplied Python virtual environment with dependencies installed from `requirements.txt`.

## 14. Conclusion

The implementation demonstrates evidence-grounded technical QA with provenance and controlled uncertainty rather than a basic chatbot.

Its main strengths are handling aliases, historical/current values, component supersession, provenance, source trust, version applicability, and missing evidence.

The system can answer when the corpus supports the claim, preserve historical context when values change, identify the source of a change, and abstain when evidence is insufficient.
