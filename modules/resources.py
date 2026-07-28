from __future__ import annotations

import streamlit as st

from .common import DATA, download_asset, load_csv, section_header, set_visited


def render() -> None:
    set_visited("Resources")
    section_header(
        "Take-home kit",
        "Updated workshop resources",
        "The supplied 10-page workshop PDF is now the presentation source. The supporting files below contain the expanded synthetic datasets and guided demonstration instructions used by the app.",
        "⬇️",
    )

    files = [
        (
            "Updated workshop kit",
            "GenAI_Healthcare_MDP_Updated_Kit.zip",
            "application/zip",
            "Supplied workshop PDF, 18 synthetic datasets, 29-tool demo matrix, playbook and quick-start guide",
            "📦",
        ),
        (
            "Supplied workshop PDF",
            "Practical-Tools-for-Doctors-and-Pharma-Professionals.pdf",
            "application/pdf",
            "The 10-page theory and laboratory presentation used inside the app",
            "🖥️",
        ),
        (
            "Live PowerPoint theory deck",
            "GenAI_Patient_Centric_Healthcare_Theory_Deck_Live_Presentation.pptx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "Presentation-ready PPTX rebuilt from the supplied workshop deck as full-slide images for zero text overlap and live slideshow use",
            "🎞️",
        ),
        (
            "Expanded synthetic datasets",
            "Synthetic_Healthcare_Pharma_Datasets_Expanded.zip",
            "application/zip",
            "Eighteen synthetic CSV datasets for patient, clinical, pharma, research, design and governance demos",
            "🧬",
        ),
        (
            "Tool demo matrix",
            "GenAI_Healthcare_Tool_Demo_Matrix_2026.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "Twenty-nine tools with use cases, linked datasets, four-step demos, prompts, verification and safety controls",
            "🧰",
        ),
        (
            "Tool demo playbook",
            "tool_demo_playbook.csv",
            "text/csv",
            "Machine-readable and facilitator-friendly instructions for every tool demo",
            "▶️",
        ),
        (
            "Workshop quick-start",
            "UPDATED_WORKSHOP_GUIDE.md",
            "text/markdown",
            "Delivery flow, six laboratory cases, demo protocol and local deployment notes",
            "🗺️",
        ),
    ]

    for i in range(0, len(files), 3):
        cols = st.columns(3)
        for col, item in zip(cols, files[i:i + 3]):
            title, filename, mime, desc, icon = item
            with col:
                st.markdown(
                    f"<div class='info-card'><div class='icon-title'><span class='icon-orb'>{icon}</span><div><h3 style='margin:.1rem 0'>{title}</h3></div></div><p>{desc}</p></div>",
                    unsafe_allow_html=True,
                )
                download_asset(f"Download {title}", filename, mime, f"res_{filename}")

    st.divider()
    section_header("Dataset catalogue", "All synthetic case datasets in the application", icon="📚")
    registry = []
    import json
    registry_data = json.loads((DATA / "dataset_registry.json").read_text(encoding="utf-8"))
    for filename, meta in registry_data.items():
        rows = len(load_csv(filename))
        registry.append(
            {
                "Icon": meta["icon"],
                "Dataset": filename,
                "Domain": meta["domain"],
                "Rows": rows,
                "Purpose": meta["description"],
            }
        )
    st.dataframe(registry, use_container_width=True, hide_index=True)

    st.divider()
    section_header("Official links", "Open the curated tool stack", icon="🔗")
    df = load_csv("tool_comparison_matrix.csv")
    st.dataframe(
        df[["Icon", "Tool", "Category", "Access", "Dataset", "Risk level", "Official URL"]],
        use_container_width=True,
        hide_index=True,
        column_config={"Official URL": st.column_config.LinkColumn("Official site", display_text="Open ↗")},
    )
    st.caption("Product access, pricing, country availability, account eligibility and data-processing terms may change. Confirm current details on each official website before delivery or real-world use.")
