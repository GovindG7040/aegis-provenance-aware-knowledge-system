# Aegis Knowledge Ingestion Challenge — Architecture & Evaluation Report

## 1. Objective
Build a provenance-preserving knowledge ingestion and Q&A system over 20 heterogeneous Aegis Series-7 HCS documents.

## 2. Dataset
20 files across 8 formats, multiple trust levels, mixed modalities, and deliberate contradictions/version changes.

## 3. Architecture
Describe the ingestion -> normalization -> entity resolution -> fact extraction -> knowledge store -> retrieval -> answer pipeline.

## 4. Intermediate Knowledge Representation
Document the Source, Chunk, Entity/Alias and Fact structures. Explain validity scope and provenance.

## 5. Extraction Strategy
- Deterministic: parsers, OCR, spreadsheets, JSON, metadata, domain rules.
- Optional model-based: grounded final response synthesis.

## 6. Entity Resolution
Explain PS-04 / PS-04A / PS-40 and HPU aliases, including why PS-04 and PS-04A are related but not the same active component.

## 7. Versioning and Conflicts
Explain 180 bar before software 3.2 versus 200 bar on 3.2+, and why both facts are retained.

## 8. Provenance and Trust
Explain source-level trust and evidence locators.

## 9. Retrieval and Answering
Explain hybrid retrieval and grounded answer generation.

## 10. Abstention / Gaps
Document the five supplied questions whose answers are not established by the package.

## 11. Evaluation
Insert `artifacts/evaluation_results.json` metrics and the final reviewed results table.

## 12. Limitations and Future Work
Discuss OCR errors, graphical topology extraction, broader alias learning, richer temporal reasoning, and stronger semantic evaluation.
