from __future__ import annotations

import pandas as pd
import streamlit as st

from .common import badges, download_dataset, load_csv, load_json, record_to_text, section_header, set_visited


def _risk_tone(risk: str) -> str:
    return "high" if risk.lower() == "high" else "medium" if risk.lower() == "medium" else "free"


def render() -> None:
    set_visited("Tool demo lab")
    section_header(
        "Guided demonstration",
        "Tool-by-tool demo laboratory",
        "Choose any listed tool and the app will supply a relevant synthetic dataset, a demo-ready record, step-by-step instructions, a safe prompt and a verification checklist.",
        "▶️",
    )
    playbook = load_json("tool_demo_playbook.json")
    df = pd.DataFrame(playbook)

    f1, f2, f3 = st.columns([1.3, 1, 1])
    with f1:
        search = st.text_input("Search tool, category or application", placeholder="e.g., literature, multilingual, dashboard")
    with f2:
        category = st.selectbox("Category", ["All"] + sorted(df["Category"].unique().tolist()))
    with f3:
        risk = st.selectbox("Risk level", ["All"] + sorted(df["Risk level"].unique().tolist()))

    view = df.copy()
    if search:
        mask = view.astype(str).agg(" ".join, axis=1).str.contains(search, case=False, regex=False)
        view = view.loc[mask]
    if category != "All":
        view = view.loc[view["Category"] == category]
    if risk != "All":
        view = view.loc[view["Risk level"] == risk]
    if view.empty:
        st.warning("No demo matches the selected filters.")
        return

    labels = [f"{row['Icon']} {row['Tool']} — {row['Application area']}" for _, row in view.iterrows()]
    selected_label = st.selectbox("Select a tool demo", labels)
    selected_name = selected_label.split(" — ", 1)[0].split(" ", 1)[1]
    demo = view.loc[view["Tool"] == selected_name].iloc[0]

    st.markdown(
        f"""
        <div class="demo-card">
          <div class="icon-title"><span class="icon-orb">{demo['Icon']}</span><div>
          <div class="section-label">{demo['Category']}</div><h2 style="margin:.05rem 0">{demo['Tool']}</h2>
          <p>{demo['Application area']}</p></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    badges([f"💳 {demo['Access']}", f"📁 {demo['Dataset']}", f"⚠️ {demo['Risk level']} risk"], _risk_tone(str(demo["Risk level"])))

    dataset = str(demo["Dataset"])
    data = load_csv(dataset)
    id_col = data.columns[0]
    left, right = st.columns([.78, 1.22], gap="large")
    with left:
        st.subheader("1. Select synthetic input")
        record_id = st.selectbox("Record", data[id_col].astype(str).tolist(), key=f"demo_record_{demo['Tool']}")
        row = data.loc[data[id_col].astype(str) == record_id].iloc[0]
        st.dataframe(row.rename("Value"), use_container_width=True)
        download_dataset(dataset, f"Download full dataset: {dataset}", key=f"demo_dl_{demo['Tool']}")
        st.link_button(f"Open {demo['Tool']} official site ↗", str(demo["Official URL"]), use_container_width=True)

    with right:
        tabs = st.tabs(["🪜 Steps", "📋 Prompt", "✅ Verify", "🎯 Expected output"])
        with tabs[0]:
            for i in range(1, 5):
                st.markdown(f"**Step {i}**")
                st.write(demo[f"Step {i}"])
            st.warning(demo["Safety note"])
        with tabs[1]:
            full_prompt = f"{demo['Prompt template']}\n\nSYNTHETIC RECORD\n{record_to_text(row)}"
            st.code(full_prompt, language="text", wrap_lines=True)
            st.download_button(
                "Download demo prompt",
                full_prompt.encode("utf-8"),
                file_name=f"{demo['Tool'].lower().replace(' ', '_')}_demo_prompt.txt",
                mime="text/plain",
                use_container_width=True,
                key=f"prompt_dl_{demo['Tool']}",
            )
        with tabs[2]:
            checks = [x.strip() for x in str(demo["Verification checklist"]).split("|")]
            checked = [st.checkbox(item, key=f"toolcheck_{demo['Tool']}_{i}") for i, item in enumerate(checks)]
            st.progress(sum(checked) / len(checked), text=f"Verification completed: {sum(checked)}/{len(checked)}")
            st.caption("An output is not workshop-ready until the relevant checks are complete and a qualified person records the final decision.")
        with tabs[3]:
            st.info(demo["Expected output"])
            reflection = st.text_area(
                "What would you accept, edit, reject or escalate?",
                height=170,
                key=f"tool_reflect_{demo['Tool']}",
                placeholder="Record the human decision, evidence checked and any limitation...",
            )
            if reflection:
                st.download_button(
                    "Download reflection",
                    reflection.encode("utf-8"),
                    file_name=f"{demo['Tool'].lower().replace(' ', '_')}_reflection.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key=f"ref_dl_{demo['Tool']}",
                )

    st.divider()
    section_header("Facilitator method", "Run a three-tool comparison", icon="⚖️")
    st.write("Assign the same synthetic record to three teams using different tools. Compare factual fidelity, missing-data handling, evidence traceability, usability, privacy fit and the amount of human correction required. Do not rank tools only by fluency.")
    compare_tools = st.multiselect("Select up to three tools", df["Tool"].tolist(), max_selections=3)
    if compare_tools:
        compare = df.loc[df["Tool"].isin(compare_tools), ["Tool", "Category", "Access", "Dataset", "Risk level", "Demo objective", "Safety note", "Official URL"]]
        st.dataframe(compare, use_container_width=True, hide_index=True, column_config={"Official URL": st.column_config.LinkColumn("Official site", display_text="Open ↗")})
