from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from .common import ROOT, badges, load_json, section_header, set_visited
from .imaging_core import (
    build_multimodal_prompt,
    compute_technical_metrics,
    export_session_payload,
    load_medical_image,
    review_ai_draft,
    serialise_medical_image,
    technical_observations,
)


def _case_label(case: dict) -> str:
    return f"{case['icon']} {case['title']} — {case['modality']}"


def render() -> None:
    set_visited("Medical imaging lab")
    section_header(
        "Radiology demonstration",
        "Medical Imaging & Multimodal AI Lab",
        "Choose a bundled public teaching sample or upload a synthetic/properly de-identified image, run local technical checks, build a modality-specific multimodal prompt and audit the AI-assisted draft before professional review.",
        "🩻",
    )
    st.markdown(
        """
        <div class="safety-banner"><b>Not a diagnostic system.</b> This lab does not diagnose, clear, stage or prescribe. It analyses basic technical pixel characteristics and structures an educational workflow. A radiologist or other authorised imaging professional must review the complete study, metadata, priors and clinical context.</div>
        """,
        unsafe_allow_html=True,
    )

    cases = load_json("radiology_case_library.json")
    sample_manifest = load_json("radiology_sample_manifest.json")
    modalities = ["All"] + list(dict.fromkeys(case["modality"] for case in cases))
    f1, f2 = st.columns([0.8, 1.2])
    with f1:
        modality = st.selectbox("Modality", modalities)
    available = cases if modality == "All" else [case for case in cases if case["modality"] == modality]
    with f2:
        selected_label = st.selectbox("Radiological case", [_case_label(case) for case in available])
    case = next(item for item in available if _case_label(item) == selected_label)

    st.markdown(
        f"""
        <div class="case-card">
          <div class="icon-title"><span class="icon-orb">{case['icon']}</span><div>
          <div class="section-label">{case['modality']} • {case['body_region']}</div>
          <h3 style="margin:.05rem 0">{case['title']}</h3>
          <p>{case['scenario']}</p></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    badges(
        [
            f"👤 Final owner: {case['human_owner']}",
            f"🧭 {len(case['systematic_review'])} review checkpoints",
            "🔒 Image is not sent to an AI API by this app",
        ],
        "medium",
    )

    c1, c2 = st.columns(2, gap="large")
    with c1:
        clinical_context = st.text_area(
            "De-identified clinical context",
            value=case["scenario"],
            height=135,
            help="Do not enter names, identifiers, exact addresses, contact details or other unnecessary personal data.",
        )
    with c2:
        clinical_question = st.text_area(
            "Clinical/educational question",
            value=case["clinical_question"],
            height=135,
        )

    st.subheader("Choose an image")
    image_source = st.radio(
        "Image source",
        ["Use a bundled sample", "Upload my own"],
        horizontal=True,
        help="Every radiological case includes five public teaching samples. Manual PNG, JPEG, TIFF and DICOM upload remains available.",
    )
    case_samples = [
        sample
        for sample in sample_manifest["samples"]
        if sample["case_id"] == case["case_id"]
    ]
    selected_sample = None
    uploaded = None
    if image_source == "Use a bundled sample":
        sample_options = {
            f"{sample['sample_id']} · {sample['title']}": sample for sample in case_samples
        }
        if not sample_options:
            st.error("No bundled sample is configured for this radiological case.")
        else:
            sample_label = st.selectbox("Bundled teaching image", list(sample_options))
            selected_sample = sample_options[sample_label]
            author = selected_sample["author"] or "Author not supplied on source page"
            license_label = selected_sample["license"]
            source_url = selected_sample["source_page"]
            license_url = selected_sample["license_url"] or source_url
            st.caption(
                "Public teaching image; not diagnostic ground truth or a validated model-evaluation dataset. "
                f"Credit: {author}."
            )
            st.markdown(
                f"[View original source ↗]({source_url}) · "
                f"[{license_label} license ↗]({license_url})"
            )
    else:
        privacy_confirmed = st.checkbox(
            "I confirm that the file and context are synthetic or properly de-identified and approved for this workshop environment.",
            value=False,
        )
        uploaded = st.file_uploader(
            "Upload PNG, JPEG, TIFF or uncompressed DICOM",
            type=["png", "jpg", "jpeg", "tif", "tiff", "dcm", "dicom"],
            disabled=not privacy_confirmed,
            help="DICOM objects can contain hidden identifiers. Use synthetic or institutionally de-identified files only.",
        )
        st.caption(
            "The app does not call an external AI service. On a hosted Streamlit deployment, the hosting server still processes the upload; follow your institution’s data policy."
        )

    loaded = None
    metrics = None
    observations: list[str] = []
    image_caption = ""
    if selected_sample is not None:
        sample_path = ROOT / selected_sample["local_path"]
        try:
            loaded = load_medical_image(sample_path.read_bytes(), sample_path.name)
            image_caption = f"Bundled teaching sample • {selected_sample['title']}"
            metrics = compute_technical_metrics(loaded.image)
            observations = technical_observations(metrics)
        except (OSError, ValueError) as exc:
            st.error(f"The bundled sample could not be loaded: {exc}")
    elif uploaded is not None:
        try:
            loaded = load_medical_image(uploaded.getvalue(), uploaded.name)
            image_caption = f"De-identified workshop upload • {loaded.source_format}"
            metrics = compute_technical_metrics(loaded.image)
            observations = technical_observations(metrics)
        except ValueError as exc:
            st.error(str(exc))

    image_tab, prompt_tab, checklist_tab, audit_tab, export_tab = st.tabs(
        [
            "🖼️ Image & technical analysis",
            "✨ Multimodal prompt",
            "🧭 Systematic review",
            "✅ Audit AI draft",
            "⬇️ Export",
        ]
    )

    with image_tab:
        if loaded is None:
            st.info(
                "Select a bundled sample or choose manual upload and provide an approved image. "
                "The remaining tabs can still be used to prepare the workflow without an image."
            )
        else:
            left, right = st.columns([1.15, 0.85], gap="large")
            with left:
                st.image(
                    loaded.image,
                    caption=image_caption,
                    use_column_width=True,
                    clamp=True,
                )
                st.warning(
                    "Preview windowing and a single exported frame can hide information. Review the complete diagnostic study in an approved viewer."
                )
            with right:
                st.subheader("Technical indicators")
                display = pd.DataFrame(
                    [
                        {"Indicator": key.replace("_", " ").title(), "Value": value}
                        for key, value in metrics.items()
                    ]
                )
                st.dataframe(display, use_container_width=True, hide_index=True)
                safe_info = serialise_medical_image(loaded)
                if safe_info["safe_metadata"]:
                    with st.expander("Technical file metadata"):
                        st.json(safe_info["safe_metadata"])
                for warning in loaded.warnings:
                    st.warning(warning)
            st.subheader("Automated technical observations")
            for item in observations:
                st.write(f"- {item}")

    prompt = build_multimodal_prompt(case, clinical_context, clinical_question, metrics)
    with prompt_tab:
        st.write(
            "Upload the same de-identified image to an institution-approved multimodal tool, paste this prompt, and retain the output for the audit tab."
        )
        p1, p2, p3 = st.columns([1, 1, 1])
        with p1:
            st.link_button("Open ChatGPT ↗", "https://chatgpt.com/", use_container_width=True)
        with p2:
            st.link_button("Open Google Gemini ↗", "https://gemini.google.com/", use_container_width=True)
        with p3:
            st.link_button("Open Microsoft Copilot ↗", "https://copilot.microsoft.com/", use_container_width=True)
        st.code(prompt, language="text", wrap_lines=True)
        st.download_button(
            "Download multimodal prompt",
            prompt.encode("utf-8"),
            file_name=f"{case['case_id'].lower()}_multimodal_prompt.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with checklist_tab:
        left, right = st.columns(2, gap="large")
        with left:
            st.subheader("Systematic review")
            checked = [
                st.checkbox(item, key=f"imaging_review_{case['case_id']}_{index}")
                for index, item in enumerate(case["systematic_review"])
            ]
            st.progress(
                sum(checked) / len(checked),
                text=f"Review completed: {sum(checked)}/{len(checked)}",
            )
        with right:
            st.subheader("Cannot-miss escalation")
            for item in case["cannot_miss"]:
                st.error(item)
            st.subheader("Case-specific limitations")
            for item in case["limitations"]:
                st.write(f"- {item}")
        st.info(
            f"The accountable final reviewer for this workflow is the {case['human_owner']}. "
            "An AI-generated checklist or draft is never the signed report."
        )

    draft_review = None
    with audit_tab:
        draft = st.text_area(
            "Paste the AI-assisted draft",
            height=280,
            placeholder="Paste the draft returned by the multimodal AI tool. Remove identifiers first.",
        )
        if draft:
            draft_review = review_ai_draft(draft)
            st.metric("Structural safety score", f"{draft_review['score']}/100")
            a1, a2 = st.columns(2)
            with a1:
                st.success(
                    "Present sections: "
                    + (", ".join(draft_review["present_sections"]) or "None detected")
                )
                if draft_review["missing_sections"]:
                    st.warning("Missing: " + ", ".join(draft_review["missing_sections"]))
            with a2:
                if draft_review["risk_phrases"]:
                    st.error("Language risks: " + ", ".join(draft_review["risk_phrases"]))
                else:
                    st.info("No predefined high-risk phrase was detected.")
            st.subheader("Required review actions")
            for item in draft_review["recommendations"]:
                st.write(f"- {item}")
            st.caption(
                "This text audit checks structure and selected high-risk phrases only. It cannot verify whether image observations are correct."
            )

    with export_tab:
        payload = export_session_payload(
            case,
            clinical_context,
            clinical_question,
            metrics,
            observations,
            draft_review,
        )
        st.subheader("De-identified session record")
        st.json(payload)
        st.download_button(
            "Download session audit JSON",
            json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8"),
            file_name=f"{case['case_id'].lower()}_imaging_session.json",
            mime="application/json",
            use_container_width=True,
        )
        st.caption(
            "The exported JSON intentionally excludes the uploaded image, filename, DICOM identifiers and AI draft text."
        )
