from __future__ import annotations

import streamlit as st

from .common import badges, download_dataset, load_csv, record_to_text, section_header, set_visited


def render() -> None:
    set_visited("Case conference")
    section_header(
        "Facilitated discussion",
        "Clinical, pharma and governance case conference",
        "The cases extend the debate prompts on page 8 of the supplied deck. Each scenario is linked to a synthetic dataset so teams can move from discussion to a documented workflow decision.",
        "🗣️",
    )
    cases = load_csv("case_conference_scenarios.csv")
    title = st.selectbox("Select case", cases["title"].tolist())
    case = cases.loc[cases["title"] == title].iloc[0]

    st.markdown(
        f"""
        <div class='case-card'>
          <div class='icon-title'><span class='icon-orb'>🧩</span><div>
          <div class='section-label'>{case['domain']}</div><h2 style='margin:.05rem 0'>{case['title']}</h2></div></div>
          <p><b>Scenario:</b> {case['scenario']}</p>
          <p><b>Available synthetic evidence:</b> {case['synthetic_evidence']}</p>
          <p><b>Decision goal:</b> {case['decision_goal']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tone = "high" if case["risk_level"] in {"High", "Critical"} else "medium"
    badges([f"⚠️ {case['risk_level']} risk", f"📁 {case['dataset_link']}", "🧑‍⚕️ Human accountability"], tone)

    linked = load_csv(case["dataset_link"])
    id_col = linked.columns[0]
    left, right = st.columns([.86, 1.14], gap="large")
    with left:
        st.subheader("Linked synthetic evidence")
        record_id = st.selectbox("Select supporting record", linked[id_col].astype(str).tolist(), key=f"case_record_{case['case_id']}")
        row = linked.loc[linked[id_col].astype(str) == record_id].iloc[0]
        st.dataframe(row.rename("Value"), use_container_width=True)
        download_dataset(case["dataset_link"], f"Download {case['dataset_link']}", key=f"case_data_{case['case_id']}")

    with right:
        tabs = st.tabs(["Team questions", "AI challenge prompt", "Decision record", "Facilitator guidance"])
        with tabs[0]:
            questions = [
                "What immediate patient, privacy, scientific or regulatory risk must be addressed?",
                "Which information is missing, and what must not be assumed?",
                "Who is accountable for review, approval and escalation?",
                "What data boundary, audit trail and stop condition are required?",
                "How will patient centricity, fairness and access be protected?",
            ]
            for i, question in enumerate(questions, 1):
                st.markdown(f"**{i}. {question}**")
        with tabs[1]:
            prompt = f"""This is a synthetic educational case for a multidisciplinary healthcare team.\n\nCASE\n{record_to_text(case)}\n\nSUPPORTING SYNTHETIC RECORD\n{record_to_text(row)}\n\nAnalyse the case without making an autonomous clinical, regulatory or research-integrity decision. Return: immediate risks, missing information, stakeholders, required controls, escalation path, audit evidence, patient-centred communication and a stop condition. Separate facts, assumptions and recommendations."""
            st.code(prompt, language="text", wrap_lines=True)
            st.download_button("Download case challenge prompt", prompt.encode("utf-8"), file_name=f"{case['case_id']}_challenge_prompt.txt", mime="text/plain", use_container_width=True)
        with tabs[2]:
            response = st.text_area("Team decision and rationale", height=260, key=f"case_{case['case_id']}", placeholder="Capture the decision, evidence, controls, owner and escalation pathway...")
            lenses = ["Patient centricity", "Safety", "Verification", "Accountability", "Documentation", "Escalation", "Fairness/access"]
            checked = [st.checkbox(item, key=f"lens_{case['case_id']}_{item}") for item in lenses]
            st.progress(sum(checked) / len(checked), text=f"Decision lenses addressed: {sum(checked)}/{len(checked)}")
            if response:
                st.download_button("Download team response", response.encode("utf-8"), file_name=f"{case['case_id']}_team_response.txt", mime="text/plain", use_container_width=True)
        with tabs[3]:
            if st.session_state.facilitator_mode:
                guidance = {
                    "CC-001": "Acknowledge concern, assess symptoms and adverse effects, explain that medicine changes require clinician review, agree on a monitored plan, document the chatbot advice and provide urgent-care red flags.",
                    "CC-002": "Limit scope to conservative navigation, minimise data, publish limitations, hard-code emergency redirection, validate each language, retain human override and audit failures.",
                    "CC-003": "Rebuild a reproducible search, preserve queries and screening criteria, verify each citation against the source, separate extraction from interpretation and disclose material AI use.",
                    "CC-004": "Reframe the problem, assess common and cannot-miss causes, seek disconfirming evidence, complete urgent tests and trigger senior review before action.",
                    "CC-005": "Clarify the unsolicited request, use approved medical-information channels, distinguish label from evidence, avoid recommendation or promotion, document sources and route safety information to PV.",
                    "CC-006": "Stop further sharing, follow incident response, assess exposure, notify privacy/governance, preserve evidence, redesign with approved systems, data minimisation and staff training.",
                }
                st.success(guidance.get(case["case_id"], "Apply the governance framework and document the accountable human decision."))
            else:
                st.info("Enable facilitator mode after team discussion to reveal guidance.")

    st.divider()
    st.subheader("60-second red-team challenge")
    st.write("Another team must identify one unsafe assumption, one missing stakeholder, one equity or access issue, and one control that would make the proposed workflow auditable.")
