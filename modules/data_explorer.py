from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from .common import badges, load_csv, load_json, section_header, set_visited


def render() -> None:
    set_visited("Data explorer")
    section_header(
        "Synthetic data",
        "Healthcare and pharma dataset explorer",
        "Inspect, filter, visualise and download every synthetic dataset used in the deck-aligned labs and tool demonstrations. These records are educational and are not clinical evidence.",
        "📊",
    )
    registry = load_json("dataset_registry.json")
    options = {f"{meta['icon']} {meta['name']}": filename for filename, meta in registry.items()}
    selected_label = st.selectbox("Dataset", list(options))
    filename = options[selected_label]
    meta = registry[filename]
    df = load_csv(filename).copy()

    st.markdown(
        f"<div class='info-card'><div class='icon-title'><span class='icon-orb'>{meta['icon']}</span><div><div class='section-label'>{meta['domain']}</div><h3 style='margin:.05rem 0'>{meta['name']}</h3><p>{meta['description']}</p></div></div></div>",
        unsafe_allow_html=True,
    )
    badges([f"📁 {filename}", "🧬 Fully synthetic", "🚫 Not clinical evidence"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Columns", len(df.columns))
    c3.metric("Missing cells", int(df.isna().sum().sum()))
    c4.metric("Duplicate rows", int(df.duplicated().sum()))

    search = st.text_input("Search all columns", placeholder="Enter a term")
    view = df
    if search:
        mask = df.astype(str).apply(lambda col: col.str.contains(search, case=False, regex=False)).any(axis=1)
        view = df.loc[mask]
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button("Download filtered CSV", view.to_csv(index=False).encode("utf-8"), file_name=filename, mime="text/csv", use_container_width=True)

    st.divider()
    section_header("Visual exploration", "Build a quick descriptive chart", icon="📈")
    categorical = [c for c in df.columns if df[c].dtype == "object" and 1 < df[c].nunique() <= 25]
    numeric = df.select_dtypes(include="number").columns.tolist()
    chart_options = []
    if categorical:
        chart_options.append("Category counts")
    if numeric:
        chart_options.append("Histogram")
    if len(numeric) >= 2:
        chart_options.append("Scatter")
    if not chart_options:
        chart_options.append("Column profile")
    chart_type = st.radio("Chart", chart_options, horizontal=True)
    if chart_type == "Category counts":
        col = st.selectbox("Category column", categorical)
        counts = df[col].fillna("Missing").value_counts().reset_index()
        counts.columns = [col, "Count"]
        fig = px.bar(counts, x=col, y="Count", text_auto=True, title=f"{col}: record count")
        fig.update_layout(height=460, margin=dict(l=25, r=25, t=60, b=80), xaxis_tickangle=-25)
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "Histogram":
        col = st.selectbox("Numeric column", numeric)
        fig = px.histogram(df, x=col, nbins=15, title=f"Distribution of {col}")
        fig.update_layout(height=460, margin=dict(l=25, r=25, t=60, b=50))
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "Scatter":
        x = st.selectbox("X axis", numeric, index=0)
        y = st.selectbox("Y axis", numeric, index=1)
        color = st.selectbox("Colour group", ["None"] + categorical)
        fig = px.scatter(df, x=x, y=y, color=None if color == "None" else color, hover_data=df.columns[:3], title=f"{y} versus {x}")
        fig.update_layout(height=460, margin=dict(l=25, r=25, t=60, b=50))
        st.plotly_chart(fig, use_container_width=True)
    else:
        profile = pd.DataFrame(
            {
                "Column": df.columns,
                "Type": [str(df[column].dtype) for column in df.columns],
                "Unique values": [int(df[column].nunique(dropna=True)) for column in df.columns],
                "Missing": [int(df[column].isna().sum()) for column in df.columns],
                "Example": [
                    str(df[column].dropna().iloc[0]) if not df[column].dropna().empty else "Missing"
                    for column in df.columns
                ],
            }
        )
        st.dataframe(profile, use_container_width=True, hide_index=True)
        st.caption("This complete profile is the supported visual response for datasets without chart-compatible columns.")

    st.caption("Charts are descriptive learning aids. Do not infer efficacy, safety or clinical associations from synthetic data.")
