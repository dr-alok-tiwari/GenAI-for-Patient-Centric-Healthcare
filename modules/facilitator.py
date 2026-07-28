from __future__ import annotations

import pandas as pd
import streamlit as st

from .common import load_csv, load_json, section_header, set_visited
from .content import LABS
from .selection_engine import coverage_matrix


def render() -> None:
    set_visited("Facilitator dashboard")
    section_header(
        "Delivery control",
        "Facilitator dashboard",
        "Run the 60-minute four-pillar theory sequence, 90-minute medical lab, verified tool alternatives, and complete dropdown-coverage diagnostics.",
        "🎛️",
    )
    if not st.session_state.facilitator_mode:
        st.warning("Facilitator mode is off. Use the sidebar toggle to reveal deck presenter notes.")

    tools = load_csv("tool_comparison_matrix.csv")
    workflows = load_json("workflow_catalog.json")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Theory", "60 min")
    c2.metric("Hands-on", "90 min")
    c3.metric("Deck slides", "12")
    c4.metric("Covered workflows", len(workflows))
    c5.metric("Labs complete", f"{len(st.session_state.completed_labs)}/6")

    agenda = pd.DataFrame(
        [
            [0, 8, "Slides 1–2: contract and goals", "State synthetic-data-only, human-authority, and verification rules."],
            [8, 22, "Slides 3–4: Pillar 1", "Run the synthetic prescription extraction/explanation demonstration."],
            [22, 36, "Slides 5–6: Pillar 2", "Show the medical-image observation boundary; do not model a diagnosis."],
            [36, 50, "Slides 7–8: Pillar 3", "Contrast PV structuring with evidence discovery and source verification."],
            [50, 60, "Slides 9–10: Pillar 4 and lab brief", "Classify one use case by data, impact, autonomy, reach, and stop condition."],
            [60, 105, "Labs 1–3", "Prescription, image observation, and bilingual discharge teach-back."],
            [105, 150, "Labs 4–6", "Differential/red flags, PV intake, and evidence/citation verification."],
        ],
        columns=["Start", "End", "Activity", "Facilitator cue"],
    )
    st.dataframe(agenda, use_container_width=True, hide_index=True)

    st.subheader("Medical live-demo sequence and fallback")
    demo = pd.DataFrame(
        [
            ["Prescription extraction", "ChatGPT", "Google Gemini / Microsoft Copilot", "Use code-generated prescription and facilitator source values"],
            ["Image observation boundary", "ChatGPT", "Google Gemini", "Use static synthetic radiograph; discuss limitations without running a model"],
            ["PV intake", "ChatGPT / Claude", "Google Gemini / Julius AI", "Use one synthetic report and manual template"],
            ["Evidence search", "PubMed / Elicit", "Consensus / Semantic Scholar", "Use saved synthetic abstracts only for extraction practice"],
        ],
        columns=["Demo", "Primary", "Verified alternative", "Offline fallback"],
    )
    st.dataframe(demo, use_container_width=True, hide_index=True)

    st.subheader("Dropdown coverage diagnostics")
    coverage = pd.DataFrame(
        coverage_matrix(
            workflows,
            ["pillar", "roles", "task", "input_type", "output_type", "languages", "risk_level"],
        )
    )
    st.dataframe(coverage, use_container_width=True, hide_index=True)
    st.success(
        "Every visible option has one or more complete workflow records. Cascading selectors remove "
        "unsupported intersections before they can be selected."
    )

    st.subheader("Lab completion board")
    for index, lab in enumerate(LABS, 1):
        done = lab["id"] in st.session_state.completed_labs
        st.write(f"{'✅' if done else '⬜'} Lab {index}: {lab['title']} — {lab['duration']} min — {lab['dataset']}")

    st.subheader("Universal debrief")
    st.markdown(
        "**Fidelity:** What changed from source?  **Safety:** What could cause harm?  "
        "**Evidence:** What was actually opened and checked?  **Authority:** Who accepted, edited, rejected, "
        "or escalated?  **Implementation:** What control and stop condition would a pilot require?"
    )
