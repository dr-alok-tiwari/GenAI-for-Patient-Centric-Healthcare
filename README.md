# Alkem AI Masterclass — GenAI for Patient-Centric Healthcare

A local-first Streamlit learning studio for a 150-minute healthcare and pharma masterclass:

- 60-minute, 12-slide theory sequence organised around four pillars
- 90-minute, six-lab medical and pharma practicum
- synthetic prescription extraction and explanation
- synthetic medical-image observation boundary—never diagnosis
- discharge, multilingual teach-back, clinical reasoning, PV, and evidence workflows
- 29-tool directory and demo playbook
- 24 complete healthcare workflow records
- cascading dropdowns with 100% visible-option coverage
- participant workbook, facilitator handbook, editable deck, PDFs, matrix, and dataset kit

## Four pillars

1. Patient Understanding and Engagement
2. Clinical Workflow and Decision Support
3. Pharma, Research and Professional Productivity
4. Responsible AI, Governance and Implementation

Every workflow connects a professional role and bounded task to a synthetic dataset, tool route, prompt, expected output, prohibited actions, verification checklist, and named human reviewer.

## Safety boundary

This application is for education only and is not a medical device. Use the bundled synthetic records and images. Do not paste identifiable patient, employee, investigator, prescription, medical-image, or adverse-event data into personal or public AI accounts.

Real-world use requires institution-approved tools and accounts, appropriate data and security controls, contracts, auditability, clinical and regulatory review where relevant, monitoring, incident handling, and qualified human verification. GenAI must not make autonomous diagnosis, prescribing, triage, pharmacovigilance, trial, publication, regulatory, legal, or governance decisions.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

The browser normally opens at `http://localhost:8501`. The app itself does not call an external AI model service and does not need a model key.

## Guaranteed dropdown coverage

`data/workflow_catalog.json` is the single source of truth for Prompt Studio selections. Each dropdown is populated from records still reachable after prior selections, so unsupported intersections are removed before they can be selected.

An unmatched free-text search returns a clearly labelled closest verified alternative. It does not fabricate a workflow or terminate with a blank response.

Run the integrity checks:

```bash
python -m unittest discover -s tests -v
```

See `DROPDOWN_COVERAGE_REPORT.md` and the downloadable `Dropdown_Coverage_Report.pdf` for the full coverage evidence.

## Project structure

```text
app.py
modules/                    Streamlit pages, brand, selection engine, labs
data/                       20 synthetic datasets and 24-workflow catalogue
assets/medical/             fully synthetic prescription and radiograph assets
assets/slides/              12 rendered slide previews and metadata
assets/downloads/           deck, guides, PDFs, workbook, datasets, reports
scripts/                    reproducible content and artifact build scripts
tests/                      dropdown coverage and integrity checks
```

## Rebuild workshop assets

The repository includes reproducible builders:

```bash
python scripts/build_masterclass_content.py
node scripts/build_presentation.mjs
python scripts/build_documents.py
node scripts/build_tool_matrix.mjs
python scripts/build_kits.py
```

Presentation and spreadsheet builders use `@oai/artifact-tool`; document builders use `python-docx`. PDF and visual verification steps are described in `IMPLEMENTATION_REPORT.md`.

## Main downloads

- `Alkem_AI_Masterclass_Healthcare.pptx` and matching PDF
- participant workbook in DOCX and PDF
- facilitator handbook in DOCX and PDF
- seven-sheet healthcare tool/workflow matrix
- complete synthetic dataset pack
- dropdown coverage report
- complete workshop kit

## Branding and attribution

The refreshed assets use the text lockup `ALKEM | AI MASTERCLASS`; no third-party or legacy API logo is used. Synthetic medical assets and external sources are documented in `ASSET_ATTRIBUTION.md` and `assets/medical/ATTRIBUTION.md`.

## Developed by

Dr. Alok Tiwari, Assistant Professor – Big Data Analytics, Goa Institute of Management.
