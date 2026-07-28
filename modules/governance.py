from __future__ import annotations

import streamlit as st

from .common import section_header, set_visited
from .content import RISK_CONTROLS


def render() -> None:
    set_visited("Governance")
    section_header("Responsible adoption", "Risk and governance workbench", "Classify a proposed GenAI use case, view the minimum controls and convert the result into a pilot decision.")

    left, right = st.columns([.9, 1.1], gap="large")
    with left:
        use_case = st.text_input("Proposed use case", placeholder="e.g., simplifying discharge instructions")
        data = st.select_slider("Data sensitivity", options=["Synthetic/public", "De-identified internal", "Identifiable patient data", "Highly sensitive/regulated"], value="Synthetic/public")
        impact = st.select_slider("Potential patient impact", options=["None", "Indirect", "Could influence care", "Direct clinical action"], value="Indirect")
        autonomy = st.select_slider("Automation level", options=["Draft only", "Human-approved recommendation", "Default recommendation", "Autonomous action"], value="Draft only")
        audience = st.select_slider("Output reach", options=["Private sandbox", "Internal team", "Individual patient/HCP", "Public or population scale"], value="Internal team")

    scores = {
        "data": ["Synthetic/public", "De-identified internal", "Identifiable patient data", "Highly sensitive/regulated"].index(data),
        "impact": ["None", "Indirect", "Could influence care", "Direct clinical action"].index(impact),
        "autonomy": ["Draft only", "Human-approved recommendation", "Default recommendation", "Autonomous action"].index(autonomy),
        "audience": ["Private sandbox", "Internal team", "Individual patient/HCP", "Public or population scale"].index(audience),
    }
    total = sum(scores.values())
    if total <= 2:
        tier = "Low"
        css = "risk-low"
    elif total <= 5:
        tier = "Moderate"
        css = "risk-medium"
    elif total <= 8:
        tier = "High"
        css = "risk-high"
    else:
        tier = "Critical"
        css = "risk-critical"

    with right:
        st.markdown(f"<div class='info-card {css}'><div class='section-label'>Indicative risk tier</div><h1>{tier}</h1><p>Score: {total}/12</p></div>", unsafe_allow_html=True)
        st.subheader("Minimum controls")
        for control in RISK_CONTROLS[tier]:
            st.checkbox(control, key=f"control_{tier}_{control}")
        if tier == "Critical":
            st.error("Do not proceed as an autonomous GenAI pilot. Redesign the scope or use a formally validated, regulated pathway.")
        elif tier == "High":
            st.warning("A formal multidisciplinary review is required before deployment.")
        else:
            st.success("A tightly scoped, monitored pilot may be appropriate after institutional review.")

    st.divider()
    section_header("Operational checklist", "Before every serious prompt")
    cols = st.columns(3)
    groups = [
        ("Data", ["Minimum necessary fields", "No direct identifiers", "Approved storage and retention"]),
        ("Output", ["Missingness visible", "No invented facts", "Sources verified where relevant"]),
        ("Accountability", ["Named reviewer", "Escalation pathway", "Decision and edits documented"]),
    ]
    for col, (title, items) in zip(cols, groups):
        with col:
            st.markdown(f"<div class='info-card'><h3>{title}</h3>" + "".join(f"<p>✓ {x}</p>" for x in items) + "</div>", unsafe_allow_html=True)
