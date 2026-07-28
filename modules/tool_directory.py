from __future__ import annotations

import pandas as pd
import streamlit as st

from .common import badges, download_dataset, load_csv, section_header, set_visited
from .selection_engine import ALL, closest_alternative, records_matching, supported_options


def _pick(label: str, field: str, records: list[dict], selected: dict[str, str], key: str) -> None:
    options = supported_options(records, field, selected)
    choice = st.selectbox(label, [ALL, *options], key=key)
    if choice != ALL:
        selected[field] = choice


def render() -> None:
    set_visited("Tool directory")
    section_header(
        "Medical workflow fit",
        "Verified GenAI tool directory",
        "Filter by pillar, professional role, input, risk, and access. Choices cascade from supported records; an unmatched search returns the closest verified alternative rather than an empty page.",
        "🧰",
    )
    df = load_csv("tool_comparison_matrix.csv").fillna("")
    records = df.to_dict("records")
    selected: dict[str, str] = {}
    f1, f2, f3, f4, f5 = st.columns([1.25, 1, 1, .75, .9])
    with f1:
        _pick("Pillar", "Pillars", records, selected, "directory_pillar")
    with f2:
        _pick("Professional role", "Roles", records, selected, "directory_role")
    with f3:
        _pick("Input modality", "Input modalities", records, selected, "directory_input")
    with f4:
        _pick("Risk", "Risk level", records, selected, "directory_risk")
    with f5:
        _pick("Access", "Access", records, selected, "directory_access")
    filtered_records = records_matching(records, selected)

    query = st.text_input(
        "Search tool or medical use case",
        placeholder="e.g., prescription, radiograph, pharmacovigilance, evidence",
    )
    if query.strip():
        direct = [
            row for row in filtered_records
            if query.lower() in " ".join(str(value) for value in row.values()).lower()
        ]
        if direct:
            filtered_records = direct
        else:
            alternative = closest_alternative(
                filtered_records,
                query,
                fields=("Tool", "Application area", "Best demo use case", "Pillars", "Roles"),
            )
            filtered_records = [alternative] if alternative else records[:1]
            st.info(
                f"No exact catalogue wording matched. Showing the closest verified alternative: "
                f"**{filtered_records[0]['Tool']}**."
            )

    filtered = pd.DataFrame(filtered_records)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Supported tools", len(filtered))
    c2.metric("Covered pillars", len({item for value in filtered["Pillars"] for item in str(value).split(";") if item}))
    c3.metric("Linked datasets", filtered["Dataset"].nunique())
    c4.metric("Latest verification", filtered["Verified on"].max())

    show_cols = [
        "Icon", "Tool", "Category", "Access", "Application area", "Input modalities",
        "Dataset", "Risk level", "Official URL",
    ]
    st.dataframe(
        filtered[show_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Official URL": st.column_config.LinkColumn("Official site", display_text="Open ↗"),
            "Application area": st.column_config.TextColumn(width="large"),
        },
    )

    selected_tool = st.selectbox("Inspect a supported tool", filtered["Tool"].tolist())
    row = filtered.loc[filtered["Tool"] == selected_tool].iloc[0]
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown(
            f"""
            <div class="tool-card">
              <div class="section-label">{row['Category']}</div>
              <h2>{row['Icon']} {row['Tool']}</h2>
              <p>{row['Application area']}</p>
              <p><b>Best workshop demo:</b> {row['Best demo use case']}</p>
              <p><b>Human reviewer:</b> {row['Human reviewer']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        badges([f"💳 {row['Access']}", f"⚠️ {row['Risk level']} risk", f"📅 {row['Verified on']}"])
        st.link_button(f"Open {selected_tool} official site ↗", row["Official URL"], use_container_width=True)
    with right:
        st.markdown(
            f"<div class='safety-banner'><b>Risk and privacy boundary</b><br>{row['Risk / privacy warning']}</div>",
            unsafe_allow_html=True,
        )
        st.write(f"**Evidence capability:** {row['Evidence capability']}")
        st.write(f"**Pricing/access note:** {row['Approx INR cost']}; {row['Login requirement']}.")
        download_dataset(row["Dataset"], f"Download {row['Dataset']}", key=f"tooldata_{selected_tool}")
        favourite = selected_tool in st.session_state.favourite_tools
        if st.button(
            "Remove from demo shortlist" if favourite else "Add to demo shortlist",
            use_container_width=True,
        ):
            favs = set(st.session_state.favourite_tools)
            favs.discard(selected_tool) if favourite else favs.add(selected_tool)
            st.session_state.favourite_tools = favs
            st.rerun()
    if st.session_state.favourite_tools:
        st.subheader("My verified demo shortlist")
        badges([f"⭐ {tool}" for tool in sorted(st.session_state.favourite_tools)], "free")
