from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from .brand import BRAND

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DATA = ROOT / "data"
DOWNLOADS = ASSETS / "downloads"
SLIDES = ASSETS / "slides"

APP_TITLE = BRAND["title"]
APP_SUBTITLE = BRAND["subtitle"]


def configure_page() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="⚕️",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={"About": "Alkem AI Masterclass: a local-first, synthetic-data learning studio for healthcare and pharma professionals."},
    )
    inject_css()
    initialize_state()


def initialize_state() -> None:
    defaults: dict[str, Any] = {
        "completed_labs": set(),
        "favourite_tools": set(),
        "visited_pages": set(),
        "quiz_submitted": False,
        "quiz_score": 0,
        "facilitator_mode": False,
        "participant_name": "",
        "theory_slide_num": 1,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
          --navy:#073647; --navy2:#0b4f60; --teal:#0f766e; --cyan:#0891b2;
          --sky:#e8f6ff; --mint:#ecfdf5; --ink:#0f172a; --muted:#475569;
          --line:#d8e7ef; --card:#ffffff; --amber:#b45309; --red:#b91c1c;
        }
        html, body, [class*="css"] { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
        .stApp { background:linear-gradient(180deg,#f8fbff 0%,#f6fffd 100%); }
        [data-testid="stSidebar"] { background:linear-gradient(180deg,#062f3e 0%,#0a5260 100%); }
        [data-testid="stSidebar"] * { color:#f8fafc; }
        [data-testid="stSidebar"] .stRadio label { padding:.31rem .42rem; border-radius:.65rem; }
        [data-testid="stSidebar"] .stRadio label:hover { background:rgba(255,255,255,.10); }
        .block-container { padding-top:1.1rem; padding-bottom:3rem; max-width:1520px; }
        h1,h2,h3,h4 { color:var(--navy); letter-spacing:-.018em; overflow-wrap:anywhere; }
        p, li, div { overflow-wrap:anywhere; }
        .hero { position:relative; overflow:hidden; border-radius:24px; min-height:330px; background-size:cover; background-position:center; box-shadow:0 20px 55px rgba(8,51,68,.16); margin-bottom:1.2rem; }
        .hero-overlay { position:absolute; inset:0; background:linear-gradient(90deg,rgba(3,37,48,.95) 0%,rgba(3,37,48,.76) 49%,rgba(3,37,48,.12) 100%); }
        .hero-content { position:relative; z-index:2; padding:52px; max-width:790px; color:white; }
        .hero-kicker { text-transform:uppercase; font-size:.76rem; letter-spacing:.16em; font-weight:850; color:#67e8f9; }
        .brand-lockup { display:inline-flex; align-items:center; padding:.35rem .7rem; border:1px solid rgba(255,255,255,.3); border-radius:999px; font-size:.72rem; font-weight:900; letter-spacing:.12em; }
        .hero h1 { color:white; font-size:clamp(2.25rem,4vw,3.25rem); line-height:1.03; margin:.52rem 0 .9rem; }
        .hero p { color:#e6f7fb; font-size:1.07rem; line-height:1.58; }
        .badge-row { display:flex; flex-wrap:wrap; gap:.42rem; align-items:center; margin:.45rem 0; }
        .badge { display:inline-flex; align-items:center; gap:.32rem; max-width:100%; padding:.34rem .66rem; border-radius:999px; border:1px solid #c8ddea; background:#eef8fc; color:#075985; font-size:.76rem; font-weight:800; line-height:1.2; white-space:normal; }
        .badge.free { background:#ecfdf5; color:#065f46; border-color:#a7f3d0; }
        .badge.medium { background:#fffbeb; color:#92400e; border-color:#fde68a; }
        .badge.high { background:#fff1f2; color:#9f1239; border-color:#fecdd3; }
        .badge.dark { background:rgba(255,255,255,.12); color:white; border-color:rgba(255,255,255,.22); }
        .metric-card,.info-card,.lab-card,.tool-card,.case-card,.demo-card {
          background:var(--card); border:1px solid var(--line); border-radius:18px; padding:1rem 1.08rem;
          box-shadow:0 8px 24px rgba(15,23,42,.055); min-height:100%; overflow:hidden;
        }
        .tool-card,.demo-card { word-break:break-word; }
        .metric-card .value { font-size:2rem; font-weight:850; color:var(--teal); line-height:1; }
        .metric-card .label { font-size:.86rem; color:var(--muted); margin-top:.45rem; }
        .section-label { font-size:.74rem; text-transform:uppercase; letter-spacing:.14em; color:var(--teal); font-weight:850; margin-bottom:.25rem; }
        .icon-title { display:flex; gap:.7rem; align-items:flex-start; min-width:0; }
        .icon-orb { display:inline-flex; align-items:center; justify-content:center; width:2.5rem; height:2.5rem; min-width:2.5rem; border-radius:14px; background:linear-gradient(135deg,#dff7fb,#e8ecff); font-size:1.25rem; border:1px solid #c7e5ef; }
        .safety-banner { background:#fff7ed; border:1px solid #fed7aa; color:#7c2d12; border-radius:14px; padding:.82rem 1rem; margin:.4rem 0 1rem; }
        .success-banner { background:#ecfdf5; border:1px solid #a7f3d0; color:#065f46; border-radius:14px; padding:.82rem 1rem; }
        .soft-banner { background:#eff6ff; border:1px solid #bfdbfe; color:#1e3a8a; border-radius:14px; padding:.82rem 1rem; }
        .timeline-row { display:grid; grid-template-columns:86px minmax(0,1fr) 116px; gap:.8rem; align-items:center; padding:.85rem 0; border-bottom:1px solid #e2e8f0; }
        .timeline-time { font-weight:850; color:var(--teal); }
        .timeline-phase { color:var(--ink); font-weight:750; min-width:0; }
        .timeline-mode { text-align:right; color:var(--muted); font-size:.84rem; }
        .tiny { font-size:.78rem; color:var(--muted); }
        .risk-low { background:#ecfdf5; color:#065f46; border-left:5px solid #10b981; }
        .risk-medium { background:#fffbeb; color:#92400e; border-left:5px solid #f59e0b; }
        .risk-high { background:#fff7ed; color:#9a3412; border-left:5px solid #f97316; }
        .risk-critical { background:#fef2f2; color:#991b1b; border-left:5px solid #ef4444; }
        .slide-shell { background:#fff; border:1px solid #dbeafe; border-radius:20px; padding:.75rem; box-shadow:0 10px 28px rgba(15,23,42,.07); }
        .slide-shell img { width:100%; height:auto; display:block; border-radius:12px; }
        .footer { text-align:center; color:#64748b; font-size:.77rem; padding-top:2rem; }
        div[data-testid="stDataFrame"] { border:1px solid #dbeafe; border-radius:14px; overflow:hidden; }
        .stButton button, .stDownloadButton button, .stLinkButton a { border-radius:12px !important; font-weight:750 !important; min-height:2.6rem; white-space:normal !important; line-height:1.25 !important; }
        .stTabs [data-baseweb="tab-list"] { gap:.35rem; flex-wrap:wrap; }
        .stTabs [data-baseweb="tab"] { border-radius:10px 10px 0 0; padding:.55rem .9rem; white-space:normal; }
        code { white-space:pre-wrap !important; word-break:break-word !important; }
        @media (max-width: 900px) {
          .hero-content { padding:30px; }
          .timeline-row { grid-template-columns:72px minmax(0,1fr); }
          .timeline-mode { display:none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def image_as_data_uri(path: Path) -> str:
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{data}"


def hero(title: str, subtitle: str, image_name: str = "hero.png", kicker: str = "Alkem AI Masterclass") -> None:
    uri = image_as_data_uri(ASSETS / image_name)
    st.markdown(
        f"""
        <div class="hero" style="background-image:url('{uri}')">
          <div class="hero-overlay"></div>
          <div class="hero-content">
            <div class="brand-lockup">ALKEM&nbsp;&nbsp;|&nbsp;&nbsp;AI MASTERCLASS</div>
            <div class="hero-kicker">{kicker}</div>
            <h1>{title}</h1><p>{subtitle}</p>
            <div class="badge-row">
              <span class="badge dark">⏱️ 60 min theory</span><span class="badge dark">🧪 90 min hands-on</span>
              <span class="badge dark">🧬 Synthetic data only</span><span class="badge dark">🛡️ Human verification</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(kicker: str, title: str, body: str | None = None, icon: str | None = None) -> None:
    st.markdown(f'<div class="section-label">{kicker}</div>', unsafe_allow_html=True)
    if icon:
        st.markdown(f'<div class="icon-title"><span class="icon-orb">{icon}</span><div><h2 style="margin:.05rem 0 .2rem">{title}</h2></div></div>', unsafe_allow_html=True)
    else:
        st.header(title)
    if body:
        st.write(body)


def badges(items: list[str], tone: str = "") -> None:
    cls = f" {tone}" if tone else ""
    html = '<div class="badge-row">' + ''.join(f'<span class="badge{cls}">{item}</span>' for item in items) + '</div>'
    st.markdown(html, unsafe_allow_html=True)


def safety_banner() -> None:
    st.markdown(
        """
        <div class="safety-banner"><b>Clinical data boundary:</b> Use synthetic data in this workshop. Never paste identifiable data into a personal or public AI account. Real-world use requires an institution-approved environment, appropriate contracts, access controls, auditability and qualified human review.</div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(value: str, label: str) -> None:
    st.markdown(f'<div class="metric-card"><div class="value">{value}</div><div class="label">{label}</div></div>', unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_csv(filename: str) -> pd.DataFrame:
    return pd.read_csv(DATA / filename)


@st.cache_data(show_spinner=False)
def load_text(filename: str) -> str:
    return (DATA / filename).read_text(encoding="utf-8")


@st.cache_data(show_spinner=False)
def load_json(filename: str) -> Any:
    return json.loads((DATA / filename).read_text(encoding="utf-8"))


def file_bytes(path: Path) -> bytes:
    return path.read_bytes()


def download_asset(label: str, filename: str, mime: str, key: str | None = None) -> None:
    path = DOWNLOADS / filename
    if not path.exists():
        st.warning(f"Resource not found: {filename}")
        return
    st.download_button(label, data=file_bytes(path), file_name=path.name, mime=mime, key=key, use_container_width=True)


def download_dataset(filename: str, label: str | None = None, key: str | None = None) -> None:
    path = DATA / filename
    st.download_button(label or f"Download {filename}", data=path.read_bytes(), file_name=filename, mime="text/csv", key=key, use_container_width=True)


def footer() -> None:
    st.markdown("<div class='footer'>Alkem AI Masterclass • GenAI for Patient-Centric Healthcare • Synthetic-data learning studio</div>", unsafe_allow_html=True)


def set_visited(page: str) -> None:
    visited = set(st.session_state.get("visited_pages", set()))
    visited.add(page)
    st.session_state.visited_pages = visited


def json_download(data: dict[str, Any], filename: str) -> bytes:
    del filename
    return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")


def record_to_text(row: pd.Series) -> str:
    return "\n".join(f"{key}: {value}" for key, value in row.items())
