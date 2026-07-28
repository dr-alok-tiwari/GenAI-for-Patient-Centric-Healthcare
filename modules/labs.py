from __future__ import annotations

import pandas as pd
import streamlit as st

from .common import ASSETS, badges, download_dataset, load_csv, load_json, record_to_text, section_header, set_visited
from .content import LABS


def _tool_demo(tool: str) -> dict | None:
    for item in load_json("tool_demo_playbook.json"):
        if item["Tool"] == tool:
            return item
    return None


def render() -> None:
    set_visited("Hands-on labs")
    section_header(
        "90-minute lab",
        "Six case-based hands-on exercises",
        "Six 15-minute exercises prioritise medical-specific practice: prescription, image observation, discharge and language, clinical reasoning, pharmacovigilance, and evidence verification.",
        "🧪",
    )

    completed = len(st.session_state.completed_labs)
    st.progress(completed / len(LABS), text=f"Workshop progress: {completed}/{len(LABS)} labs")
    labels = [f"{lab['icon']} {idx + 1}. {lab['title']} — {lab['duration']} min" for idx, lab in enumerate(LABS)]
    selected_label = st.selectbox("Select exercise", labels)
    lab_index = labels.index(selected_label)
    lab = LABS[lab_index]

    st.markdown(
        f"""
        <div class="lab-card">
          <div class="icon-title"><span class="icon-orb">{lab['icon']}</span><div>
          <div class="section-label">Lab {lab_index + 1} • Page {lab['deck_page']} • {lab['duration']} minutes</div>
          <h2 style="margin:.05rem 0">{lab['title']}</h2><p>{lab['goal']}</p></div></div>
          <p><b>Case:</b> {lab['case_brief']}</p><p><b>Deliverable:</b> {lab['deliverable']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    badges(["🧬 Synthetic data", "🧑‍⚕️ Human review", "⏱️ 3-6-4-2 workflow", f"📄 Deck page {lab['deck_page']}"])

    df = load_csv(lab["dataset"])
    setup, task = st.columns([.78, 1.22], gap="large")
    with setup:
        st.subheader("A. Select the case")
        record_id = st.selectbox("Synthetic record", df[lab["id_col"]].astype(str).tolist(), key=f"record_{lab['id']}")
        row = df.loc[df[lab["id_col"]].astype(str) == record_id].iloc[0]
        if "image_file" in row and str(row["image_file"]):
            st.image(
                ASSETS / "medical" / str(row["image_file"]),
                caption="Fully synthetic training asset",
                use_container_width=True,
            )
        st.dataframe(row.rename("Value"), use_container_width=True)
        download_dataset(lab["dataset"], f"Download {lab['dataset']}", key=f"labdata_{lab['id']}")

        if lab.get("support_dataset"):
            support = load_csv(lab["support_dataset"])
            with st.expander(f"Supporting synthetic file: {lab['support_dataset']}"):
                st.dataframe(support.head(8), use_container_width=True, hide_index=True)
                download_dataset(lab["support_dataset"], f"Download {lab['support_dataset']}", key=f"labsupport_{lab['id']}")

        st.subheader("B. Choose a demo tool")
        selected_tool = st.selectbox("Tool", lab["tool_options"], key=f"tool_{lab['id']}")
        demo = _tool_demo(selected_tool)
        if demo:
            st.link_button(f"Open {selected_tool} official site ↗", demo["Official URL"], use_container_width=True)
            badges([f"💳 {demo['Access']}", f"⚠️ {demo['Risk level']} risk"])
            with st.expander("Tool-specific demo instructions", expanded=True):
                st.write(demo["Demo objective"])
                for i in range(1, 5):
                    st.markdown(f"**{i}. {demo[f'Step {i}']}**")
                st.warning(demo["Safety note"])
        if lab.get("language_selector"):
            language = st.selectbox(
                "Target language",
                ["Hindi", "Marathi", "Bengali", "Tamil", "Telugu", "Kannada", "Malayalam"],
                key=f"{lab['id']}_language",
            )
        else:
            language = "Hindi"

    prompt = lab["prompt"].format(record=record_to_text(row), language=language)
    with task:
        tabs = st.tabs(["1️⃣ Run", "2️⃣ Verify", "3️⃣ Debrief", "4️⃣ Record decision"])
        with tabs[0]:
            st.markdown("**Timebox: 3 min orient + 6 min run**")
            st.code(prompt, language="text", wrap_lines=True)
            st.download_button(
                "Download this lab prompt",
                prompt.encode("utf-8"),
                file_name=f"{lab['id']}_{selected_tool.lower().replace(' ', '_')}_prompt.txt",
                mime="text/plain",
                key=f"download_{lab['id']}_{selected_tool}",
                use_container_width=True,
            )
            if lab["id"] in {"lab5", "lab6"}:
                st.info("For a batch-analysis tool, upload the full CSV. For a chat-only demo, start with the selected row and then compare with a small sample.")
        with tabs[1]:
            st.markdown("**Timebox: 4 min verify**")
            checks = [st.checkbox(item, key=f"{lab['id']}_{selected_tool}_{idx}") for idx, item in enumerate(lab["review"])]
            st.progress(sum(checks) / len(checks), text=f"Review checks passed: {sum(checks)}/{len(checks)}")
            if demo:
                st.caption(demo["Verification checklist"])
        with tabs[2]:
            st.markdown("**Use the case, not just the prose quality, to judge the tool.**")
            for i, question in enumerate(lab["debrief"], 1):
                st.markdown(f"**{i}. {question}**")
            comparison = st.text_area("Comparison notes", height=150, key=f"debrief_{lab['id']}_{selected_tool}", placeholder="What was accurate, unsafe, missing or difficult to verify?")
        with tabs[3]:
            st.markdown("**Timebox: 2 min record the human decision**")
            decision = st.text_area(
                "What would you accept, edit, reject or escalate?",
                key=f"reflection_{lab['id']}_{selected_tool}",
                height=180,
                placeholder="State the professional decision, evidence checked, edits made and escalation route...",
            )
            if decision:
                package = f"LAB: {lab['title']}\nTOOL: {selected_tool}\nRECORD: {record_id}\n\nDECISION\n{decision}\n\nDEBRIEF\n{comparison if 'comparison' in locals() else ''}"
                st.download_button("Download lab decision record", package.encode("utf-8"), file_name=f"{lab['id']}_decision_record.txt", mime="text/plain", use_container_width=True)

    done = lab["id"] in st.session_state.completed_labs
    if st.button("Mark lab incomplete" if done else "Mark lab complete", type="primary", use_container_width=True):
        completed_labs = set(st.session_state.completed_labs)
        completed_labs.discard(lab["id"]) if done else completed_labs.add(lab["id"])
        st.session_state.completed_labs = completed_labs
        st.rerun()

    if len(st.session_state.completed_labs) == len(LABS):
        st.balloons()
        st.success("All six deck-aligned labs are complete. Continue to Assessment and the 30-day pilot plan.")
