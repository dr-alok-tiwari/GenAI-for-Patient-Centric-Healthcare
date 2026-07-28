from __future__ import annotations

import json

import streamlit as st

from .common import DATA, download_asset, load_csv, section_header, set_visited


def render() -> None:
    set_visited("Resources")
    section_header(
        "Take-home kit",
        "Alkem AI Masterclass resources",
        "Editable presentation, matching PDF, participant and facilitator guides, verified tool/workflow matrix, synthetic datasets, attribution, and implementation reports.",
        "⬇️",
    )
    files = [
        (
            "Editable masterclass deck",
            "Alkem_AI_Masterclass_Healthcare.pptx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "Twelve editable 16:9 slides with four pillars, medical demos, speaker notes, and sources",
            "🖥️",
        ),
        (
            "Masterclass deck PDF",
            "Alkem_AI_Masterclass_Healthcare.pdf",
            "application/pdf",
            "Presentation-ready PDF matching the refreshed editable deck",
            "📄",
        ),
        (
            "Participant workbook",
            "Alkem_AI_Masterclass_Participant_Workbook.pdf",
            "application/pdf",
            "Twelve-page lab workbook with prompt canvas, verification, comparison, and pilot plan",
            "📝",
        ),
        (
            "Facilitator handbook",
            "Alkem_AI_Masterclass_Facilitator_Handbook.pdf",
            "application/pdf",
            "Thirteen-page delivery guide with demo boundaries, fallbacks, answer key, and sources",
            "🎛️",
        ),
        (
            "Healthcare tool matrix",
            "Alkem_AI_Masterclass_Healthcare_Tool_Matrix.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "Seven-sheet workbook: tool matrix, workflows, dropdown coverage, labs, pilot, and sources",
            "🧰",
        ),
        (
            "Synthetic dataset pack",
            "Synthetic_Healthcare_Pharma_Datasets_Expanded.zip",
            "application/zip",
            "Twenty synthetic datasets, including prescription and imaging cases",
            "🧬",
        ),
        (
            "Complete workshop kit",
            "Alkem_AI_Masterclass_Healthcare_Kit.zip",
            "application/zip",
            "Decks, workbooks, matrix, datasets, guides, reports, and attribution in one bundle",
            "📦",
        ),
        (
            "Dropdown coverage report",
            "Dropdown_Coverage_Report.pdf",
            "application/pdf",
            "Evidence that every visible selector option resolves to a complete workflow",
            "✅",
        ),
    ]
    for index in range(0, len(files), 4):
        cols = st.columns(4)
        for col, item in zip(cols, files[index:index + 4]):
            title, filename, mime, description, icon = item
            with col:
                st.markdown(
                    f"<div class='info-card'><div class='icon-title'><span class='icon-orb'>{icon}</span>"
                    f"<div><h3 style='margin:.1rem 0'>{title}</h3></div></div><p>{description}</p></div>",
                    unsafe_allow_html=True,
                )
                download_asset(f"Download {title}", filename, mime, f"res_{filename}")

    st.divider()
    section_header("Dataset catalogue", "All synthetic case datasets", icon="📚")
    registry_data = json.loads((DATA / "dataset_registry.json").read_text(encoding="utf-8"))
    registry = [
        {
            "Icon": meta["icon"],
            "Dataset": filename,
            "Domain": meta["domain"],
            "Rows": len(load_csv(filename)),
            "Purpose": meta["description"],
        }
        for filename, meta in registry_data.items()
    ]
    st.dataframe(registry, use_container_width=True, hide_index=True)

    st.divider()
    section_header("Official links", "Verified tool source register", icon="🔗")
    tools = load_csv("tool_comparison_matrix.csv")
    st.dataframe(
        tools[
            [
                "Icon", "Tool", "Category", "Access", "Dataset", "Risk level",
                "Verified on", "Official URL",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Official URL": st.column_config.LinkColumn("Official site", display_text="Open ↗")
        },
    )
    st.caption(
        "Product access, pricing, country availability, account eligibility, capabilities, and terms may "
        "change. Confirm current details on each official website before delivery or real-world use."
    )
