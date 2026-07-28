from __future__ import annotations

import json
from html import escape

import streamlit as st
import streamlit.components.v1 as components

from .common import SLIDES, badges, download_asset, image_as_data_uri, section_header, set_visited

META_PATH = SLIDES / "slides_meta.json"


def _load_meta() -> list[dict]:
    return json.loads(META_PATH.read_text(encoding="utf-8"))


def _render_live_presenter(image_name: str, title: str, height: int = 720) -> None:
    """Render a zoomable, fullscreen-capable slide inside Streamlit."""
    uri = image_as_data_uri(SLIDES / image_name)
    safe_title = escape(title)
    components.html(
        f"""
        <style>
          :root {{ --navy:#073647; --teal:#0f766e; --line:#d8e7ef; }}
          * {{ box-sizing:border-box; }}
          body {{ margin:0; font-family:Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background:#f8fbff; }}
          .present-wrap {{ border:1px solid var(--line); border-radius:18px; overflow:hidden; background:#ffffff; box-shadow:0 10px 28px rgba(15,23,42,.08); }}
          .toolbar {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; justify-content:space-between; padding:10px 12px; background:linear-gradient(90deg,#073647,#0b4f60); color:white; }}
          .title {{ font-size:13px; font-weight:800; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:48%; }}
          .controls {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; justify-content:flex-end; }}
          button {{ border:1px solid rgba(255,255,255,.28); color:#fff; background:rgba(255,255,255,.12); border-radius:10px; padding:8px 11px; font-weight:800; cursor:pointer; }}
          button:hover {{ background:rgba(255,255,255,.22); }}
          .zoom {{ font-size:12px; font-weight:800; min-width:56px; text-align:center; }}
          .stage {{ height:{height}px; overflow:auto; background:linear-gradient(180deg,#eaf7ff,#f8fbff); padding:14px; }}
          .slide {{ width:100%; height:auto; display:block; margin:0 auto; border-radius:10px; box-shadow:0 10px 32px rgba(2,32,48,.20); background:white; }}
          .hint {{ color:#d7f9ff; font-size:12px; }}
          @media (max-width:760px) {{ .title {{ max-width:100%; }} .toolbar {{ align-items:flex-start; }} .controls {{ justify-content:flex-start; }} .stage {{ height:{max(440, height-180)}px; }} }}
        </style>
        <div id="wrap" class="present-wrap">
          <div class="toolbar">
            <div class="title">{safe_title}</div>
            <div class="controls">
              <span class="hint">Use +/− or full screen for live teaching</span>
              <button onclick="zoomOut()">− Zoom</button>
              <button onclick="resetZoom()">100%</button>
              <button onclick="zoomIn()">+ Zoom</button>
              <button onclick="toggleFit()">Fit width</button>
              <button onclick="goFull()">⛶ Present full screen</button>
              <span id="zoomLabel" class="zoom">100%</span>
            </div>
          </div>
          <div id="stage" class="stage">
            <img id="slide" class="slide" src="{uri}" alt="{safe_title}">
          </div>
        </div>
        <script>
          let zoom = 1.0;
          const img = document.getElementById('slide');
          const label = document.getElementById('zoomLabel');
          function applyZoom() {{
            img.style.width = (zoom * 100) + '%';
            label.textContent = Math.round(zoom * 100) + '%';
          }}
          function zoomIn() {{ zoom = Math.min(3.0, zoom + 0.15); applyZoom(); }}
          function zoomOut() {{ zoom = Math.max(0.45, zoom - 0.15); applyZoom(); }}
          function resetZoom() {{ zoom = 1.0; applyZoom(); }}
          function toggleFit() {{ zoom = 1.0; applyZoom(); document.getElementById('stage').scrollTo({{top:0,left:0,behavior:'smooth'}}); }}
          function goFull() {{
            const el = document.getElementById('wrap');
            if (el.requestFullscreen) {{ el.requestFullscreen(); }}
            else if (el.webkitRequestFullscreen) {{ el.webkitRequestFullscreen(); }}
          }}
          document.addEventListener('keydown', function(e) {{
            if (e.key === '+' || e.key === '=') zoomIn();
            if (e.key === '-' || e.key === '_') zoomOut();
            if (e.key === '0') resetZoom();
          }});
          applyZoom();
        </script>
        """,
        height=height + 70,
        scrolling=False,
    )


def render() -> None:
    set_visited("Theory deck")
    section_header(
        "60-minute theory",
        "Interactive deck navigator",
        "The original app deck has been replaced with the supplied 10-page workshop presentation. Pages are rendered as images so text remains fixed, readable and free from browser-layout overlap.",
        "🖥️",
    )
    meta = _load_meta()
    total = len(meta)
    chapters = list(dict.fromkeys(item["chapter"] for item in meta))

    current_num = int(st.session_state.get("theory_slide_num", 1))
    current_num = min(max(current_num, 1), total)
    current_meta = next(m for m in meta if m["number"] == current_num)

    c1, c2, c3 = st.columns([1.1, 1.8, .75])
    with c1:
        chapter = st.selectbox("Chapter", chapters, index=chapters.index(current_meta["chapter"]))
    chapter_pages = [m for m in meta if m["chapter"] == chapter]
    labels = [f'{m["number"]}. {m["title"]}' for m in chapter_pages]
    selected_default = next((x for x in labels if x.startswith(f"{current_num}.")), labels[0])
    with c2:
        selected = st.selectbox("Page", labels, index=labels.index(selected_default))
    selected_num = int(selected.split(".", 1)[0])
    if selected_num != current_num:
        st.session_state.theory_slide_num = selected_num
        st.rerun()
    with c3:
        st.metric("Page", f"{selected_num}/{total}")

    current = next(m for m in meta if m["number"] == selected_num)
    left, right = st.columns([1.45, .55], gap="large")
    with left:
        st.caption("Live presentation mode: zoom in/out inside the slide, or click full screen to teach directly from the app. For a true PowerPoint slideshow, download the PPTX below and open it in PowerPoint/Keynote/Google Slides.")
        presenter_height = st.slider("Presentation viewport height", 520, 1000, 720, 20, help="Increase this when projecting on a large display.")
        _render_live_presenter(current["image"], f'Page {selected_num}: {current["title"]}', presenter_height)
        nav1, nav2, nav3, nav4 = st.columns([1, 1, 1.25, 1.25])
        with nav1:
            if st.button("← Previous", disabled=selected_num == 1, use_container_width=True):
                st.session_state.theory_slide_num = selected_num - 1
                st.rerun()
        with nav2:
            if st.button("Next →", disabled=selected_num == total, use_container_width=True):
                st.session_state.theory_slide_num = selected_num + 1
                st.rerun()
        with nav3:
            download_asset("Download live PPTX", "GenAI_Patient_Centric_Healthcare_Theory_Deck_Live_Presentation.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", "theory_pptx")
        with nav4:
            download_asset("Download PDF", "Practical-Tools-for-Doctors-and-Pharma-Professionals.pdf", "application/pdf", "theory_pdf")
    with right:
        st.markdown(
            f"<div class='info-card'><div class='section-label'>{current['chapter']}</div><h3>{current['title']}</h3><p>{current['summary']}</p></div>",
            unsafe_allow_html=True,
        )
        badges(current.get("badges", []))
        related = current.get("related_labs", [])
        if related:
            badges([f"🧪 Related lab {x}" for x in related], "free")
        st.subheader("Facilitation cue")
        st.write(current["cue"])
        if st.session_state.facilitator_mode:
            with st.expander("Presenter notes", expanded=True):
                st.write(current["notes"])
        else:
            st.info("Enable facilitator mode in the sidebar to reveal presenter notes.")

    st.divider()
    section_header("Deck map", "Theory at a glance")
    cols = st.columns(3)
    for idx, chapter_name in enumerate(chapters):
        pages = [m for m in meta if m["chapter"] == chapter_name]
        with cols[idx % 3]:
            st.markdown(
                f"<div class='info-card'><h3>{chapter_name}</h3><p>Pages {pages[0]['number']}–{pages[-1]['number']}</p><span class='tiny'>{len(pages)} page(s)</span></div>",
                unsafe_allow_html=True,
            )
