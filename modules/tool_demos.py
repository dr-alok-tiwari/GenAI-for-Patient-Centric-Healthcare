from __future__ import annotations

import pandas as pd
import streamlit as st

from .common import badges, download_dataset, load_csv, load_json, record_to_text, section_header, set_visited
from .selection_engine import ALL, closest_alternative, records_matching, supported_options


def _pick(label: str, field: str, records: list[dict], selected: dict[str, str], key: str) -> None:
    options = supported_options(records, field, selected)
    choice = st.selectbox(label, [ALL, *options], key=key)
    if choice != ALL:
        selected[field] = choice


def render() -> None:
    set_visited("Tool demo lab")
    section_header(
        "Guided medical demonstration",
        "Tool-by-tool demo laboratory",
        "Every visible selection resolves to a linked synthetic dataset, complete prompt, four-step method, expected output, safety boundary, and verification checklist.",
        "▶️",
    )
    records: list[dict] = load_json("tool_demo_playbook.json")
    selected: dict[str, str] = {}
    f1, f2, f3, f4 = st.columns([1.25, 1, .9, .8])
    with f1:
        _pick("Pillar", "Pillars", records, selected, "demo_pillar")
    with f2:
        _pick("Role", "Roles", records, selected, "demo_role")
    with f3:
        _pick("Input", "Input types", records, selected, "demo_input")
    with f4:
        _pick("Risk", "Risk level", records, selected, "demo_risk")
    view = records_matching(records, selected)

    search = st.text_input("Search tool or application", placeholder="e.g., literature, multilingual, dashboard")
    if search.strip():
        direct = [
            row for row in view
            if search.lower() in " ".join(str(value) for value in row.values()).lower()
        ]
        if direct:
            view = direct
        else:
            alternative = closest_alternative(
                view, search, fields=("Tool", "Application area", "Demo objective", "Category")
            )
            view = [alternative] if alternative else records[:1]
            st.info(f"Closest verified demo: **{view[0]['Tool']}**.")

    labels = {
        f"{row['Icon']} {row['Tool']} — {row['Application area']}": row["Tool"]
        for row in view
    }
    label = st.selectbox("Complete tool demo", list(labels))
    demo = next(row for row in view if row["Tool"] == labels[label])
    badges(
        [
            f"💳 {demo['Access']}", f"📁 {demo['Dataset']}",
            f"⚠️ {demo['Risk level']} risk", f"📅 {demo['Verified on']}",
        ]
    )

    data = load_csv(str(demo["Dataset"]))
    id_col = data.columns[0]
    left, right = st.columns([0.78, 1.22], gap="large")
    with left:
        st.subheader("1. Select synthetic input")
        record_id = st.selectbox(
            "Record",
            data[id_col].astype(str).tolist(),
            key=f"demo_record_{demo['Tool']}",
        )
        row = data.loc[data[id_col].astype(str) == record_id].iloc[0]
        st.dataframe(row.rename("Value"), use_container_width=True)
        download_dataset(str(demo["Dataset"]), f"Download {demo['Dataset']}", key=f"demo_dl_{demo['Tool']}")
        st.link_button(f"Open {demo['Tool']} official site ↗", str(demo["Official URL"]), use_container_width=True)
    with right:
        tabs = st.tabs(["🪜 Steps", "📋 Prompt", "✅ Verify", "🎯 Human decision"])
        with tabs[0]:
            for index in range(1, 5):
                st.markdown(f"**Step {index}.** {demo[f'Step {index}']}")
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
            )
        with tabs[2]:
            checks = [item.strip() for item in str(demo["Verification checklist"]).split("|")]
            done = [
                st.checkbox(item, key=f"toolcheck_{demo['Tool']}_{index}")
                for index, item in enumerate(checks)
            ]
            st.progress(sum(done) / len(done), text=f"Verification: {sum(done)}/{len(done)}")
        with tabs[3]:
            st.info(demo["Expected output"])
            st.text_area(
                "Accept, edit, reject, or escalate—and why?",
                height=170,
                key=f"tool_reflect_{demo['Tool']}",
            )

    st.divider()
    section_header("Facilitator method", "Compare up to three supported tools", icon="⚖️")
    compare_tools = st.multiselect(
        "Tools",
        [row["Tool"] for row in records],
        max_selections=3,
    )
    if compare_tools:
        compare = pd.DataFrame(records)
        compare = compare.loc[
            compare["Tool"].isin(compare_tools),
            ["Tool", "Category", "Access", "Dataset", "Risk level", "Demo objective", "Official URL"],
        ]
        st.dataframe(
            compare,
            use_container_width=True,
            hide_index=True,
            column_config={"Official URL": st.column_config.LinkColumn("Official site", display_text="Open ↗")},
        )
    else:
        st.caption("Optional comparison. The guided single-tool demo above is always complete.")
