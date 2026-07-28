from __future__ import annotations

import pandas as pd
import streamlit as st

from .common import DATA, download_asset, hero, metric_card, section_header, safety_banner, set_visited


def _synthetic_record_count() -> int:
    total = 0
    for path in DATA.glob("*.csv"):
        if path.name.startswith("tool_"):
            continue
        try:
            total += len(pd.read_csv(path))
        except Exception:
            pass
    return total


def render() -> None:
    set_visited("Home")
    hero(
        "Generative AI for Patient-Centric Healthcare",
        "An interactive 150-minute MDP studio built around the supplied workshop deck, 29 guided tool demonstrations, six case-based laboratories and synthetic healthcare/pharma datasets.",
    )
    safety_banner()

    cols = st.columns(4)
    with cols[0]: metric_card("10", "presentation pages with facilitation cues")
    with cols[1]: metric_card("29", "tools with guided demo playbooks")
    with cols[2]: metric_card("6 × 15", "case-based laboratory minutes")
    with cols[3]: metric_card(f"{_synthetic_record_count():,}", "synthetic records across the app")

    st.write("")
    left, right = st.columns([1.12, .88], gap="large")
    with left:
        section_header("Learning journey", "150-minute workshop flow", icon="⏱️")
        rows = [
            ("00–08", "Patient centricity, outcomes and safety boundary", "Theory"),
            ("08–20", "Why GenAI matters: capabilities and limits", "Theory + poll"),
            ("20–35", "Twelve application categories and tool selection", "Theory + demos"),
            ("35–50", "Clinical, pharma and research workflows", "Theory + demos"),
            ("50–60", "Governance debate and laboratory briefing", "Discussion"),
            ("60–105", "Labs 1–3: communication, language and reasoning", "Hands-on"),
            ("105–150", "Labs 4–6: PV, research and patient feedback", "Hands-on + debrief"),
        ]
        html = "<div class='info-card'>"
        for time, phase, mode in rows:
            html += f"<div class='timeline-row'><div class='timeline-time'>{time}</div><div class='timeline-phase'>{phase}</div><div class='timeline-mode'>{mode}</div></div>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    with right:
        section_header("Start here", "Choose your pathway", icon="🧭")
        st.markdown(
            """
            <div class="info-card">
              <div class="icon-title"><span class="icon-orb">🧑‍⚕️</span><div><b>Participant pathway</b><br><span class="tiny">View the supplied deck, select a tool, use a linked synthetic record, complete verification and document a human decision.</span></div></div><br>
              <div class="icon-title"><span class="icon-orb">🎛️</span><div><b>Facilitator pathway</b><br><span class="tiny">Reveal presenter notes, run tool comparisons, monitor lab completion and use case-specific debrief questions.</span></div></div><br>
              <div class="icon-title"><span class="icon-orb">🔒</span><div><b>Local-first app</b><br><span class="tiny">No external AI API is called. Participants deliberately open official tool sites and use only synthetic records.</span></div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        participant = st.text_input("Participant/team name", value=st.session_state.participant_name, placeholder="e.g., Team Patient Voice")
        st.session_state.participant_name = participant
        completed = len(st.session_state.completed_labs)
        st.progress(completed / 6, text=f"Lab progress: {completed}/6 completed")

    st.write("")
    section_header("What changed", "Deck-aligned interactive redesign", icon="✨")
    c1, c2, c3 = st.columns(3)
    cards = [
        (c1, "🖥️", "Supplied deck replaces the old PPT", "All 10 pages are rendered at fixed aspect ratio, with responsive navigation and no browser-generated slide text overlap."),
        (c2, "▶️", "Every tool now has a demo", "Each of the 29 tools has a linked dataset, step sequence, prompt, expected output, verification checklist and safety badge."),
        (c3, "🧪", "Labs now mirror page 9", "The six 15-minute exercises match the presentation and include case briefs, downloadable records, tool-specific guidance and debrief prompts."),
    ]
    for col, icon, title, text in cards:
        with col:
            st.markdown(f"<div class='info-card'><div class='icon-title'><span class='icon-orb'>{icon}</span><div><h3 style='margin:.1rem 0'>{title}</h3></div></div><p>{text}</p></div>", unsafe_allow_html=True)

    st.write("")
    section_header("Core materials", "Download the updated workshop resources", icon="⬇️")
    d1, d2, d3 = st.columns(3)
    with d1:
        download_asset("Download supplied workshop PDF", "Practical-Tools-for-Doctors-and-Pharma-Professionals.pdf", "application/pdf", "home_pdf")
    with d2:
        download_asset("Download synthetic datasets", "Synthetic_Healthcare_Pharma_Datasets_Expanded.zip", "application/zip", "home_data")
    with d3:
        download_asset("Download updated workshop kit", "GenAI_Healthcare_MDP_Updated_Kit.zip", "application/zip", "home_kit")
