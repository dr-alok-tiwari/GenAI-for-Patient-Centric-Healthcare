# GenAI Healthcare MDP Prompt Bank

## 1. Patient empathy rewrite
**Type:** Beginner

```text
Rewrite the following instruction in simple, empathetic language for a patient with low health literacy. Keep medical meaning unchanged. Add 3 red flags and 3 follow-up reminders. Text: [paste synthetic text].
```

## 2. Discharge simplification
**Type:** Structured

```text
Act as a clinician-supervised patient education assistant. Input: synthetic discharge summary. Output: 1) diagnosis in simple words, 2) medicine schedule table, 3) warning signs, 4) diet/activity advice, 5) follow-up date, 6) questions to ask the doctor. Use no more than Grade 6 language.
```

## 3. Multilingual counselling
**Type:** Role-based

```text
You are helping a doctor prepare bilingual counselling. Translate the key advice into [language] using respectful, culturally appropriate phrasing. Keep drug names in English. Include a note: “Please confirm this with your doctor.”
```

## 4. Differential diagnosis safety
**Type:** Safety-aware clinical

```text
For this synthetic case, create a differential diagnosis checklist for clinician review. Separate likely, must-not-miss, and red-flag diagnoses. Do not provide final diagnosis. Ask what additional history, exam, and tests are needed. Case: [paste synthetic OPD row].
```

## 5. SOAP note draft
**Type:** Clinical productivity

```text
Convert the following synthetic encounter into a SOAP note. Mark assumptions clearly. Add missing information checklist. Do not invent lab values. Encounter: [paste synthetic case].
```

## 6. PV triage
**Type:** Pharma-compliant

```text
Classify this synthetic adverse-event report: seriousness, expectedness unknown, missing fields, follow-up questions, and neutral case narrative. Do not assess causality beyond “requires medical review.” Report: [paste AE row].
```

## 7. Medical information response
**Type:** Pharma-compliant

```text
Draft a balanced, non-promotional response to this medical query. Include: scope, label status, evidence needed, limitations, when to escalate to medical affairs/PV. Do not make off-label recommendations. Query: [paste row].
```

## 8. Literature review PICO
**Type:** Research synthesis

```text
Convert this research idea into PICO/PECO, 3 PubMed search strings, inclusion/exclusion criteria, evidence table columns, and 5 likely limitations. Topic: GenAI for patient education in chronic disease.
```

## 9. Research gap extraction
**Type:** Research synthesis

```text
From these abstracts, create a synthesis matrix with design, population, intervention, outcome, limitation, and gap. Then propose 3 feasible study questions. Use citations only when source metadata is provided.
```

## 10. Feedback analytics
**Type:** Data-analysis

```text
Analyze this synthetic patient feedback CSV. Provide top 5 themes, departments needing attention, 3 charts to create, and a service recovery action plan. Flag uncertainty and data quality issues.
```

