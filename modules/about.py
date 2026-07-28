from __future__ import annotations

import streamlit as st

from .common import ASSETS, section_header, set_visited


def render() -> None:
    set_visited("About")
    section_header("About the learning studio", "Designed for responsible executive education", icon="ℹ️")
    left, right = st.columns([.9, 1.1], gap="large")
    with left:
        st.image(ASSETS / "workshop.png", use_container_width=True)
    with right:
        st.markdown(
            """
            ### Dr. Alok Tiwari
            **Assistant Professor – Big Data Analytics, Goa Institute of Management**

            This application packages a 150-minute Alkem AI Masterclass for doctors and pharma professionals. It combines a refreshed, editable 12-slide four-pillar theory sequence with interactive synthetic-data laboratories.

            **Focus areas:** AI in healthcare, healthcare analytics, medical imaging, machine learning, research methods, executive education and responsible GenAI adoption.
            """
        )
        st.link_button("View academic portfolio ↗", "https://dr-alok-tiwari.github.io/", use_container_width=True)
        st.link_button("View GitHub profile ↗", "https://github.com/dr-alok-tiwari", use_container_width=True)

    st.divider()
    st.subheader("Scope and disclaimer")
    st.info(
        "This educational app is not a medical device and does not provide diagnosis, treatment, prescribing, trial-enrolment, medical-information approval or pharmacovigilance causality decisions. Users must follow applicable institutional policies, privacy requirements, regulations and professional standards."
    )
    st.subheader("Local-first architecture")
    st.write(
        "The application reads its bundled PDF page images, CSV datasets, JSON metadata and downloadable files locally. It does not transmit entered text to an AI provider. External tool websites open only when a participant deliberately selects an official link."
    )
    st.subheader("Workshop content at a glance")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Presentation slides", 12)
    c2.metric("Guided tool demos", 29)
    c3.metric("Synthetic datasets", 20)
    c4.metric("Hands-on exercises", 6)
