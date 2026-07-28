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

No application secret is needed. The source PDF, rendered pages, live PPTX and datasets are bundled locally, so confirm that the repository remains within the hosting platform's file-size limits.

## Administrator customisation

- Presenter profile: `modules/about.py`
- Workshop flow: `modules/facilitator.py`
- Theory-page metadata: `assets/slides/slides_meta.json`
- Tool directory: `data/tool_comparison_matrix.csv`
- Tool demo instructions: `data/tool_demo_playbook.json`
- Lab cases and prompts: `modules/content.py`
- Dataset catalogue: `data/dataset_registry.json`
- Downloadable resources: `assets/downloads/`

## Replacing the workshop PDF later

1. Put the new source PDF under `assets/downloads/`.
2. Render each PDF page to PNG at a consistent DPI.
3. Replace the images in `assets/slides/`.
4. Update `assets/slides/slides_meta.json` with titles, summaries, facilitation notes and linked labs.
5. Rebuild `assets/downloads/GenAI_Patient_Centric_Healthcare_Theory_Deck_Live_Presentation.pptx` from the new PDF page images.
6. Update the source-PDF and PPTX filenames in `modules/theory.py` and `modules/resources.py` if the filenames change.

The app displays page images rather than reconstructing slide text in HTML. This preserves the original design and prevents text-box overlap at different browser widths. The PPTX uses full-slide images for the same reason, making it safe for live PowerPoint/Keynote/Google Slides presentation.

## Privacy architecture

The app does not call external GenAI APIs. Participants decide whether to open official third-party websites. During workshops, use only the supplied synthetic records. For real data, confirm institutional approval, contracts, access controls, data-retention terms, auditability and applicable clinical or regulatory review.
