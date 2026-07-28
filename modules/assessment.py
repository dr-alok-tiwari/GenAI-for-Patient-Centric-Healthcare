from __future__ import annotations

import json

import streamlit as st

from .common import json_download, section_header, set_visited
from .content import QUIZ


def render() -> None:
    set_visited("Assessment")
    section_header("Knowledge check", "Assessment and implementation pledge", "Complete the quiz, review explanations and record one responsible use case you will pilot after the MDP.")

    with st.form("quiz_form"):
        answers = []
        for i, item in enumerate(QUIZ, 1):
            st.markdown(f"**{i}. {item['q']}**")
            ans = st.radio("Select one", item["options"], index=None, key=f"quiz_{i}", label_visibility="collapsed")
            answers.append(ans)
            st.write("")
        submitted = st.form_submit_button("Submit assessment", type="primary", use_container_width=True)

    if submitted:
        score = sum(ans == item["options"][item["answer"]] for ans, item in zip(answers, QUIZ))
        st.session_state.quiz_submitted = True
        st.session_state.quiz_score = score
        st.session_state.quiz_answers = answers

    if st.session_state.quiz_submitted:
        score = st.session_state.quiz_score
        pct = round(score / len(QUIZ) * 100)
        st.metric("Score", f"{score}/{len(QUIZ)}", f"{pct}%")
        if pct >= 80:
            st.success("Strong understanding. Focus next on organisational controls and measurable pilot outcomes.")
        elif pct >= 60:
            st.warning("Good foundation. Review the explanations below before planning a pilot.")
        else:
            st.error("Revisit the governance and lab review sections before applying GenAI in a serious workflow.")
        with st.expander("Review answers and explanations", expanded=True):
            stored = st.session_state.get("quiz_answers", [])
            for i, (ans, item) in enumerate(zip(stored, QUIZ), 1):
                correct = item["options"][item["answer"]]
                icon = "✓" if ans == correct else "✗"
                st.markdown(f"**{icon} Q{i}. Correct answer: {correct}**")
                st.write(item["explanation"])

    st.divider()
    section_header("Transfer to practice", "My 30-day responsible pilot")
    c1, c2 = st.columns(2)
    with c1:
        pilot = st.text_area("Use case and current pain point", height=120, placeholder="Describe one low-risk workflow...")
        owner = st.text_input("Accountable owner/team")
        measure = st.text_input("Success measure", placeholder="e.g., comprehension score, turnaround time, error rate")
    with c2:
        data_rule = st.text_area("Data boundary", height=90, placeholder="What data may and may not be used?")
        review_rule = st.text_area("Human review and escalation", height=90)
        stop_rule = st.text_input("Stop condition", placeholder="When will the pilot be paused?")
    plan = {
        "participant_or_team": st.session_state.participant_name,
        "use_case": pilot,
        "owner": owner,
        "success_measure": measure,
        "data_boundary": data_rule,
        "human_review_and_escalation": review_rule,
        "stop_condition": stop_rule,
        "labs_completed": sorted(st.session_state.completed_labs),
        "quiz_score": st.session_state.quiz_score if st.session_state.quiz_submitted else None,
    }
    st.download_button("Download implementation plan", json_download(plan, "implementation_plan.json"), file_name="30_day_genai_pilot_plan.json", mime="application/json", use_container_width=True)
