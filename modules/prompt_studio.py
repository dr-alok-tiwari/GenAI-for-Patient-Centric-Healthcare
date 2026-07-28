from __future__ import annotations

import streamlit as st

from .common import badges, load_csv, load_json, record_to_text, section_header, set_visited
from .selection_engine import ALL, closest_alternative, records_matching, supported_options


def _selector(
    label: str,
    field: str,
    catalog: list[dict],
    selections: dict[str, str],
    key: str,
) -> str:
    options = supported_options(catalog, field, selections)
    choice = st.selectbox(label, [ALL, *options], key=key)
    if choice != ALL:
        selections[field] = choice
    return choice


def render() -> None:
    set_visited("Prompt studio")
    section_header(
        "Guaranteed workflow coverage",
        "Healthcare prompt studio",
        "Choose any visible pillar, role, task, input, and language. Options cascade from the verified workflow catalogue, so every selectable combination has a prompt, tool route, dataset, output, verification checklist, and accountable reviewer.",
        "✨",
    )
    catalog: list[dict] = load_json("workflow_catalog.json")

    search = st.text_input(
        "Describe another need",
        placeholder="e.g., explain a medicine image, review an adverse event, design a safe pilot",
        help="If the wording does not exactly match a workflow, the app returns the closest verified alternative.",
    )
    if search.strip():
        match = closest_alternative(catalog, search)
        if match:
            st.info(
                f"Closest verified workflow: **{match['icon']} {match['title']}**. "
                "The structured selectors below remain available if you want to narrow the route."
            )

    selections: dict[str, str] = {}
    s1, s2, s3, s4, s5 = st.columns([1.25, 1, 1.2, 1, .85])
    with s1:
        _selector("Pillar", "pillar", catalog, selections, "studio_pillar")
    with s2:
        _selector("Role", "roles", catalog, selections, "studio_role")
    with s3:
        _selector("Task", "task", catalog, selections, "studio_task")
    with s4:
        _selector("Input", "input_type", catalog, selections, "studio_input")
    with s5:
        _selector("Language", "languages", catalog, selections, "studio_language")

    matches = records_matching(catalog, selections)
    st.caption(f"{len(matches)} complete workflow(s) support the current selection.")
    workflow_labels = {
        f"{item['icon']} {item['title']} — {item['primary_tool']}": item["workflow_id"]
        for item in matches
    }
    workflow_label = st.selectbox("Complete workflow", list(workflow_labels), key="studio_workflow")
    item = next(row for row in matches if row["workflow_id"] == workflow_labels[workflow_label])

    df = load_csv(item["dataset"])
    id_col = df.columns[0]
    record_id = st.selectbox("Synthetic case", df[id_col].astype(str).tolist(), key="studio_record")
    row = df.loc[df[id_col].astype(str) == record_id].iloc[0]
    language = selections.get("languages", item["languages"][0])
    prompt = (
        item["prompt_template"]
        .replace("{reviewer}", item["human_reviewer"])
        .replace("{record}", record_to_text(row))
    )
    if language != "English":
        prompt += (
            f"\n\nLANGUAGE\nDraft the audience-facing portion in {language} and include an aligned English "
            "version. Keep medicine, product, and test names stable. Require fluent clinical review."
        )

    left, right = st.columns([0.82, 1.18], gap="large")
    with left:
        st.markdown(
            f"""
            <div class="info-card">
              <div class="section-label">{item['pillar']}</div>
              <h3>{item['icon']} {item['title']}</h3>
              <p>{item['case_context']}</p>
              <p><b>Expected output:</b> {item['expected_output']}</p>
              <p><b>Qualified reviewer:</b> {item['human_reviewer']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        badges(
            [
                f"⚠️ {item['risk_level']} risk",
                f"📁 {item['dataset']}",
                f"⏱️ {item['time_minutes']} min",
                f"📅 Verified {item['last_verified']}",
            ]
        )
        st.dataframe(row.rename("Synthetic value"), use_container_width=True)
        st.warning(item["prohibited_actions"])
    with right:
        tabs = st.tabs(["📋 Prompt", "🧰 Tool route", "✅ Verify"])
        with tabs[0]:
            st.code(prompt, language="text", wrap_lines=True)
            st.download_button(
                "Download complete prompt",
                prompt.encode("utf-8"),
                file_name=f"{item['workflow_id'].lower()}_prompt.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with tabs[1]:
            st.subheader(f"Primary: {item['primary_tool']}")
            badges([f"Alternative: {tool}" for tool in item["alternative_tools"]], "free")
            st.write(
                "Choose an organisation-approved tool whose data handling, account type, regional access, "
                "and capability fit the workflow. Tool popularity is not a safety control."
            )
        with tabs[2]:
            for index, check in enumerate(item["verification"], 1):
                st.checkbox(check, key=f"studio_verify_{item['workflow_id']}_{index}")
            st.info(
                "The visible selectors are data-driven. If a role, language, or input is shown, at least one "
                "complete workflow supports it; unsupported combinations are never offered."
            )
