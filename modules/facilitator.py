from __future__ import annotations

import pandas as pd
import streamlit as st

from .common import load_csv, section_header, set_visited
from .content import LABS


def render() -> None:
    set_visited("Facilitator dashboard")
    section_header(
        "Delivery control",
        "Facilitator dashboard",
        "Run the 150-minute programme from the supplied 10-page deck, demonstrate selected tools with synthetic records and monitor completion of the six 15-minute exercises.",
        "🎛️",
    )

    if not st.session_state.facilitator_mode:
        st.warning("Facilitator mode is currently off. Use the sidebar toggle to reveal presenter notes on the Theory deck page.")

    tools = load_csv("tool_comparison_matrix.csv")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Theory", "60 min")
    c2.metric("Hands-on", "90 min")
    c3.metric("Deck pages", "10")
    c4.metric("Guided tools", len(tools))
    c5.metric("Labs", f"{len(st.session_state.completed_labs)}/6")

    agenda = pd.DataFrame(
        [
            [0, 5, "Page 1: contract and expectations", "State clinician-in-the-loop, synthetic-data-only and verification rules."],
            [5, 13, "Page 2: why GenAI matters", "Use a show-of-hands poll: time, communication, evidence or operations?"],
            [13, 27, "Page 3: 12-category landscape", "Demonstrate how to select a tool by task, risk and data boundary—not popularity."],
            [27, 38, "Pages 4–5: patient and doctor workflows", "Run one plain-language or documentation demo with a synthetic case."],
            [38, 48, "Pages 6–7: pharma and research", "Contrast MLR review, citation verification and manuscript assistance."],
            [48, 57, "Page 8: governance debate", "Use one case to identify data, decision, human and escalation controls."],
            [57, 60, "Page 9: lab briefing", "Assign teams, tools, datasets and the accept/edit/reject/escalate decision record."],
            [60, 105, "Labs 1–3", "Discharge simplification, multilingual counselling and differential diagnosis checks."],
            [105, 150, "Labs 4–6", "Adverse-event triage, literature review and patient-feedback dashboard, including debrief."],
        ],
        columns=["Start", "End", "Activity", "Facilitator cue"],
    )
    st.dataframe(agenda, use_container_width=True, hide_index=True)

    st.subheader("Recommended live-demo shortlist")
    shortlist = tools.loc[
        tools["Tool"].isin(
            ["ChatGPT", "Google Gemini", "Elicit", "Julius AI", "OpenEvidence", "Canva", "Napkin AI"]
        ),
        ["Icon", "Tool", "Application area", "Dataset", "Risk level", "Official URL"],
    ]
    st.dataframe(
        shortlist,
        use_container_width=True,
        hide_index=True,
        column_config={"Official URL": st.column_config.LinkColumn("Official site", display_text="Open ↗")},
    )
    st.caption("The full Tool demo lab contains guided instructions for all 29 tools. Select only the tools that fit the participants' roles, access and time.")

    st.subheader("Lab completion board")
    for idx, lab in enumerate(LABS, 1):
        done = lab["id"] in st.session_state.completed_labs
        st.write(f"{'✅' if done else '⬜'} Lab {idx}: {lab['title']} — {lab['duration']} min — {lab['dataset']}")

    st.subheader("Universal debrief sequence")
    st.markdown(
        "**1. Fidelity:** What was preserved or distorted?  **2. Safety:** What could harm a patient, trial, publication or regulatory process?  "
        "**3. Evidence:** What was verified and from where?  **4. Human authority:** What did the professional accept, edit, reject or escalate?  "
        "**5. Workflow fit:** What access control, audit trail and stop condition would be required for a pilot?"
    )
