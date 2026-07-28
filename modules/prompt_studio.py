from __future__ import annotations

import textwrap

import streamlit as st

from .common import badges, load_csv, load_json, record_to_text, section_header, set_visited

TASKS = {
    "Patient education": "Transform the supplied facts into a patient-friendly explanation and action plan with teach-back questions.",
    "Multilingual counselling": "Create a bilingual counselling draft that preserves medicine/test names and flags translation review needs.",
    "Clinical reasoning checklist": "Separate common, likely, cannot-miss and missing-information items without giving a final diagnosis or treatment.",
    "Clinical documentation draft": "Structure the supplied encounter into a reviewable document while marking assumptions and missing facts.",
    "Medical information response": "Draft a balanced, non-promotional response workflow and specify evidence, MLR and PV escalation requirements.",
    "Pharmacovigilance intake": "Structure seriousness screening, missing fields, follow-up questions and a neutral narrative without unsupported causality.",
    "Research synthesis": "Create a reproducible search/extraction plan and separate source facts from inference.",
    "Patient feedback action plan": "Convert patient feedback into prioritised service-recovery and process-improvement actions with owners and measures.",
    "Professional communication": "Improve clarity, empathy and tone without adding or changing facts, claims, dates, doses or commitments.",
    "Governance assessment": "Classify the proposed AI use case and specify minimum controls, approval roles, monitoring and stop conditions.",
}


def render() -> None:
    set_visited("Prompt studio")
    section_header(
        "Prompt engineering",
        "Healthcare prompt studio",
        "Build a prompt with explicit role, context, task, constraints, output and verification. Use any of the expanded synthetic datasets as structured input.",
        "✨",
    )
    registry = load_json("dataset_registry.json")
    dataset_options = {"No dataset — write a general prompt": None}
    dataset_options.update({f"{meta['icon']} {meta['name']}": filename for filename, meta in registry.items() if filename != "tool_demo_playbook.csv"})

    left, right = st.columns([.9, 1.1], gap="large")
    with left:
        use_case = st.selectbox("Use case", list(TASKS))
        role = st.text_input("Qualified reviewer role", value="clinician / medical affairs / research professional")
        audience = st.selectbox("Audience", ["Patient and caregiver", "Doctor/clinical team", "Medical affairs/PV team", "Research team", "Hospital leadership", "Public/professional audience"])
        language = st.selectbox("Language", ["English", "Hindi", "Marathi", "Konkani", "Bengali", "Tamil", "Telugu", "Kannada", "Malayalam", "Spanish", "Other — specify in task"])
        output_format = st.multiselect(
            "Output components",
            ["Executive summary", "Table", "Checklist", "Step-by-step plan", "Red flags", "Missing-information list", "Source-verification table", "Teach-back questions", "Owner and metric", "Stop conditions"],
            default=["Executive summary", "Checklist", "Missing-information list"],
        )
        dataset_label = st.selectbox("Optional synthetic dataset", list(dataset_options))
        record_text = "[Insert synthetic or institution-approved context here]"
        selected_file = dataset_options[dataset_label]
        if selected_file:
            df = load_csv(selected_file)
            id_col = df.columns[0]
            record_id = st.selectbox("Record", df[id_col].astype(str).tolist())
            row = df.loc[df[id_col].astype(str) == record_id].iloc[0]
            record_text = record_to_text(row)
            badges([f"📁 {selected_file}", "🧬 Synthetic"])
        strictness = st.slider("Safety strictness", 1, 5, 5, help="Higher values add more explicit limits, uncertainty handling and escalation language.")

    safeguards = [
        "Use only the supplied data and do not invent clinical facts, doses, dates, references, test results or patient details.",
        "Mark missing information, assumptions and uncertainty clearly.",
        "Do not make autonomous diagnosis, prescribing, trial-enrolment, causality or regulatory decisions.",
        "Use citations only when the source can be opened and verified; never fabricate bibliographic metadata.",
        "Flag red flags, escalation needs and the qualified human role responsible for approval.",
    ]
    selected_safeguards = safeguards[:max(1, strictness)]
    output_text = ", ".join(output_format) if output_format else "a clearly structured response"
    prompt = textwrap.dedent(
        f"""
        ROLE
        You are a GenAI drafting assistant supporting a qualified {role}. You do not replace professional judgement.

        CONTEXT
        Audience: {audience}
        Language: {language}
        Use case: {use_case}
        Data classification: synthetic educational data unless explicitly stated otherwise.

        INPUT
        {record_text}

        TASK
        {TASKS[use_case]}

        SAFETY AND QUALITY CONSTRAINTS
        """
    ).strip()
    prompt += "\n" + "\n".join(f"- {item}" for item in selected_safeguards)
    prompt += f"\n\nOUTPUT FORMAT\nReturn {output_text}. Separate source facts, assumptions, interpretation and recommendations.\n\nFINAL VERIFICATION\nEnd with a checklist for the {role}, including what must be checked against the source and what requires escalation."

    with right:
        st.subheader("Generated prompt")
        st.code(prompt, language="text", wrap_lines=True)
        score = min(100, 42 + 7 * len(output_format) + 7 * strictness)
        st.progress(score / 100, text=f"Prompt completeness score: {score}/100")
        st.download_button("Download prompt as TXT", prompt.encode("utf-8"), file_name="healthcare_genai_prompt.txt", mime="text/plain", use_container_width=True)
        with st.expander("Why this prompt is safer"):
            st.write("It names the accountable reviewer, limits invention, keeps missingness visible, separates facts from interpretation and ends with explicit source and escalation checks.")

    st.divider()
    section_header("Reusable formula", "R-C-T-C-O-V", icon="🧱")
    cols = st.columns(6)
    labels = [
        ("R", "Role", "Who the model assists"), ("C", "Context", "Audience and situation"),
        ("T", "Task", "One clear objective"), ("C", "Constraints", "Safety and boundaries"),
        ("O", "Output", "Required structure"), ("V", "Verify", "Human review checks"),
    ]
    for col, (letter, name, desc) in zip(cols, labels):
        with col:
            st.markdown(f"<div class='metric-card'><div class='value'>{letter}</div><div class='label'><b>{name}</b><br>{desc}</div></div>", unsafe_allow_html=True)
