from __future__ import annotations

import streamlit as st

from modules import (
    about, assessment, cases, data_explorer, facilitator, governance, home,
    labs, medical_artifact_lab, prompt_studio, resources, theory, tool_demos,
    tool_directory,
)
from modules.common import APP_SUBTITLE, APP_TITLE, configure_page, footer

configure_page()

PAGES = {
    "Home": ("🏠", home.render),
    "Theory deck": ("🖥️", theory.render),
    "Tool directory": ("🧰", tool_directory.render),
    "Tool demo lab": ("▶️", tool_demos.render),
    "Medical artifact lab": ("🩻", medical_artifact_lab.render),
    "Prompt studio": ("✨", prompt_studio.render),
    "Hands-on labs": ("🧪", labs.render),
    "Data explorer": ("📊", data_explorer.render),
    "Case conference": ("🗣️", cases.render),
    "Governance": ("🛡️", governance.render),
    "Assessment": ("✅", assessment.render),
    "Facilitator dashboard": ("🎛️", facilitator.render),
    "Resources": ("⬇️", resources.render),
    "About": ("ℹ️", about.render),
}

with st.sidebar:
    st.markdown("### ALKEM  |  AI MASTERCLASS")
    st.markdown(f"## {APP_TITLE}")
    st.caption(APP_SUBTITLE)
    st.divider()
    labels = [f"{icon}  {name}" for name, (icon, _) in PAGES.items()]
    selection = st.radio("Navigate", labels, label_visibility="collapsed", key="main_navigation")
    page_name = selection.split("  ", 1)[1]
    st.divider()
    completed = len(st.session_state.completed_labs)
    st.progress(completed / 6, text=f"Labs {completed}/6")
    st.toggle("Facilitator mode", key="facilitator_mode")
    st.caption("Synthetic data only. Human review is mandatory.")

PAGES[page_name][1]()
footer()
