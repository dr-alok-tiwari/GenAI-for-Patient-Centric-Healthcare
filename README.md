# GenAI for Patient-Centric Healthcare — MDP Learning Studio

A local-first Streamlit application built around the supplied **Practical Tools for Doctors and Pharma Professionals** workshop PDF and a 150-minute MDP format:

- 60-minute theory experience using all 10 supplied PDF pages
- zoomable live presentation viewer with full-screen browser teaching mode
- downloadable presentation-ready PPTX rebuilt from the supplied PDF
- responsive page viewer with facilitation cues, icons and badges
- no browser-reconstructed slide text, avoiding text overlap
- curated directory of 29 healthcare, pharma, research, analytics and design tools
- guided tool-demo laboratory for every listed tool
- dedicated medical-imaging and multimodal-AI laboratory
- ten chest X-ray, CT, MRI, ultrasound, mammography and musculoskeletal workflows
- PNG, JPEG, TIFF and uncompressed DICOM upload and preview
- local non-diagnostic pixel checks, modality-specific prompts and AI-draft auditing
- one relevant synthetic dataset, demo record, prompt and verification checklist per tool
- six 15-minute hands-on labs aligned with page 9 of the supplied deck
- 18 synthetic CSV datasets covering clinical, patient, pharma, research and governance workflows
- prompt studio, data explorer, case conference, governance workbench and assessment
- downloadable updated workshop kit and tool-demo workbook

## Medical Imaging & Multimodal AI Lab

Open **Medical imaging lab** from the sidebar. The lab provides ten structured
radiology demonstrations:

1. Chest X-ray for acute breathlessness
2. Chest X-ray for tubes and line position
3. Non-contrast CT head
4. CT pulmonary angiography
5. MRI brain
6. MRI spine
7. Musculoskeletal trauma X-ray
8. Abdominal ultrasound
9. Obstetric ultrasound
10. Mammography

The app performs basic local technical image checks and creates a
modality-specific prompt for an approved multimodal tool. It does **not** run a
diagnostic classifier, sign a report, prescribe treatment or replace a qualified
radiologist. DICOM metadata displayed by the app is restricted to selected
technical tags; patient and study identifiers are deliberately excluded.

### Imaging workflow

1. Select a radiological case.
2. Confirm that the image and context are synthetic or properly de-identified.
3. Upload a PNG, JPEG, TIFF or uncompressed DICOM image.
4. Review the image preview, technical indicators and limitations.
5. Download the multimodal prompt and use it with an institution-approved account.
6. Paste the resulting draft into the structural safety audit.
7. Complete the professional checklist and export a de-identified session record.

The export intentionally excludes image pixels, filenames, DICOM identifiers and
AI-draft text.

## Safety

This application is for education only and is not a medical device. Use the bundled synthetic records during demonstrations. Do not paste identifiable patient, employee, investigator or adverse-event data into personal or public AI accounts. Real-world use requires an institution-approved environment, suitable contracts and access controls, auditability, regulatory review where relevant and qualified human verification.

## Run locally

### Windows

Double-click `RUN_APP_WINDOWS.bat`, or run:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux

```bash
chmod +x RUN_APP_MAC_LINUX.sh
./RUN_APP_MAC_LINUX.sh
```

Alternatively:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

The browser normally opens at `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository and upload the contents of this folder.
2. Sign in to Streamlit Community Cloud with GitHub.
3. Select **Create app**, choose the repository and branch, and set `app.py` as the entry point.
4. Deploy. No API key or secret is required for the application itself.

## Project structure

```text
app.py
modules/                 application pages, imaging core and shared components
data/                    synthetic datasets, radiology cases and tool playbooks
assets/slides/           10 rendered pages from the supplied PDF plus metadata
assets/downloads/        supplied PDF, live PPTX deck, dataset ZIP, demo workbook and updated kit
tests/                   unit tests for the local imaging workflow
.streamlit/config.toml   visual theme and server settings
requirements.txt
```

## Customisation

- Update presenter information in `modules/about.py`.
- Edit the workshop timing in `modules/facilitator.py`.
- Edit the six labs in `modules/content.py`.
- Edit radiology cases in `data/radiology_case_library.json`.
- Extend image handling and prompts in `modules/imaging_core.py`.
- Add or revise tools in `data/tool_comparison_matrix.csv` and `data/tool_demo_playbook.json`.
- Add a dataset to `data/` and register it in `data/dataset_registry.json`.
- Replace the source PDF page images in `assets/slides/` and update `slides_meta.json`.

## Developed by

Dr. Alok Tiwari, Assistant Professor – Big Data Analytics, Goa Institute of Management.

## Live theory deck

Open **Theory deck** inside the app for browser-based full-screen delivery with zoom controls. For native slide-show delivery, download `GenAI_Patient_Centric_Healthcare_Theory_Deck_Live_Presentation.pptx` from the Theory deck or Resources page and open it in PowerPoint, Keynote or Google Slides. The PPTX uses full-slide images from the supplied PDF, so browser text wrapping cannot create slide overlap.
