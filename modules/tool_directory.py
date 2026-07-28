from __future__ import annotations

import pandas as pd
import streamlit as st

from .common import badges, download_dataset, load_csv, section_header, set_visited


def render() -> None:
    set_visited("Tool directory")
    section_header(
        "Curated landscape",
        "GenAI tool directory",
        "Browse 29 tools across patient communication, clinical work, pharma, research, analytics, design and governance. Every tool is linked to a synthetic dataset and a guided demo.",
        "🧰",
    )
    df = load_csv("tool_comparison_matrix.csv").copy()

    qcol, ccol, acol, rcol = st.columns([1.25, 1, .85, .7])
    with qcol:
        query = st.text_input("Search tools or use cases", placeholder="e.g., literature, patient education, workflow")
    with ccol:
        categories = st.multiselect("Categories", sorted(df["Category"].dropna().unique()))
    with acol:
        accesses = st.multiselect("Access", sorted(df["Access"].dropna().unique()))
    with rcol:
        risks = st.multiselect("Risk", sorted(df["Risk level"].dropna().unique()))

    mask = pd.Series(True, index=df.index)
    if query:
        searchable = df.astype(str).agg(" ".join, axis=1).str.lower()
        mask &= searchable.str.contains(query.lower(), regex=False)
    if categories:
        mask &= df["Category"].isin(categories)
    if accesses:
        mask &= df["Access"].isin(accesses)
    if risks:
        mask &= df["Risk level"].isin(risks)
    filtered = df.loc[mask].reset_index(drop=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Matching tools", len(filtered))
    c2.metric("Categories", filtered["Category"].nunique())
    c3.metric("Free/freemium", int(filtered["Access"].str.contains("Free", case=False, na=False).sum()))
    c4.metric("Linked datasets", filtered["Dataset"].nunique())

    show_cols = ["Icon", "Tool", "Category", "Access", "Application area", "Dataset", "Risk level", "Official URL"]
    st.dataframe(
        filtered[show_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Official URL": st.column_config.LinkColumn("Official site", display_text="Open ↗"),
            "Application area": st.column_config.TextColumn(width="large"),
            "Dataset": st.column_config.TextColumn(width="medium"),
        },
    )
    if filtered.empty:
        st.warning("No tool matches the selected filters.")
        return

    st.divider()
    section_header("Tool briefing", "Inspect one tool", icon="🔍")
    selected = st.selectbox("Select tool", filtered["Tool"].tolist())
    row = filtered.loc[filtered["Tool"] == selected].iloc[0]
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown(
            f"""
            <div class="tool-card">
              <div class="icon-title"><span class="icon-orb">{row['Icon']}</span><div>
              <div class="section-label">{row['Category']}</div><h2 style="margin:.05rem 0">{row['Tool']}</h2>
              <p>{row['Application area']}</p></div></div>
              <h4>Best workshop demo</h4><p>{row['Best demo use case']}</p>
              <h4>Linked synthetic dataset</h4><p><code>{row['Dataset']}</code></p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        badges([f"💳 {row['Access']}", f"⚠️ {row['Risk level']} risk", f"📅 Checked {row['Verified on']}"])
        st.link_button(f"Open {selected} official site ↗", row["Official URL"], use_container_width=True)
    with right:
        st.markdown(f"<div class='safety-banner'><b>Risk and privacy warning</b><br>{row['Risk / privacy warning']}</div>", unsafe_allow_html=True)
        download_dataset(row["Dataset"], f"Download {row['Dataset']}", key=f"tooldata_{selected}")
        favourite = selected in st.session_state.favourite_tools
        if st.button("Remove from demo shortlist" if favourite else "Add to demo shortlist", use_container_width=True):
            favs = set(st.session_state.favourite_tools)
            favs.discard(selected) if favourite else favs.add(selected)
            st.session_state.favourite_tools = favs
            st.rerun()
        st.info("Open **Tool demo lab** from the sidebar for a record selector, full prompt, four-step demonstration and verification checklist.")

    if st.session_state.favourite_tools:
        st.subheader("My demo shortlist")
        badges([f"⭐ {tool}" for tool in sorted(st.session_state.favourite_tools)], "free")
