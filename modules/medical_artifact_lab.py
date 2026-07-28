from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from .brand import SAFETY_ACKNOWLEDGEMENT
from .common import ASSETS, badges, load_csv, record_to_text, section_header, set_visited

MEDICAL = ASSETS / "medical"


def _decision_record(key: str, checks: list[str]) -> None:
    st.subheader("3. Verify and record the human decision")
    completed = [
        st.checkbox(item, key=f"{key}_check_{index}")
        for index, item in enumerate(checks)
    ]
    st.progress(
        sum(completed) / len(completed),
        text=f"Verification completed: {sum(completed)}/{len(completed)}",
    )
    decision = st.radio(
        "Qualified human decision",
        ["Accept after verification", "Edit", "Reject", "Escalate"],
        horizontal=True,
        key=f"{key}_decision",
    )
    rationale = st.text_area(
        "Evidence checked, edits made, uncertainty, and escalation",
        key=f"{key}_rationale",
        height=135,
        placeholder="Name the source fields checked and explain the decision...",
    )
    if all(completed) and rationale.strip():
        st.success(f"Decision recorded: {decision}. This remains an educational, session-local note.")
    else:
        st.info("Complete every relevant check and document the rationale before treating the exercise as finished.")


def _prescription_lab() -> None:
    records = load_csv("prescription_cases.csv")
    labels = {
        f"{row.prescription_id} — {row.medicine}": row.prescription_id
        for row in records.itertuples()
    }
    choice = st.selectbox("Synthetic prescription case", list(labels), key="rx_case")
    record = records.loc[records["prescription_id"] == labels[choice]].iloc[0]

    c1, c2 = st.columns([0.8, 1.2], gap="large")
    with c1:
        st.subheader("1. Inspect the source")
        st.image(MEDICAL / str(record["image_file"]), caption="Fully synthetic mock prescription", use_container_width=True)
        with st.expander("Facilitator reference values"):
            st.dataframe(record.drop(labels=["image_file"]).rename("Source value"), use_container_width=True)
        upload = st.file_uploader(
            "Optional local practice image",
            type=["png", "jpg", "jpeg"],
            key="rx_upload",
            help="Preview only. The app does not save the upload or send it to an AI service.",
        )
        if upload:
            st.image(upload, caption="Session-only local preview", use_container_width=True)
            st.warning("Before using any external tool, confirm that the image is synthetic or approved and contains no identifiers.")
    with c2:
        st.subheader("2. Run a bounded prompt")
        prompt = (
            "You are assisting a qualified clinician or pharmacist. Use only the supplied SYNTHETIC "
            "prescription image.\n\nA. EXACT EXTRACTION\nReturn a table with medicine/product, strength, "
            "route, frequency, duration, follow-up/warning, and confidence for each field. Use [UNREADABLE] "
            "instead of guessing.\n\nB. PATIENT EXPLANATION\nExplain the legible instructions in plain language "
            "without adding advice. Keep medicine names, strengths, and instructions exactly aligned to the "
            "source.\n\nC. SAFETY\nDo not prescribe, substitute, infer an indication, assess interactions, or "
            "reconstruct unclear content. State that the prescription and qualified reviewer are authoritative.\n\n"
            "D. VERIFY\nEnd with a field-by-field source comparison and three teach-back questions."
        )
        st.code(prompt, language="text", wrap_lines=True)
        st.link_button("Open ChatGPT image input ↗", "https://chatgpt.com/", use_container_width=True)
        st.caption("Tool access and image capability can change. Use only an organisation-approved account and data boundary.")
        output = st.text_area(
            "Paste the tool output here for review",
            height=240,
            key="rx_output",
            placeholder="The app does not call an external model. Paste a result here to practise verification...",
        )
        if output:
            st.write("Compare the pasted result to the synthetic source image and facilitator reference values—not to fluency.")
        _decision_record(
            "rx",
            [
                "Every medicine/product and strength matches the image",
                "Frequency, duration, and warnings match the image",
                "Unreadable or absent content was not guessed",
                "No indication, interaction, substitution, or new advice was added",
                "A clinician or pharmacist retains the final decision",
            ],
        )


def _image_lab() -> None:
    records = load_csv("imaging_cases.csv")
    labels = {
        f"{row.image_id} — {row.modality} • {row.view}": row.image_id
        for row in records.itertuples()
    }
    choice = st.selectbox("Synthetic image case", list(labels), key="img_case")
    record = records.loc[records["image_id"] == labels[choice]].iloc[0]

    c1, c2 = st.columns([0.82, 1.18], gap="large")
    with c1:
        st.subheader("1. Inspect the source")
        st.image(MEDICAL / str(record["image_file"]), caption="Fully AI-generated synthetic radiograph; no diagnostic ground truth", use_container_width=True)
        st.dataframe(
            pd.Series(
                {
                    "Modality": record["modality"],
                    "Region": record["body_region"],
                    "View": record["view"],
                    "Training goal": record["training_goal"],
                },
                name="Value",
            ),
            use_container_width=True,
        )
        upload = st.file_uploader(
            "Optional local practice image",
            type=["png", "jpg", "jpeg"],
            key="img_upload",
            help="Preview only. The app does not persist it or call an AI service.",
        )
        if upload:
            st.image(upload, caption="Session-only local preview", use_container_width=True)
            st.warning("Do not upload real medical images to an unapproved tool. Remove identifiers and follow institutional policy.")
    with c2:
        st.subheader("2. Run a non-diagnostic observation prompt")
        st.markdown(
            "<div class='safety-banner'><b>Important limitation:</b> General-purpose image models are not "
            "a substitute for a radiologist or a validated medical-device workflow. The exercise teaches "
            "observation discipline, limitation reporting, and escalation—not image diagnosis.</div>",
            unsafe_allow_html=True,
        )
        prompt = (
            "This is a fully synthetic training image with no diagnostic ground truth. Do not diagnose or "
            "recommend treatment.\n\n1. IMAGE ADEQUACY: Comment only on visible projection/positioning, "
            "inspiration, rotation, exposure, artefact, and important limitations.\n2. STRUCTURED VISIBLE "
            "OBSERVATIONS: Describe visible features by region using neutral language; do not label a disease.\n"
            "3. UNCERTAINTY: List what cannot be assessed and where image quality limits confidence.\n"
            "4. ESCALATION: State what a qualified radiologist or treating clinician must verify and that "
            "real images require approved clinical workflows.\n5. SAFETY CHECK: Confirm that no diagnosis, "
            "triage clearance, or treatment recommendation was made."
        )
        st.code(prompt, language="text", wrap_lines=True)
        st.link_button("Read ChatGPT image-input limitations ↗", "https://help.openai.com/articles/8400551-chatgpt-image-inputs-faq", use_container_width=True)
        output = st.text_area(
            "Paste the tool output here for review",
            height=220,
            key="img_output",
            placeholder="Judge the result for structure, unsupported inference, uncertainty, and escalation...",
        )
        if output:
            st.write("There is intentionally no AI-generated 'correct diagnosis.' Evaluate whether the output stayed inside the observation boundary.")
        _decision_record(
            "img",
            [
                "Image adequacy and limitations were considered first",
                "Observations stayed descriptive and non-diagnostic",
                "Cannot-assess items and uncertainty are explicit",
                "No triage clearance or treatment recommendation appears",
                "Qualified clinical interpretation and approved workflow are explicit",
            ],
        )


def render() -> None:
    set_visited("Medical artifact lab")
    section_header(
        "Medical-specific demonstration",
        "Prescription and medical-image safety lab",
        "Practise upload workflows with fully synthetic assets, bounded prompts, reference checks, and an explicit qualified-human decision.",
        "🩻",
    )
    badges(["🧬 Fully synthetic assets", "🔒 No upload is persisted", "🚫 Not diagnostic", "🧑‍⚕️ Qualified review"])
    acknowledged = st.checkbox(SAFETY_ACKNOWLEDGEMENT, key="artifact_ack")
    if not acknowledged:
        st.warning("Acknowledge the data and decision boundary to unlock the exercises.")
        return
    rx_tab, image_tab = st.tabs(["💊 Prescription extraction", "🩻 Medical-image observation"])
    with rx_tab:
        _prescription_lab()
    with image_tab:
        _image_lab()
