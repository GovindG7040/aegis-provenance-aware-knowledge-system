# Aegis Assessment — Demo Script

## Goal

Demonstrate five capabilities:

1. Version-aware retrieval
2. Entity resolution
3. Provenance
4. Procedural retrieval
5. Abstention

## Setup

```powershell
cd E:\aegisv3\aegis-ai-assessment
.venv\Scripts\activate
```

## 1. Version-aware answer

```powershell
python -m app.cli ask "What is the current normal operating pressure for the HPU?"
```

Explain:

> The important part is that the system does not simply retrieve the latest number. It preserves the historical 180-bar value and applies 200 bar only to software revision 3.2 and later.

## 2. Entity resolution

```powershell
python -m app.cli ask "Is PS-04 the same component as PS-04A?"
```

Explain:

> The system resolves aliases, but deliberately does not merge PS-04 and PS-04A into one entity.

## 3. Provenance

```powershell
python -m app.cli ask "Which document introduced the change from PS-04 to PS-04A?"
```

Expected answer:

> ECN-1042.

Explain:

> The answer is tied to the Engineering Change Notice rather than inferred from generic similarity.

## 4. Procedure

```powershell
python -m app.cli ask "What happens if alarm A17 persists for more than 10 seconds?"
```

Expected answer:

> Execute Shutdown Procedure 4.7 before investigating further.

## 5. Abstention

```powershell
python -m app.cli ask "What is the maximum continuous operating temperature of PS-04A?"
```

Expected behavior:

> This cannot be determined from the supplied documentation.

Explain:

> This is intentional. The corpus does not establish the value, so the system abstains instead of allowing the LLM to guess.

## 6. Full evaluation

```powershell
python -m app.cli evaluate
```

Expected baseline:

```text
questions: 23
mean_keyword_coverage: 1.0
correct_abstention_rate_q19_q23: 1.0
```

Do not call this 100% semantic accuracy.

Say:

> The automated keyword-coverage baseline reached 1.0 across all 23 questions, with a 100% correct abstention rate for the five unsupported questions. I also manually reviewed evidence, provenance, and version applicability.

## If asked: Why not just use RAG?

> A standard RAG system could retrieve both the historical 180-bar value and current 200-bar value without understanding applicability. This implementation adds entity normalization, structured facts, version applicability, source trust, provenance, and abstention so retrieval results are interpreted in context.

## If asked about Gemini

> Gemini is not treated as the knowledge source. Retrieval identifies the relevant evidence first, and Gemini is used to formulate the final answer from that evidence.

## If asked about unsupported questions

> The system distinguishes between finding an answer and determining that the corpus does not establish an answer. That is important for technical documentation because hallucinating an operating limit can be worse than returning an explicit unknown.

## Closing statement

> The main design goal was evidence-grounded technical QA with provenance and controlled uncertainty, rather than simply making a chatbot answer as many questions as possible.
