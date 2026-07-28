from __future__ import annotations

import pandas as pd
import streamlit as st

from .brand import PILLARS
from .common import DATA, download_asset, hero, metric_card, section_header, safety_banner, set_visited


def _synthetic_record_count() -> int:
    total = 0
    for path in DATA.glob("*.csv"):
        if path.name.startswith("tool_"):
            continue
        try:
            total += len(pd.read_csv(path))
        except Exception:
            continue
    return total


def render() -> None:
    set_visited("Home")
    hero(
        "GenAI for Patient-Centric Healthcare",
        "A practical Alkem AI Masterclass: 60 minutes of concise concepts and medical examples, followed by 90 minutes of safe, case-based practice for doctors and pharma professionals.",
    )
    safety_banner()

    cols = st.columns(4)
    with cols[0]:
        metric_card("12", "editable, healthcare-specific theory slides")
    with cols[1]:
        metric_card("29", "verified tools with guided demos")
    with cols[2]:
        metric_card("24", "fully covered role-to-workflow pathways")
    with cols[3]:
        metric_card(f"{_synthetic_record_count():,}", "synthetic records across the app")

    st.write("")
    section_header(
        "Programme architecture",
        "Four pillars, one accountable workflow",
        "Each pillar connects a medical or pharma need to a bounded prompt, synthetic input, verification checklist, and named human decision-maker.",
        "🧭",
    )
    pillar_cols = st.columns(4)
    for col, pillar in zip(pillar_cols, PILLARS):
        with col:
            st.markdown(
                f"""
                <div class="info-card" style="border-top:5px solid {pillar['colour']}">
                  <div class="icon-title"><span class="icon-orb">{pillar['icon']}</span>
                  <div><h3 style="margin:.05rem 0">{pillar['short']}</h3></div></div>
                  <p>{pillar['promise']}</p>
                  <span class="tiny">{pillar['examples']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    left, right = st.columns([1.08, .92], gap="large")
    with left:
        section_header("Learning journey", "150-minute masterclass flow", icon="⏱️")
        rows = [
            ("00–08", "Contract: synthetic data, human authority, measurable outcomes", "Theory"),
            ("08–22", "Pillar 1: patient understanding and prescription explanation", "Theory + demo"),
            ("22–36", "Pillar 2: clinical workflow and image-observation boundary", "Theory + demo"),
            ("36–50", "Pillar 3: PV, evidence and professional productivity", "Theory + demo"),
            ("50–60", "Pillar 4: governance, controls and lab briefing", "Discussion"),
            ("60–105", "Labs 1–3: prescription, image, discharge and teach-back", "Hands-on"),
            ("105–150", "Labs 4–6: reasoning, PV and evidence verification", "Hands-on + debrief"),
        ]
        html = "<div class='info-card'>"
        for time, phase, mode in rows:
            html += (
                f"<div class='timeline-row'><div class='timeline-time'>{time}</div>"
                f"<div class='timeline-phase'>{phase}</div><div class='timeline-mode'>{mode}</div></div>"
            )
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)
    with right:
        section_header("Start here", "Choose a safe practice route", icon="🚦")
        st.markdown(
            """
            <div class="info-card">
              <div class="icon-title"><span class="icon-orb">🩻</span><div><b>Medical artifact lab</b><br>
              <span class="tiny">Use a synthetic prescription or radiograph, a bounded prompt, and a qualified-human decision record.</span></div></div><br>
              <div class="icon-title"><span class="icon-orb">✨</span><div><b>Prompt studio</b><br>
              <span class="tiny">Every visible dropdown combination is backed by a complete healthcare workflow and dataset.</span></div></div><br>
              <div class="icon-title"><span class="icon-orb">🔒</span><div><b>Local-first learning</b><br>
              <span class="tiny">The app does not call an external model service. Participants open approved tools deliberately and use synthetic records.</span></div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        participant = st.text_input(
            "Participant/team name",
            value=st.session_state.participant_name,
            placeholder="e.g., Team Patient Voice",
        )
        st.session_state.participant_name = participant
        completed = len(st.session_state.completed_labs)
        st.progress(completed / 6, text=f"Lab progress: {completed}/6 completed")

    st.write("")
    section_header("Take-home materials", "Use the same system after the session", icon="⬇️")
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        download_asset(
            "Download masterclass deck",
            "Alkem_AI_Masterclass_Healthcare.pptx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "home_pptx",
        )
    with d2:
        download_asset(
            "Download participant workbook",
            "Alkem_AI_Masterclass_Participant_Workbook.pdf",
            "application/pdf",
            "home_workbook",
        )
    with d3:
        download_asset(
            "Download synthetic datasets",
            "Synthetic_Healthcare_Pharma_Datasets_Expanded.zip",
            "application/zip",
            "home_data",
        )
    with d4:
        download_asset(
            "Download complete kit",
            "Alkem_AI_Masterclass_Healthcare_Kit.zip",
            "application/zip",
            "home_kit",
        )
