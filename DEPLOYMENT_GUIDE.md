# Deployment Guide

## Fast local launch

- **Windows:** double-click `RUN_APP_WINDOWS.bat`.
- **macOS/Linux:** open Terminal in this folder and run `chmod +x RUN_APP_MAC_LINUX.sh && ./RUN_APP_MAC_LINUX.sh`.

The first launch creates a private virtual environment and installs the dependencies.

## GitHub setup

```bash
git init
git add .
git commit -m "Updated GenAI healthcare MDP app"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

## Streamlit Community Cloud

1. Push the complete project to GitHub.
2. Sign in to Streamlit Community Cloud.
3. Create an app from the repository.
4. Select `app.py` as the entry point.
5. Deploy.

No application secret is needed. The editable deck, rendered pages, workbooks and datasets are bundled locally, so confirm that the repository remains within the hosting platform's file-size limits.

## Administrator customisation

- Presenter profile: `modules/about.py`
- Workshop flow: `modules/facilitator.py`
- Theory-page metadata: `assets/slides/slides_meta.json`
- Tool directory: `data/tool_comparison_matrix.csv`
- Tool demo instructions: `data/tool_demo_playbook.json`
- Lab cases and prompts: `modules/content.py`
- Dataset catalogue: `data/dataset_registry.json`
- Downloadable resources: `assets/downloads/`

## Rebuilding the workshop assets

1. Update the workflow catalogue or app content.
2. Run `python scripts/build_masterclass_content.py`.
3. Run `node scripts/build_presentation.mjs`.
4. Run `python scripts/build_documents.py`.
5. Run `node scripts/build_tool_matrix.mjs`.
6. Render and visually verify the deck, PDFs, documents, and every spreadsheet sheet.
7. Run `python scripts/build_kits.py`.
8. Run `python -m unittest discover -s tests -v`.

The PowerPoint deck contains editable objects. The app displays exported slide previews for dependable browser presentation while preserving the editable PPTX as the source deliverable.

## Privacy architecture

The app does not call external GenAI APIs. Participants decide whether to open official third-party websites. During workshops, use only the supplied synthetic records. For real data, confirm institutional approval, contracts, access controls, data-retention terms, auditability and applicable clinical or regulatory review.
