import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import time
import json
import os
import hashlib
import secrets
import smtplib
from email.message import EmailMessage
try:
    from streamlit_autorefresh import st_autorefresh  # type: ignore[import-untyped]
except ImportError:
    # fallback if package not installed
    def st_autorefresh(interval=1000, key=None):
        pass
import sys

import plotly.graph_objects as go

# --- Page Config (must be first) ---
st.set_page_config(page_title="Smart Factory", layout="wide")

# --- Load CSS once (cached) ---
@st.cache_data
def load_css():
    return """
<style>
.stApp {
    background: radial-gradient(circle at top, #16233b 0%, #0f172a 45%, #0b1120 100%);
    color: #f8fafc;
}
.disconnect-modal {
    background: linear-gradient(140deg, rgba(69,10,10,0.94) 0%, rgba(127,29,29,0.92) 45%, rgba(30,41,59,0.94) 100%);
    border: 1px solid #f87171;
    border-radius: 20px;
    padding: 22px;
    margin: 16px 0 8px 0;
    box-shadow: 0 24px 54px rgba(127, 29, 29, 0.28);
    text-align: center;
}

.page-section {
    background: linear-gradient(180deg, rgba(15,23,42,0.9) 0%, rgba(17,24,39,0.9) 100%);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 14px;
    margin: 10px 0;
}

/* platform sidebar nav styling */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div > div,
[data-testid="stSidebarContent"],
[data-testid="stSidebar"] section[data-testid="stSidebarContent"] {
    background: #0b1220 !important;
    border-left: 1px solid #1e293b !important;
    border-right: none !important;
}
.disconnect-title {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 800;
    color: #fee2e2;
}
.disconnect-sub {
    margin: 10px 0 0 0;
    font-size: 1rem;
    color: #fecaca;
}

[data-testid="stSidebar"],
[data-testid="stSidebarNav"] {
    display: none;
}

.stApp, .stMarkdown, .stCaption, .stText, p, li, label, div {
    color: #e5eefb;
}

h1, h2, h3, h4, h5, h6 {
    color: #f8fafc !important;
    letter-spacing: 0.01em;
}

[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stMetricDelta"] {
    color: #f8fafc !important;
}

[data-testid="stCaptionContainer"] {
    color: #cbd5e1 !important;
}

[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
    color: #e5eefb;
}

.card {
    background: linear-gradient(180deg, rgba(17,24,39,0.94) 0%, rgba(15,23,42,0.98) 100%);
    border: 1px solid #334155;
    box-shadow: 0 16px 32px rgba(2, 8, 23, 0.28);
    border-radius: 16px;
    padding: 16px;
    margin: 8px 0;
}

.welcome-card,
.feature-card,
.status-card {
    background: linear-gradient(180deg, rgba(15,23,42,0.95) 0%, rgba(17,24,39,0.95) 100%);
    border: 1px solid #334155;
    box-shadow: 0 18px 40px rgba(2, 8, 23, 0.24);
    border-radius: 18px;
    padding: 18px;
    margin: 10px 0;
}

.top-nav-shell {
    background: linear-gradient(180deg, rgba(8,15,30,0.96) 0%, rgba(15,23,42,0.96) 100%);
    border: 1px solid #334155;
    box-shadow: 0 20px 44px rgba(2, 8, 23, 0.32);
    border-radius: 20px;
    padding: 10px 12px;
    margin: 0 0 8px 0;
}

.top-nav-divider {
    width: 1px;
    min-height: 42px;
    background: linear-gradient(180deg, rgba(148,163,184,0.1) 0%, rgba(148,163,184,0.9) 50%, rgba(148,163,184,0.1) 100%);
}

.stButton > button {
    background: linear-gradient(180deg, #172554 0%, #1e3a8a 100%) !important;
    color: #eff6ff !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    box-shadow: 0 10px 24px rgba(30, 64, 175, 0.24);
}

.stButton > button:hover {
    background: linear-gradient(180deg, #1e3a8a 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border-color: #60a5fa !important;
}

.stForm [data-testid="stFormSubmitButton"] > button,
.stForm button,
[data-testid="stFormSubmitButton"] > button,
[data-testid="stDownloadButton"] > button,
.stDownloadButton > button,
.stLinkButton > a,
button[kind="primary"],
button[kind="secondary"],
button[kind="tertiary"],
button[kind="header"],
button[data-testid="baseButton-primary"],
button[data-testid="baseButton-secondary"],
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-secondary"] {
    background: linear-gradient(180deg, #172554 0%, #1e3a8a 100%) !important;
    color: #eff6ff !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    box-shadow: 0 10px 24px rgba(30, 64, 175, 0.24) !important;
}

.stLinkButton > a {
    text-decoration: none !important;
    padding: 0.45rem 0.9rem !important;
}

.stButton > button[kind="secondary"] {
    background: linear-gradient(180deg, #111827 0%, #1f2937 100%) !important;
    color: #e2e8f0 !important;
    border: 1px solid #475569 !important;
    box-shadow: none;
}

button[kind="secondary"],
button[data-testid="baseButton-secondary"],
button[data-testid="stBaseButton-secondary"] {
    background: linear-gradient(180deg, #111827 0%, #1f2937 100%) !important;
    color: #e2e8f0 !important;
    border: 1px solid #475569 !important;
    box-shadow: none !important;
}

.stButton > button:disabled {
    opacity: 1 !important;
    background: linear-gradient(180deg, #0f766e 0%, #115e59 100%) !important;
    color: #ecfeff !important;
    border-color: #2dd4bf !important;
}

/* Form controls: force dark backgrounds + light text for dropdowns/select menus */
[data-baseweb="select"] > div {
    background: #111827 !important;
    border-color: #334155 !important;
}

[data-baseweb="select"] * {
    color: #e2e8f0 !important;
}

div[role="listbox"] {
    background: #111827 !important;
    border: 1px solid #334155 !important;
}

div[role="option"] {
    background: #111827 !important;
    color: #e2e8f0 !important;
}

div[role="option"][aria-selected="true"] {
    background: #1e3a8a !important;
    color: #eff6ff !important;
}

div[role="option"]:hover {
    background: #1f2937 !important;
    color: #f8fafc !important;
}

.stMultiSelect [data-baseweb="tag"] {
    background: #1e293b !important;
    color: #dbeafe !important;
    border: 1px solid #334155 !important;
}

.stRadio label,
.stCheckbox label {
    color: #e2e8f0 !important;
}

/* Extra hardening for clicked/focused select states */
.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div {
    background: #111827 !important;
    color: #e2e8f0 !important;
}

.stSelectbox [data-baseweb="select"] > div:focus-within,
.stMultiSelect [data-baseweb="select"] > div:focus-within,
.stSelectbox [data-baseweb="select"] > div:hover,
.stMultiSelect [data-baseweb="select"] > div:hover {
    background: #0f172a !important;
    border-color: #60a5fa !important;
    box-shadow: 0 0 0 1px #60a5fa inset !important;
}

.stSelectbox [data-baseweb="select"] input,
.stMultiSelect [data-baseweb="select"] input,
.stSelectbox [data-baseweb="select"] span,
.stMultiSelect [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] div,
.stMultiSelect [data-baseweb="select"] div {
    color: #e2e8f0 !important;
}

div[data-baseweb="popover"] div[role="listbox"],
div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] li {
    background: #111827 !important;
    color: #e2e8f0 !important;
}

div[data-baseweb="popover"] [aria-selected="true"],
div[data-baseweb="popover"] li[aria-selected="true"] {
    background: #1e3a8a !important;
    color: #eff6ff !important;
}

.stPlotlyChart {
    background: rgba(15, 23, 42, 0.55);
    border-radius: 18px;
    padding: 6px;
}

a {
    color: #93c5fd;
}

.settings-hero {
    background: linear-gradient(130deg, rgba(30,41,59,0.94) 0%, rgba(15,23,42,0.95) 45%, rgba(15,118,110,0.3) 100%);
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 18px 20px;
    margin: 8px 0 14px 0;
}

.settings-hero-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #f8fafc;
}

.settings-hero-sub {
    font-size: 0.95rem;
    color: #dbeafe;
    margin-top: 6px;
}

.settings-chip {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid #475569;
    background: rgba(15, 23, 42, 0.8);
    color: #e2e8f0;
    font-size: 0.82rem;
    margin-right: 6px;
}

.settings-section {
    background: linear-gradient(180deg, rgba(15,23,42,0.9) 0%, rgba(17,24,39,0.9) 100%);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 14px;
    margin: 10px 0;
}

[data-testid="stSegmentedControl"] {
    background: transparent !important;
}

[data-testid="stSegmentedControl"] > div {
    background: transparent !important;
}

[data-testid="stSegmentedControl"] [role="radiogroup"] {
    background: linear-gradient(180deg, rgba(12, 20, 36, 0.96) 0%, rgba(15, 23, 42, 0.96) 100%) !important;
    border: 1px solid #265073 !important;
    border-radius: 999px !important;
    padding: 3px !important;
    gap: 4px !important;
}

[data-testid="stSegmentedControl"] [role="radio"] {
    min-height: 30px !important;
    padding: 0 10px !important;
    border-radius: 999px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: #d1e7ff !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}

[data-testid="stSegmentedControl"] button {
    background: transparent !important;
    color: #d1e7ff !important;
    border: 1px solid transparent !important;
}

[data-testid="stSegmentedControl"] button[aria-pressed="true"],
[data-testid="stSegmentedControl"] button[aria-selected="true"],
[data-testid="stSegmentedControl"] [data-selected="true"] {
    background: linear-gradient(180deg, #0ea5e9 0%, #2563eb 100%) !important;
    color: #eff6ff !important;
    border-color: #7dd3fc !important;
    box-shadow: 0 6px 16px rgba(14, 165, 233, 0.32) !important;
}

[data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"] {
    background: linear-gradient(180deg, #0ea5e9 0%, #2563eb 100%) !important;
    color: #eff6ff !important;
    border-color: #7dd3fc !important;
    box-shadow: 0 6px 16px rgba(14, 165, 233, 0.32) !important;
}

[data-testid="stSegmentedControl"] [role="radio"]:hover {
    background: rgba(37, 99, 235, 0.18) !important;
    color: #eff6ff !important;
}

/* ── Account page left-nav panel ── */
/* ── Account page: style columns via :has() on marker spans ── */
.acct-nav-marker, .acct-content-marker { display: none; }

[data-testid="column"]:has(.acct-nav-marker) {
    background: transparent;
    padding: 0 !important;
}
[data-testid="column"]:has(.acct-nav-marker) .stButton > button {
    width: 100%;
    text-align: left !important;
    justify-content: flex-start !important;
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    color: #64748b !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
    margin-bottom: 1px;
    box-shadow: none !important;
    letter-spacing: 0.01em;
    transition: all 0.18s cubic-bezier(0.4,0,0.2,1);
}
[data-testid="column"]:has(.acct-nav-marker) .stButton > button:hover {
    background: rgba(59,130,246,0.08) !important;
    color: #cbd5e1 !important;
    transform: translateX(2px);
}
[data-testid="column"]:has(.acct-nav-marker) .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(59,130,246,0.20) 0%, rgba(99,102,241,0.15) 100%) !important;
    color: #93c5fd !important;
    font-weight: 700 !important;
    box-shadow: inset 3px 0 0 #3b82f6, 0 2px 8px rgba(59,130,246,0.12) !important;
}
[data-testid="column"]:has(.acct-nav-marker) .stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, rgba(59,130,246,0.28) 0%, rgba(99,102,241,0.22) 100%) !important;
    transform: translateX(2px);
}
[data-testid="column"]:has(.acct-content-marker) {
    background: linear-gradient(160deg, rgba(15,23,42,0.85) 0%, rgba(17,24,39,0.92) 60%, rgba(30,41,59,0.75) 100%);
    border: 1px solid rgba(51,65,85,0.5);
    border-radius: 20px;
    padding: 28px 30px !important;
    min-height: 480px;
    box-shadow: 0 8px 32px rgba(2,8,23,0.28), inset 0 1px 0 rgba(148,163,184,0.06);
}
[data-testid="column"]:has(.acct-content-marker) h2,
[data-testid="column"]:has(.acct-content-marker) h3 {
    color: #f1f5f9 !important;
    margin-bottom: 18px !important;
}
.acct-nav-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #475569;
    padding: 4px 14px 10px 14px;
    display: block;
}

    margin: 6px 0 8px 0;
}

.connect-wrap {
    background: linear-gradient(130deg, rgba(30,41,59,0.95) 0%, rgba(15,23,42,0.96) 55%, rgba(14,116,144,0.28) 100%);
    border: 1px solid #334155;
    border-radius: 20px;
    padding: 18px 20px;
    text-align: center;
    box-shadow: 0 16px 36px rgba(2, 8, 23, 0.28);
}

.connect-title {
    margin: 0;
    color: #f8fafc;
    font-size: 1.35rem;
    font-weight: 800;
}

.connect-sub {
    margin: 6px 0 0 0;
    color: #cbd5e1;
    font-size: 0.95rem;
}

.connect-status {
    text-align: center;
    margin-bottom: 16px;
    padding: 14px;
    border-radius: 16px;
    border: 1px solid #334155;
    background: rgba(15, 23, 42, 0.72);
}

.connect-status-icon {
    font-size: 2.2rem;
    line-height: 1;
}

.connect-status-label {
    margin: 8px 0 4px 0;
    font-weight: 700;
}

.connect-status-meta {
    margin: 0;
    color: #cbd5e1;
    font-size: 0.85rem;
}

.device-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-radius: 14px;
    border: 1px solid #334155;
    background: linear-gradient(180deg, rgba(17,24,39,0.92) 0%, rgba(15,23,42,0.95) 100%);
}

.device-icon {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    display: grid;
    place-items: center;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    color: #0f172a;
    background: linear-gradient(180deg, #67e8f9 0%, #22d3ee 100%);
}

.device-info {
    flex: 1;
}

.device-name {
    margin: 0;
    color: #f8fafc;
    font-weight: 700;
}

.device-ip {
    margin: 2px 0 0 0;
    color: #cbd5e1;
    font-size: 0.82rem;
}

.device-connected-badge {
    border: 1px solid #0f766e;
    background: rgba(20, 184, 166, 0.2);
    color: #99f6e4;
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 0.75rem;
    font-weight: 700;
}

.connect-section-label {
    color: #cbd5e1;
    font-size: 0.85rem;
    margin: 0 0 8px 0;
    font-weight: 700;
}

.connect-anim-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 8px 0 14px 0;
}

.connect-radar {
    position: relative;
    width: 94px;
    height: 94px;
    border-radius: 999px;
    border: 2px solid rgba(34, 211, 238, 0.75);
    background: radial-gradient(circle, rgba(34,211,238,0.22) 0%, rgba(15,23,42,0.2) 62%, rgba(15,23,42,0) 100%);
}

.connect-radar::before,
.connect-radar::after {
    content: "";
    position: absolute;
    inset: -2px;
    border-radius: 999px;
    border: 2px solid rgba(56, 189, 248, 0.5);
    animation: radarPulse 1.8s ease-out infinite;
}

.connect-radar::after {
    animation-delay: 0.9s;
}

.connect-radar-dot {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 14px;
    height: 14px;
    transform: translate(-50%, -50%);
    border-radius: 999px;
    background: #67e8f9;
    box-shadow: 0 0 0 0 rgba(103, 232, 249, 0.8);
    animation: dotGlow 1.6s ease-in-out infinite;
}

.connect-feature-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
    margin: 0 0 12px 0;
}

.connect-feature-card {
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 12px;
    background: linear-gradient(180deg, rgba(17,24,39,0.9) 0%, rgba(15,23,42,0.92) 100%);
}

.connect-feature-title {
    margin: 0;
    font-size: 0.9rem;
    font-weight: 700;
    color: #f8fafc;
}

.connect-feature-text {
    margin: 6px 0 0 0;
    font-size: 0.82rem;
    color: #cbd5e1;
}

.history-hero {
    background: linear-gradient(130deg, rgba(30,41,59,0.95) 0%, rgba(15,23,42,0.96) 58%, rgba(59,130,246,0.18) 100%);
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 18px 20px;
    margin: 8px 0 14px 0;
}

.history-hero-title {
    margin: 0;
    color: #f8fafc;
    font-size: 1.3rem;
    font-weight: 800;
}

.history-hero-sub {
    margin: 8px 0 0 0;
    color: #cbd5e1;
    font-size: 0.94rem;
}

.history-chip {
    display: inline-block;
    padding: 4px 10px;
    margin: 10px 6px 0 0;
    border-radius: 999px;
    border: 1px solid #475569;
    background: rgba(15, 23, 42, 0.72);
    color: #e2e8f0;
    font-size: 0.8rem;
    font-weight: 600;
}

.history-section {
    background: linear-gradient(180deg, rgba(15,23,42,0.92) 0%, rgba(17,24,39,0.92) 100%);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 14px;
    margin: 10px 0;
}

.history-event-card {
    background: linear-gradient(180deg, rgba(30,41,59,0.92) 0%, rgba(15,23,42,0.96) 100%);
    border: 1px solid #334155;
    border-left-width: 5px;
    padding: 14px 16px;
    border-radius: 14px;
    margin-bottom: 10px;
    box-shadow: 0 10px 28px rgba(2, 8, 23, 0.18);
}

.history-event-top {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
}

.history-badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    background: rgba(15, 23, 42, 0.66);
}

.history-timestamp {
    color: #94a3b8;
    font-size: 0.85rem;
}

.history-message {
    color: #e2e8f0;
    margin-top: 9px;
    line-height: 1.45;
}

@keyframes radarPulse {
    0% {
        transform: scale(1);
        opacity: 0.75;
    }
    100% {
        transform: scale(1.55);
        opacity: 0;
    }
}

@keyframes dotGlow {
    0%, 100% {
        box-shadow: 0 0 0 0 rgba(103, 232, 249, 0.75);
    }
    50% {
        box-shadow: 0 0 0 10px rgba(103, 232, 249, 0.05);
    }
}

@media (max-width: 900px) {
    .connect-feature-grid {
        grid-template-columns: 1fr;
    }
}
</style>
"""


st.markdown(load_css(), unsafe_allow_html=True)


if 'language' not in st.session_state:
    st.session_state.language = 'EN'
if 'num_machines' not in st.session_state:
    st.session_state.num_machines = 3
if 'refresh_rate' not in st.session_state:
    st.session_state.refresh_rate = 1
if 'machine_names' not in st.session_state:
    st.session_state.machine_names = [f"Machine {i}" for i in range(1, st.session_state.num_machines + 1)]
if 'df' not in st.session_state:
    _initial = {f"current_{i}": np.zeros(50) for i in range(1, st.session_state.num_machines + 1)}
    st.session_state.df = pd.DataFrame(_initial)
    st.session_state.df["timestamp"] = pd.date_range(end=pd.Timestamp.now(), periods=50, freq="1s")
if 'last_current_values' not in st.session_state:
    st.session_state.last_current_values = {
        f"current_{i}": 0.0 for i in range(1, st.session_state.num_machines + 1)
    }


def t(en: str, nl: str) -> str:
    return en if st.session_state.get('language', 'EN') == 'EN' else nl


USER_DB_FILE = os.path.join(os.path.dirname(__file__), "users.json")


def load_user_db():
    if not os.path.exists(USER_DB_FILE):
        return {"users": {}}
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and isinstance(data.get("users"), dict):
            return data
    except Exception:
        pass
    return {"users": {}}


def save_user_db(db):
    try:
        with open(USER_DB_FILE, "w", encoding="utf-8") as fh:
            json.dump(db, fh)
    except Exception as exc:
        print("Error saving user database:", exc, file=sys.stderr)


def hash_password(password, salt_hex):
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200000)
    return digest.hex()


def register_user(username, password, profile_name="", profile_email="", profile_company=""):
    username = (username or "").strip().lower()
    if not username:
        return False, "Gebruikersnaam is verplicht."
    if len(password or "") < 6:
        return False, "Wachtwoord moet minimaal 6 tekens hebben."

    db = load_user_db()
    users = db.setdefault("users", {})
    if username in users:
        return False, "Deze gebruikersnaam bestaat al."

    salt_hex = secrets.token_hex(16)
    users[username] = {
        "salt": salt_hex,
        "password_hash": hash_password(password, salt_hex),
        "state": {
            "profile_name": str(profile_name or "").strip(),
            "profile_email": str(profile_email or "").strip(),
            "profile_company": str(profile_company or "").strip(),
        },
    }
    save_user_db(db)
    return True, "Account aangemaakt."


def authenticate_user(username, password):
    username = (username or "").strip().lower()
    db = load_user_db()
    user_record = db.get("users", {}).get(username)
    if not user_record:
        return False

    expected = user_record.get("password_hash", "")
    salt_hex = user_record.get("salt", "")
    if not expected or not salt_hex:
        return False

    return hash_password(password, salt_hex) == expected


def send_login_email(username):
    """Send a login notification email for the given username.

    Configuration is read from environment variables:
    - SMARTFACTORY_SMTP_HOST
    - SMARTFACTORY_SMTP_PORT (optional, default: 587)
    - SMARTFACTORY_SMTP_USER
    - SMARTFACTORY_SMTP_PASS
    - SMARTFACTORY_EMAIL_FROM (optional, defaults to SMTP user)
    """
    username = (username or "").strip().lower()
    if not username:
        return False, "No username"

    smtp_host = os.getenv("SMARTFACTORY_SMTP_HOST", "").strip()
    smtp_user = os.getenv("SMARTFACTORY_SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMARTFACTORY_SMTP_PASS", "").strip()
    smtp_from = os.getenv("SMARTFACTORY_EMAIL_FROM", "").strip() or smtp_user
    smtp_port_raw = os.getenv("SMARTFACTORY_SMTP_PORT", "587").strip()

    if not smtp_host or not smtp_user or not smtp_pass or not smtp_from:
        return False, "SMTP not configured"

    try:
        smtp_port = int(smtp_port_raw)
    except ValueError:
        smtp_port = 587

    db = load_user_db()
    user_record = db.get("users", {}).get(username, {})
    user_state = user_record.get("state", {}) if isinstance(user_record, dict) else {}
    recipient = str(user_state.get("profile_email", "")).strip()
    if not recipient:
        return False, "No recipient email"

    msg = EmailMessage()
    msg["Subject"] = f"Login alert for {username}"
    msg["From"] = smtp_from
    msg["To"] = recipient
    msg.set_content(
        f"Hello {username},\n\n"
        f"A successful login was detected for your Smart Factory account.\n\n"
        f"If this was not you, please change your password immediately.\n"
    )

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.ehlo()
            if smtp_port in (587, 25):
                server.starttls()
                server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True, "Email sent"
    except Exception as exc:
        return False, str(exc)


def set_user_remember_token(username):
    username = (username or "").strip().lower()
    if not username:
        return ""
    db = load_user_db()
    users = db.setdefault("users", {})
    user_record = users.get(username)
    if not user_record:
        return ""
    token = secrets.token_urlsafe(24)
    user_record["remember_token"] = token
    users[username] = user_record
    save_user_db(db)
    return token


def get_username_by_remember_token(token):
    token = (token or "").strip()
    if not token:
        return None
    db = load_user_db()
    for username, user_record in db.get("users", {}).items():
        if user_record.get("remember_token") == token:
            return username
    return None


def clear_user_remember_token(username):
    username = (username or "").strip().lower()
    if not username:
        return
    db = load_user_db()
    users = db.setdefault("users", {})
    user_record = users.get(username)
    if not user_record:
        return
    user_record["remember_token"] = ""
    users[username] = user_record
    save_user_db(db)


def perform_logout():
    """
    Comprehensive logout function that:
    1. Saves current user state to database
    2. Clears remember token
    3. Resets all session variables
    4. Clears query parameters
    5. Restarts the app
    """
    current_user = st.session_state.get("auth_user")
    
    # Step 1: Persist current user state
    if current_user:
        persist_active_user_state()
        clear_user_remember_token(current_user)
    
    # Step 2: Reset all authentication state
    st.session_state.auth_user = None
    st.session_state.auth_loaded_user = None
    
    # Step 3: Reset page and navigation
    st.session_state.page = "Platform"
    st.session_state.last_non_device_page = "Platform"
    st.session_state.pending_mode = None
    
    # Step 4: Reset user preferences to defaults
    st.session_state.language = 'EN'
    st.session_state.mode = 'Simulation'
    st.session_state.num_machines = 3
    st.session_state.refresh_rate = 1
    st.session_state.machine_names = [f"Machine {i}" for i in range(1, 4)]
    
    # Step 5: Clear device/connection state
    st.session_state.connected_devices = []
    st.session_state.show_disconnect_prompt = False
    st.session_state.ble_prov_devices = []
    
    # Step 6: Clear cloud bridge settings (except API key)
    st.session_state.cloud_bridge_enabled = False
    st.session_state.cloud_bridge_max_age_s = 300
    st.session_state.cloud_bridge_public_base_url = ""
    
    # Step 7: Reset simulation data
    st.session_state.sim_machine_profiles = {}
    st.session_state.sim_tick = 0
    st.session_state.last_current_values = {}
    st.session_state.target_currents = {}
    
    # Step 8: Clear display/animation state
    st.session_state.smoothed_currents = {}
    st.session_state.gauge_display_values = {}
    
    # Step 9: Reset UI state
    st.session_state.welcome_shown = False
    st.session_state._last_page = None
    
    # Step 10: Clear query parameters and trigger rerun
    st.query_params.clear()
    st.rerun()


def restore_auth_from_query_token():
    """Restore auth session from persistent query token when possible."""
    if st.session_state.get("auth_user"):
        return
    token = str(st.query_params.get("auth", "") or "").strip()
    if not token:
        return
    username = get_username_by_remember_token(token)
    if not username:
        return
    st.session_state.auth_user = username
    st.session_state.auth_loaded_user = username
    db = load_user_db()
    user_state = db.get("users", {}).get(username, {}).get("state", {})
    apply_user_state(user_state)


def serialize_current_user_state():
    df_local = st.session_state.get("df", pd.DataFrame())
    df_records = []
    if isinstance(df_local, pd.DataFrame) and not df_local.empty:
        tmp_df = df_local.tail(300).copy()
        if "timestamp" in tmp_df.columns:
            ts = pd.to_datetime(tmp_df["timestamp"], errors="coerce")
            tmp_df["timestamp"] = ts.dt.strftime("%Y-%m-%d %H:%M:%S").fillna("")
        df_records = tmp_df.to_dict(orient="records")

    return {
        "language": st.session_state.get("language", "EN"),
        "num_machines": int(st.session_state.get("num_machines", 3)),
        "refresh_rate": int(st.session_state.get("refresh_rate", 1)),
        "machine_names": list(st.session_state.get("machine_names", [])),
        "profile_name": st.session_state.get("profile_name", ""),
        "profile_email": st.session_state.get("profile_email", ""),
        "profile_company": st.session_state.get("profile_company", ""),
        "notifications_faults": bool(st.session_state.get("notifications_faults", True)),
        "notifications_email": bool(st.session_state.get("notifications_email", True)),
        "notifications_push": bool(st.session_state.get("notifications_push", False)),
        "theme_preference": st.session_state.get("theme_preference", "Dark"),
        "dashboard_preference": st.session_state.get("dashboard_preference", "Overview"),
        "subscription_plan": st.session_state.get("subscription_plan", "Starter"),
        "invoice_history": list(st.session_state.get("invoice_history", []))[:50],
        "mode": st.session_state.get("mode", "Simulation"),
        "cloud_bridge_enabled": bool(st.session_state.get("cloud_bridge_enabled", False)),
        "cloud_bridge_max_age_s": int(st.session_state.get("cloud_bridge_max_age_s", 300)),
        "cloud_bridge_public_base_url": st.session_state.get("cloud_bridge_public_base_url", ""),
        "cloud_bridge_api_key": st.session_state.get("cloud_bridge_api_key", ""),
        "event_history": list(st.session_state.get("event_history", []))[:300],
        "anomalies": list(st.session_state.get("anomalies", []))[:300],
        "bottlenecks": list(st.session_state.get("bottlenecks", []))[:300],
        "df_records": df_records,
    }


def apply_user_state(state):
    if not isinstance(state, dict):
        return

    st.session_state.language = state.get("language", st.session_state.get("language", "EN"))
    st.session_state.num_machines = int(state.get("num_machines", st.session_state.get("num_machines", 3)))
    st.session_state.refresh_rate = int(state.get("refresh_rate", st.session_state.get("refresh_rate", 1)))
    st.session_state.machine_names = list(
        state.get("machine_names", [f"Machine {i}" for i in range(1, st.session_state.num_machines + 1)])
    )[: st.session_state.num_machines]
    if len(st.session_state.machine_names) < st.session_state.num_machines:
        start = len(st.session_state.machine_names) + 1
        st.session_state.machine_names.extend(
            [f"Machine {i}" for i in range(start, st.session_state.num_machines + 1)]
        )

    st.session_state.mode = state.get("mode", st.session_state.get("mode", "Simulation"))
    st.session_state.profile_name = state.get("profile_name", st.session_state.get("profile_name", ""))
    st.session_state.profile_email = state.get("profile_email", st.session_state.get("profile_email", ""))
    st.session_state.profile_company = state.get("profile_company", st.session_state.get("profile_company", ""))
    st.session_state.notifications_faults = bool(state.get("notifications_faults", st.session_state.get("notifications_faults", True)))
    st.session_state.notifications_email = bool(state.get("notifications_email", st.session_state.get("notifications_email", True)))
    st.session_state.notifications_push = bool(state.get("notifications_push", st.session_state.get("notifications_push", False)))
    st.session_state.theme_preference = state.get("theme_preference", st.session_state.get("theme_preference", "Dark"))
    st.session_state.dashboard_preference = state.get("dashboard_preference", st.session_state.get("dashboard_preference", "Overview"))
    st.session_state.subscription_plan = state.get("subscription_plan", st.session_state.get("subscription_plan", "Starter"))
    st.session_state.invoice_history = list(state.get("invoice_history", st.session_state.get("invoice_history", [])))
    st.session_state.cloud_bridge_enabled = bool(state.get("cloud_bridge_enabled", False))
    st.session_state.cloud_bridge_max_age_s = int(state.get("cloud_bridge_max_age_s", 300))
    st.session_state.cloud_bridge_public_base_url = state.get("cloud_bridge_public_base_url", "")
    st.session_state.cloud_bridge_api_key = state.get("cloud_bridge_api_key", st.session_state.get("cloud_bridge_api_key", ""))
    st.session_state.event_history = list(state.get("event_history", []))
    st.session_state.anomalies = list(state.get("anomalies", []))
    st.session_state.bottlenecks = list(state.get("bottlenecks", []))

    records = state.get("df_records", [])
    if isinstance(records, list) and records:
        loaded_df = pd.DataFrame(records)
        for i in range(1, st.session_state.num_machines + 1):
            col = f"current_{i}"
            if col not in loaded_df.columns:
                loaded_df[col] = 0.0
            loaded_df[col] = pd.to_numeric(loaded_df[col], errors="coerce").fillna(0.0)
        if "timestamp" in loaded_df.columns:
            loaded_df["timestamp"] = pd.to_datetime(loaded_df["timestamp"], errors="coerce")
        else:
            loaded_df["timestamp"] = pd.date_range(
                end=pd.Timestamp.now(),
                periods=len(loaded_df),
                freq=f"{max(1, int(st.session_state.refresh_rate))}s",
            )
        st.session_state.df = loaded_df.tail(300).reset_index(drop=True)


def persist_active_user_state():
    active_user = st.session_state.get("auth_user")
    if not active_user:
        return

    db = load_user_db()
    users = db.setdefault("users", {})
    user_record = users.get(active_user)
    if not user_record:
        return

    user_record["state"] = serialize_current_user_state()
    users[active_user] = user_record
    save_user_db(db)


if 'page' not in st.session_state:
    st.session_state.page = "Platform"
if 'welcome_shown' not in st.session_state:
    st.session_state.welcome_shown = False
if 'mode' not in st.session_state:
    st.session_state.mode = 'Simulation'
if 'connected_devices' not in st.session_state:
    st.session_state.connected_devices = []
if 'cloud_bridge_enabled' not in st.session_state:
    st.session_state.cloud_bridge_enabled = False
if 'cloud_bridge_max_age_s' not in st.session_state:
    st.session_state.cloud_bridge_max_age_s = 300
if 'cloud_bridge_public_base_url' not in st.session_state:
    st.session_state.cloud_bridge_public_base_url = ""
if 'cloud_bridge_api_key' not in st.session_state:
    st.session_state.cloud_bridge_api_key = os.getenv("MACHINE_MONITOR_API_KEY", "change-me")
if 'animation_tick_ms' not in st.session_state:
    # UI animation heartbeat; smaller is smoother but costs more CPU.
    st.session_state.animation_tick_ms = 300
if 'last_data_poll_ts' not in st.session_state:
    st.session_state.last_data_poll_ts = 0.0
if 'target_currents' not in st.session_state:
    st.session_state.target_currents = {}
if 'history_anchor_ts' not in st.session_state:
    st.session_state.history_anchor_ts = pd.Timestamp.now().isoformat()
if 'show_disconnect_prompt' not in st.session_state:
    st.session_state.show_disconnect_prompt = False
if 'sim_machine_profiles' not in st.session_state:
    st.session_state.sim_machine_profiles = {}
if 'sim_tick' not in st.session_state:
    st.session_state.sim_tick = 0
if 'smoothing_alpha' not in st.session_state:
    # Lower alpha means smoother, less jumpy visuals.
    st.session_state.smoothing_alpha = 0.15
if 'smoothed_currents' not in st.session_state:
    st.session_state.smoothed_currents = {}
if 'gauge_display_values' not in st.session_state:
    st.session_state.gauge_display_values = {}
if 'gauge_alpha' not in st.session_state:
    # Separate easing for gauges: lower values move more gradually.
    st.session_state.gauge_alpha = 0.35
if 'gauge_max_step' not in st.session_state:
    # Maximum ampere change per refresh to avoid sudden jumps.
    st.session_state.gauge_max_step = 0.45
if 'auth_user' not in st.session_state:
    st.session_state.auth_user = None
if 'auth_loaded_user' not in st.session_state:
    st.session_state.auth_loaded_user = None
if 'profile_name' not in st.session_state:
    st.session_state.profile_name = ""
if 'profile_email' not in st.session_state:
    st.session_state.profile_email = ""
if 'profile_company' not in st.session_state:
    st.session_state.profile_company = ""
if 'notifications_faults' not in st.session_state:
    st.session_state.notifications_faults = True
if 'notifications_email' not in st.session_state:
    st.session_state.notifications_email = True
if 'notifications_push' not in st.session_state:
    st.session_state.notifications_push = False
if 'theme_preference' not in st.session_state:
    st.session_state.theme_preference = "Dark"
if 'dashboard_preference' not in st.session_state:
    st.session_state.dashboard_preference = "Overview"
if 'subscription_plan' not in st.session_state:
    st.session_state.subscription_plan = "Starter"
if 'account_section' not in st.session_state:
    st.session_state.account_section = "profiel"
if 'invoice_history' not in st.session_state:
    st.session_state.invoice_history = [
        {"date": "2026-03-01", "description": "Starter Plan", "amount": "EUR 0.00", "status": "Paid"},
        {"date": "2026-02-01", "description": "Starter Plan", "amount": "EUR 0.00", "status": "Paid"},
    ]

# Reset BLE scanlijst als je de verbindingspagina verlaat.
if st.session_state.get('page') != "Device Connection":
    st.session_state.ble_prov_devices = []

NUM_MACHINES = int(st.session_state.get('num_machines', 3))

# --- Modus: wordt beheerd via Settings, niet via sidebar ---
# Zorg dat pending_mode afgehandeld wordt bij elke refresh
if st.session_state.get('pending_mode') == 'Live' and st.session_state.get('device_connected', False):
    st.session_state.mode = 'Live'
    st.session_state.pending_mode = None

def get_simulated_data():
    # Give each machine a distinct simulation profile so values do not move uniformly.
    machine_count = int(st.session_state.get('num_machines', 3))
    profiles = st.session_state.get('sim_machine_profiles', {})

    if not isinstance(profiles, dict) or len(profiles) != machine_count:
        rebuilt_profiles = {}
        for i in range(1, machine_count + 1):
            tier = (i - 1) % 4
            if tier == 0:
                base = float(np.random.uniform(1.0, 2.0))
            elif tier == 1:
                base = float(np.random.uniform(2.0, 3.0))
            elif tier == 2:
                base = float(np.random.uniform(3.0, 4.3))
            else:
                base = float(np.random.uniform(1.4, 3.8))

            rebuilt_profiles[f'current_{i}'] = {
                'base': base,
                'volatility': float(np.random.uniform(0.02, 0.12)),
                'spike_prob': float(np.random.uniform(0.01, 0.07)),
                'spike_scale': float(np.random.uniform(0.12, 0.65)),
                'cycle_amp': float(np.random.uniform(0.08, 0.75)),
                'cycle_speed': float(np.random.uniform(0.02, 0.09)),
                'phase': float(np.random.uniform(0.0, 2.0 * np.pi)),
            }

        st.session_state.sim_machine_profiles = rebuilt_profiles
        profiles = rebuilt_profiles

    if 'last_current_values' not in st.session_state or not isinstance(st.session_state.last_current_values, dict):
        st.session_state.last_current_values = {}

    st.session_state.sim_tick = int(st.session_state.get('sim_tick', 0)) + 1
    tick = st.session_state.sim_tick

    result = {}
    for i in range(1, machine_count + 1):
        key = f'current_{i}'
        profile = profiles[key]

        prev = float(st.session_state.last_current_values.get(key, 0.0))
        if prev <= 0.01:
            prev = float(profile['base'] + np.random.normal(0, 0.2))

        cycle_target = float(profile['base']) + float(profile['cycle_amp']) * np.sin(
            tick * float(profile['cycle_speed']) + float(profile['phase'])
        )
        drift_to_target = (cycle_target - prev) * 0.18
        noise = float(np.random.normal(0, float(profile['volatility'])))

        spike = 0.0
        if np.random.rand() < float(profile['spike_prob']):
            spike = float(np.random.normal(0, float(profile['spike_scale'])))

        new_val = float(np.clip(prev + drift_to_target + noise + spike, 0.5, 6.0))
        st.session_state.last_current_values[key] = new_val
        result[key] = new_val

    return result


def smooth_current_row(row, alpha=None):
    """Apply EMA smoothing so charts/metrics update more fluidly."""
    if alpha is None:
        alpha = float(st.session_state.get('smoothing_alpha', 0.22))

    smoothed = {}
    state = st.session_state.get('smoothed_currents', {})
    for key, value in row.items():
        if not str(key).startswith('current_'):
            smoothed[key] = value
            continue
        target = float(value)
        prev = float(state.get(key, target))
        val = prev + alpha * (target - prev)
        state[key] = val
        smoothed[key] = float(np.clip(val, 0.5, 6.0))

    st.session_state.smoothed_currents = state
    return smoothed


def animate_gauge_value(gauge_key, target, alpha=None, max_step=None):
    """Move a gauge value gradually toward target instead of jumping directly."""
    if alpha is None:
        alpha = float(st.session_state.get('gauge_alpha', 0.35))
    if max_step is None:
        max_step = float(st.session_state.get('gauge_max_step', 0.45))

    state = st.session_state.get('gauge_display_values', {})
    target = float(target)
    prev = float(state.get(gauge_key, target))
    delta = target - prev
    step = float(np.clip(delta * alpha, -max_step, max_step))
    current = prev + step
    state[gauge_key] = float(np.clip(current, 0.0, 8.0))
    st.session_state.gauge_display_values = state
    return state[gauge_key]


def build_device_endpoint(device_ip=None, device_port=None):
    ip_address = (device_ip or st.session_state.get('device_ip') or '192.168.1.100').strip()
    port = int(device_port or st.session_state.get('device_port') or 80)
    return f"http://{ip_address}:{port}/data"


PROV_CRED_UUID    = "12345678-1234-5678-1234-56789abcdef1"
PROV_STATUS_UUID  = "12345678-1234-5678-1234-56789abcdef2"


def get_current_wifi_ssid() -> str:
    """Probeer het huidige WiFi SSID te detecteren (macOS)."""
    import subprocess
    try:
        result = subprocess.run(
            ["networksetup", "-getairportnetwork", "en0"],
            capture_output=True, text=True, timeout=3
        )
        if "Current Wi-Fi Network:" in result.stdout:
            return result.stdout.split("Current Wi-Fi Network:")[-1].strip()
    except Exception:
        pass
    return ""


def get_current_wifi_password(ssid: str) -> str:
    """Haal het WiFi-wachtwoord op uit de macOS Keychain voor het opgegeven SSID."""
    import subprocess
    if not ssid:
        return ""
    try:
        result = subprocess.run(
            ["security", "find-generic-password",
             "-D", "AirPort network password", "-a", ssid, "-w"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def ble_scan_for_provisioning(timeout: float = 6.0) -> list:
    """
    Scan via Bluetooth LE naar unprovisioned ESP32s (adverteren als 'MM_PROV').
    Geeft lijst van dicts {'address': ..., 'name': ...} terug.
    """
    import asyncio
    import threading

    found = []

    async def _scan():
        from bleak import BleakScanner

        devices = await BleakScanner.discover(timeout=timeout)
        for d in devices:
            if d.name == "MM_PROV":
                found.append({"address": d.address, "name": d.name})

    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_scan())
        except Exception:
            pass
        finally:
            loop.close()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout=timeout + 5)
    return found


def ble_provision_esp32(device_address: str, wifi_ssid: str, wifi_password: str,
                        timeout: float = 35.0) -> str:
    """
    Verbind via BLE met een unprovisioned ESP32, stuur WiFi credentials,
    en wacht op de terug-gestuurde IP als "OK:<ip>".
    Geeft het IP-adres terug, of gooit een Exception bij fouten.
    """
    import asyncio
    import ipaddress
    import threading

    result_ip: list[str] = []
    exc_holder: list = [None]  # holds Exception | None

    def _parse_provision_message(data: bytes):
        msg = data.decode("utf-8", errors="ignore").strip()
        if msg.startswith("OK:"):
            candidate_ip = msg[3:].strip()
            try:
                ipaddress.ip_address(candidate_ip)
                return "ok", candidate_ip
            except Exception:
                return "err", f"ERR: Ongeldig IP ontvangen: {candidate_ip}"
        if msg.startswith("ERR"):
            return "err", msg
        return "ignore", msg

    async def _provision():
        from bleak import BleakClient

        received_event = asyncio.Event()
        error_msgs = []

        async with BleakClient(device_address, timeout=15.0) as client:
            def on_notify(characteristic, data):
                status, value = _parse_provision_message(data)
                if status == "ok":
                    result_ip.append(value)
                    received_event.set()
                elif status == "err":
                    error_msgs.append(value)
                    received_event.set()

            await client.start_notify(PROV_STATUS_UUID, on_notify)
            creds = f"{wifi_ssid}|{wifi_password}"
            await client.write_gatt_char(PROV_CRED_UUID, creds.encode("utf-8"), response=True)

            try:
                await asyncio.wait_for(received_event.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                raise TimeoutError("ESP32 heeft niet gereageerd (time-out).")

            await client.stop_notify(PROV_STATUS_UUID)

        if error_msgs:
            raise Exception(error_msgs[0])
        if not result_ip:
            raise Exception("Geen IP ontvangen van ESP32.")

    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_provision())
        except Exception as e:
            exc_holder[0] = e
        finally:
            loop.close()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout=timeout + 20)

    if exc_holder[0] is not None:
        raise exc_holder[0]
    if not result_ip:
        raise TimeoutError("Provisioning thread time-out.")
    return result_ip[0]


def wait_for_device_endpoint(device_ip, device_port=80, attempts=12, delay_s=3, timeout=4):
    """Wait until device endpoint responds with valid JSON payload."""
    last_error = None
    for _ in range(int(max(1, attempts))):
        try:
            return test_device_endpoint(device_ip, int(device_port), timeout=timeout)
        except Exception as exc:
            last_error = exc
            time.sleep(max(0.1, float(delay_s)))
    if last_error:
        raise last_error
    raise TimeoutError(f"Device {device_ip}:{device_port} not reachable")


def activate_live_device_connection(device_ip, device_port=80, timeout=5):
    """Test endpoint, persist connection, and switch dashboard to live mode."""
    endpoint, payload, normalized = test_device_endpoint(device_ip, int(device_port), timeout=timeout)
    save_connected_device(device_ip, int(device_port), endpoint)
    st.session_state.mode = 'Live'
    st.session_state.history_anchor_ts = pd.Timestamp.now().isoformat()
    st.session_state.pending_mode = None
    st.session_state.page = "Dashboard"
    return endpoint, payload, normalized


def scan_network_for_devices(subnet_base="192.168.1", timeout: float = 1.0, max_hosts=254):
    """Auto-discover ESP32 devices: only accepts responses with ESP32 JSON fields."""
    import requests
    import threading

    discovered = []
    lock = threading.Lock()
    ESP32_FIELDS = {"temperature", "speed", "energy"}  # minimale vingerafdruk

    def check_ip(ip):
        try:
            response = requests.get(f"http://{ip}:80/data", timeout=timeout)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if ESP32_FIELDS.issubset(data.keys()):
                        with lock:
                            discovered.append(ip)
                except Exception:
                    pass
        except Exception:
            pass

    threads = []
    host_count = max(1, min(int(max_hosts), 254))
    for i in range(1, host_count + 1):
        ip = f"{subnet_base}.{i}"
        thread = threading.Thread(target=check_ip, args=(ip,), daemon=True)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join(timeout=max(timeout * 3, 4))

    return discovered


def test_device_endpoint(device_ip, device_port, timeout=5):
    import requests

    endpoint = build_device_endpoint(device_ip, device_port)
    response = requests.get(endpoint, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    normalized = normalize_live_payload(payload)
    return endpoint, payload, normalized


def configure_live_layout_from_connections():
    """Set machine count and labels from connected ESP32 devices."""
    devices = st.session_state.get("connected_devices", [])
    device_count = len(devices)

    if device_count <= 0:
        return

    st.session_state.num_machines = device_count
    st.session_state.machine_names = [
        device.get("name") or f"ESP32 {index + 1}"
        for index, device in enumerate(devices)
    ]

    current_df = st.session_state.get("df")

    new_df = {}
    for index in range(1, device_count + 1):
        col = f"current_{index}"
        if isinstance(current_df, pd.DataFrame) and not current_df.empty and col in current_df.columns:
            new_df[col] = current_df[col].tail(100).astype(float).reset_index(drop=True)
        else:
            # Start live charts empty until first real ESP32 measurements arrive.
            new_df[col] = pd.Series(dtype="float64")

    st.session_state.df = pd.DataFrame(new_df)
    if isinstance(current_df, pd.DataFrame) and "timestamp" in current_df.columns:
        timestamp_series = pd.Series(pd.to_datetime(current_df["timestamp"], errors="coerce"))
        st.session_state.df["timestamp"] = timestamp_series.tail(len(st.session_state.df)).reset_index(drop=True)
    elif not st.session_state.df.empty:
        st.session_state.df["timestamp"] = pd.date_range(
            end=pd.Timestamp.now(),
            periods=len(st.session_state.df),
            freq=f"{int(st.session_state.refresh_rate)}s",
        )
    else:
        st.session_state.df["timestamp"] = pd.Series(dtype="datetime64[ns]")
    if not st.session_state.df.empty:
        st.session_state.last_current_values = {
            f"current_{index}": float(st.session_state.df[f"current_{index}"].iloc[-1])
            for index in range(1, device_count + 1)
        }
    else:
        st.session_state.last_current_values = {
            f"current_{index}": 0.5 for index in range(1, device_count + 1)
        }

    # Clear paused chart snapshots so charts immediately reflect the new shape.
    for chart_key in [
        "dashboard_realtime",
        "dashboard_distribution",
        "factory_analysis",
        "ai_table",
    ]:
        st.session_state[f"{chart_key}_snapshot"] = None


def save_connected_device(device_ip, device_port, endpoint):
    device_ip = str(device_ip).strip()
    device_port = int(device_port)
    device_name = f"ESP32 {device_ip.split('.')[-1]}"

    devices = st.session_state.get("connected_devices", [])
    existing_index = next(
        (index for index, device in enumerate(devices)
         if device.get("ip") == device_ip and int(device.get("port", 80)) == device_port),
        None,
    )

    device_record = {
        "ip": device_ip,
        "port": device_port,
        "endpoint": endpoint,
        "name": device_name,
    }
    if existing_index is None:
        devices.append(device_record)
    else:
        devices[existing_index] = device_record

    st.session_state.connected_devices = devices
    # Reset df so simulation history doesn't pollute live averages
    st.session_state.pop("df", None)
    st.session_state.pop("last_current_values", None)
    configure_live_layout_from_connections()

    # Legacy single-device fields kept for compatibility in existing UI pieces.
    st.session_state.device_ip = device_ip
    st.session_state.device_port = device_port
    st.session_state.device_endpoint = endpoint
    st.session_state.device_connected = len(st.session_state.connected_devices) > 0
    st.session_state.last_live_error = None
    st.session_state.show_disconnect_prompt = False
    st.session_state.last_connected_device = f"{device_ip}:{device_port}"
    log_event("Connection", f"Device connected - Endpoint: {endpoint}")


def has_connected_device():
    return len(st.session_state.get("connected_devices", [])) > 0


def clear_device_connection_state():
    st.session_state.connected_devices = []
    st.session_state.device_connected = False
    st.session_state.last_live_error = None
    st.session_state.show_disconnect_prompt = False
    st.session_state.history_anchor_ts = pd.Timestamp.now().isoformat()

    for key in [
        "device_endpoint",
        "device_ip",
        "device_port",
        "last_connected_device",
        "last_device_payload",
        "last_live_current",
        "last_voltage",
    ]:
        st.session_state.pop(key, None)


def disconnect_device(device_ip: str):
    """Remove a device from the connected list and reconfigure layout."""
    devices = st.session_state.get("connected_devices", [])
    devices = [d for d in devices if d.get("ip") != device_ip]
    if not devices:
        clear_device_connection_state()
        st.session_state.mode = "Simulation"
    else:
        st.session_state.connected_devices = devices
        st.session_state.device_connected = True
        primary_device = devices[0]
        st.session_state.device_ip = primary_device.get("ip")
        st.session_state.device_port = int(primary_device.get("port", 80))
        st.session_state.device_endpoint = primary_device.get("endpoint") or build_device_endpoint(
            primary_device.get("ip"),
            primary_device.get("port", 80),
        )
        configure_live_layout_from_connections()
    st.session_state.history_anchor_ts = pd.Timestamp.now().isoformat()
    log_event("Connection", f"Device disconnected: {device_ip}")


def get_local_subnet_candidates():
    import socket

    candidates = []
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()
        parts = local_ip.split(".")
        if len(parts) == 4:
            candidates.append(f"{parts[0]}.{parts[1]}.{parts[2]}")
    except Exception:
        pass

    candidates.extend(["192.168.68", "192.168.1", "192.168.0"])

    unique = []
    for subnet in candidates:
        if subnet not in unique:
            unique.append(subnet)
    return unique


def normalize_live_payload(payload):
    """Normalize arbitrary live payloads to current_1..current_N values."""
    machine_count = int(st.session_state.get("num_machines", 1))
    expected_keys = [f"current_{i}" for i in range(1, machine_count + 1)]

    if not isinstance(payload, dict) or not payload:
        raise ValueError("Invalid live payload: expected non-empty object")

    if "voltage" in payload and isinstance(payload.get("voltage"), (int, float)):
        st.session_state.last_voltage = float(payload["voltage"])

    if all(key in payload for key in expected_keys):
        return {
            key: float(np.clip(float(payload[key]), 0.5, 6.0))
            for key in expected_keys
        }

    if isinstance(payload.get("current"), (int, float)):
        return {"current_1": float(np.clip(float(payload["current"]), 0.5, 6.0))}

    esp32_keys = ["temperature", "speed", "energy"]
    if all(key in payload for key in esp32_keys):
        temp = float(payload["temperature"])
        speed = float(payload["speed"])
        energy = float(payload["energy"])

        mapped_values = [
            float(np.clip((temp - 15) / 65 * 3.5 + 0.5, 0.5, 4.0)),
            float(np.clip((speed - 500) / 2500 * 5.0 + 1.0, 1.0, 6.0)),
            float(np.clip(energy / 40.0, 0.5, 6.0)),
        ]

        if machine_count <= 1:
            return {"current_1": mapped_values[-1]}

        return {
            f"current_{index}": mapped_values[min(index - 1, len(mapped_values) - 1)]
            for index in range(1, machine_count + 1)
        }

    numeric_values = [
        float(value) for value in payload.values() if isinstance(value, (int, float))
    ]
    if numeric_values:
        return {
            f"current_{index}": float(np.clip(numeric_values[min(index - 1, len(numeric_values) - 1)], 0.5, 6.0))
            for index in range(1, machine_count + 1)
        }

    raise ValueError("Unsupported live payload received from device")


def build_live_fallback_row():
    """Return a stable fallback row from last known live values."""
    smoothed = st.session_state.get("smoothed_currents", {})
    last_values = st.session_state.get("last_current_values", {})
    machine_count = int(st.session_state.get("num_machines", 1))
    fallback = {}
    for index in range(1, machine_count + 1):
        key = f"current_{index}"
        candidate = smoothed.get(
            key,
            last_values.get(key, st.session_state.get("last_live_current", 0.5)),
        )
        fallback[key] = float(np.clip(float(candidate), 0.5, 6.0))
    return fallback


def get_connected_devices_from_state():
    """Resolve connected devices, including legacy single-device state."""
    devices = st.session_state.get("connected_devices", [])

    if not devices and st.session_state.get("device_ip"):
        devices = [{
            "ip": st.session_state.get("device_ip"),
            "port": int(st.session_state.get("device_port", 80)),
            "name": f"ESP32 {str(st.session_state.get('device_ip')).split('.')[-1]}",
        }]
        st.session_state.connected_devices = devices
        configure_live_layout_from_connections()

    return devices


def extract_device_current(payload, normalized):
    """Select the best current value for one connected device."""
    if isinstance(payload.get("current"), (int, float)):
        return float(np.clip(float(payload["current"]), 0.5, 6.0))
    if isinstance(payload.get("energy"), (int, float)):
        return float(np.clip(float(payload["energy"]) / 40.0, 0.5, 6.0))
    if normalized:
        return float(next(iter(normalized.values())))
    raise ValueError("No current value found in normalized payload")


def poll_connected_devices(timeout):
    """Poll all connected devices and return (row, success_count, errors)."""
    devices = get_connected_devices_from_state()
    if not devices:
        raise ValueError("No connected devices")

    row = {}
    errors = []
    latest_payload = None
    latest_endpoint = None
    successful_devices = 0

    for index, device in enumerate(devices, start=1):
        key = f"current_{index}"
        ip = device.get("ip")
        port = int(device.get("port", 80))

        try:
            endpoint, payload, normalized = test_device_endpoint(ip, port, timeout=timeout)
            value = extract_device_current(payload, normalized)
            row[key] = value

            if index == 1:
                st.session_state.last_live_current = value

            device["endpoint"] = endpoint
            latest_payload = payload
            latest_endpoint = endpoint
            successful_devices += 1
        except Exception as exc:
            previous = st.session_state.get("last_live_current") if index == 1 else None
            if previous is None:
                previous = st.session_state.get("last_current_values", {}).get(key, 0.5)
            row[key] = float(np.clip(float(previous), 0.5, 6.0))
            errors.append(f"{ip}:{port} -> {exc}")

    st.session_state.connected_devices = devices
    if latest_endpoint:
        st.session_state.device_endpoint = latest_endpoint
    if latest_payload is not None:
        st.session_state.last_device_payload = latest_payload

    return row, successful_devices, errors


CLOUD_BRIDGE_FILE = os.path.join(os.path.dirname(__file__), "cloud_latest.json")


def save_cloud_payload(payload):
    """Persist last received cloud payload for remote/live fallback."""
    try:
        record = {
            "timestamp": float(time.time()),
            "payload": payload,
        }
        with open(CLOUD_BRIDGE_FILE, "w", encoding="utf-8") as fh:
            json.dump(record, fh)
    except Exception as exc:
        print("Error saving cloud payload:", exc, file=sys.stderr)


def read_cloud_record():
    """Read raw cloud bridge record from disk."""
    if not os.path.exists(CLOUD_BRIDGE_FILE):
        return None
    try:
        with open(CLOUD_BRIDGE_FILE, "r", encoding="utf-8") as fh:
            record = json.load(fh)
        if isinstance(record, dict):
            return record
    except Exception:
        return None
    return None


def read_cloud_payload(max_age_s=300):
    """Return normalized live payload from cloud cache if it is still fresh."""
    record = read_cloud_record()
    if not record:
        return None

    ts = float(record.get("timestamp", 0.0))
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return None
    if time.time() - ts > float(max_age_s):
        return None

    try:
        normalized = normalize_live_payload(payload)
        return normalized, payload, ts
    except Exception:
        return None


def get_live_data():
    """Unified entry point for receiving simulation/live current data."""
    if st.session_state.mode == "Simulation":
        return get_simulated_data()

    timeout = float(st.session_state.get("connection_timeout", 5))

    try:
        row, successful_devices, errors = poll_connected_devices(timeout=timeout)
        st.session_state.device_connected = successful_devices > 0
        st.session_state.last_live_error = "; ".join(errors) if errors else None
        if successful_devices > 0:
            st.session_state.show_disconnect_prompt = False
        elif st.session_state.get("mode") == "Live":
            st.session_state.show_disconnect_prompt = True
        return row
    except Exception as exc:
        # Optional remote bridge fallback when local polling fails/off-LAN.
        if st.session_state.get("cloud_bridge_enabled", False):
            max_age_s = int(st.session_state.get("cloud_bridge_max_age_s", 300))
            cloud_data = read_cloud_payload(max_age_s=max_age_s)
            if cloud_data:
                normalized, payload, _ = cloud_data
                st.session_state.device_connected = True
                st.session_state.last_live_error = None
                st.session_state.last_device_payload = payload
                st.session_state.show_disconnect_prompt = False
                return normalized

        st.session_state.device_connected = False
        st.session_state.last_live_error = str(exc)
        if st.session_state.get("mode") == "Live":
            st.session_state.show_disconnect_prompt = True
        print("Error fetching live data:", exc, file=sys.stderr)
        return build_live_fallback_row()

# --- Safe defaults ---
if "anomalies" not in st.session_state:
    st.session_state.anomalies = []

if "bottlenecks" not in st.session_state:
    st.session_state.bottlenecks = []

if "event_history" not in st.session_state:
    st.session_state.event_history = []

# Helper function to log events
def log_event(event_type, message):
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event = {"timestamp": timestamp, "type": event_type, "message": message}
    st.session_state.event_history.insert(0, event)  # Add to beginning (newest first)
    # Keep only last 100 events
    if len(st.session_state.event_history) > 100:
        st.session_state.event_history = st.session_state.event_history[:100]

# Initialiseer dataframe — in live modus beginnen we leeg zodat nooit
# willekeurige simulatiedata de grafieken vervuilt.
if "df" not in st.session_state:
    data = {}
    is_live = (
        st.session_state.get('mode') == 'Live'
        and len(st.session_state.get('connected_devices', [])) > 0
    )
    for i in range(1, st.session_state.num_machines + 1):
        if is_live:
            data[f"current_{i}"] = []  # leeg — wordt gevuld door echte ESP32-data
        else:
            seed = np.random.uniform(1.5, 4.5)
            steps = np.random.normal(loc=0.0, scale=0.05, size=100)
            data[f"current_{i}"] = np.clip(seed + np.cumsum(steps), 0.5, 6.0)
    st.session_state.df = pd.DataFrame(data)
    if not is_live and not st.session_state.df.empty:
        st.session_state.df["timestamp"] = pd.date_range(
            end=pd.Timestamp.now(),
            periods=len(st.session_state.df),
            freq=f"{int(st.session_state.refresh_rate)}s",
        )
    else:
        st.session_state.df["timestamp"] = pd.Series(dtype="datetime64[ns]")

    if not is_live:
        st.session_state.last_current_values = {
            f"current_{i}": float(st.session_state.df[f"current_{i}"].iloc[-1])
            for i in range(1, st.session_state.num_machines + 1)
        }

df = st.session_state.df

NAV_ALLOWED_PAGES = {
    "Welcome",
    "Dashboard",
    "Factory Analysis",
    "Platform",
    "About",
    "Contact",
    "FAQ",
    "Support",
    "AI Insights",
    "Settings",
    "History",
    "Account",
}
SIDEBAR_HIDDEN_PAGES = {
    "Device Connection",
    "Welcome",
    "Platform",
    "About",
    "Contact",
    "FAQ",
    "Support",
    "Account",
}
DATA_REFRESH_PAGES = {"Dashboard", "Factory Analysis", "AI Insights", "History"}

DISPLAY_PAGE_LABELS = {
    "Welcome": "⌂ Welcome",
    "Dashboard": "⌗ Dashboard",
    "Factory Analysis": "⚒ Machine Overzicht",
    "Platform": "◈ Platform",
    "About": "◈ Over ons",
    "Contact": "◈ Contact",
    "FAQ": "◈ FAQ",
    "Support": "◈ Support",
    "AI Insights": "⌬ AI Insights",
    "History": "⚙ History",
    "Settings": "⚙ Settings",
    "Account": "👤 Account",
}


def apply_navigation_query_params():
    """Apply query-param based navigation and clear processed params."""
    query_params = st.query_params
    should_clear = False
    auth_token = query_params.get("auth")

    requested_page = query_params.get("page")
    if requested_page in NAV_ALLOWED_PAGES:
        st.session_state.page = requested_page
        should_clear = True

    shortcut = query_params.get("shortcut")
    if shortcut:
        should_clear = True
        if shortcut.startswith("page="):
            page_name = shortcut.split("=", 1)[1]
            if page_name in NAV_ALLOWED_PAGES:
                st.session_state.page = page_name
        elif shortcut == "action=toggle_language":
            st.session_state.language = 'NL' if st.session_state.get('language', 'EN') == 'EN' else 'EN'
        elif shortcut == "action=open_device_connection":
            st.session_state.page = "Device Connection"
            st.session_state.pending_mode = 'Live'
        elif shortcut == "action=logout":
            perform_logout()

    if should_clear:
        st.query_params.clear()
        if auth_token:
            st.query_params["auth"] = auth_token


def render_page_selector(current_page):
    """Render redesigned top navigation bar and return the active page."""

    if current_page in SIDEBAR_HIDDEN_PAGES:
        return current_page

    nav_items = [
        ("Dashboard", "⌗ " + t("Dashboard", "Dashboard")),
        ("Factory Analysis", "⚒ " + t("Machine Overview", "Machine Overzicht")),
        ("AI Insights", "⌬ " + t("AI Insights", "AI Inzichten")),
        ("History", "◷ " + t("History", "Geschiedenis")),
    ]

    st.markdown('<div class="top-nav-shell">', unsafe_allow_html=True)

    nav_cols = st.columns([1.4, 1.7, 1.5, 1.2, 0.08, 1.1, 1.0], gap="small")

    for idx, (page_name, label) in enumerate(nav_items):
        with nav_cols[idx]:
            is_active = current_page == page_name
            if st.button(
                label,
                key=f"top_nav_{page_name.replace(' ', '_').lower()}",
                width="stretch",
                type="primary" if is_active else "secondary",
                disabled=is_active,
            ):
                st.session_state.page = page_name
                st.rerun()

    with nav_cols[4]:
        st.markdown('<div class="top-nav-divider" style="margin: 6px auto;"></div>', unsafe_allow_html=True)

    with nav_cols[5]:
        settings_active = current_page == "Settings"
        if st.button(
            "⚙ " + t("Settings", "Instellingen"),
            key="top_nav_settings",
            width="stretch",
            type="primary" if settings_active else "secondary",
            disabled=settings_active,
            help=t("Open settings", "Open instellingen"),
        ):
            st.session_state.page = "Settings"
            st.rerun()

    with nav_cols[6]:
        if st.button(
            "+ " + t("Device", "Device"),
            key="top_nav_device_connect",
            width="stretch",
            type="secondary",
            help=t("Add device", "Apparaat toevoegen"),
        ):
            st.session_state.page = "Device Connection"
            st.session_state.pending_mode = 'Live'
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    return st.session_state.page


def render_platform_sidebar_nav():
    """Custom fixed right-side nav panel — no Streamlit sidebar used."""
    current = st.session_state.get("page", "Platform")

    active_platform = " pnav-active" if current == "Platform" else ""
    active_about = " pnav-active" if current == "About" else ""
    active_contact = " pnav-active" if current == "Contact" else ""
    active_faq = " pnav-active" if current == "FAQ" else ""
    active_support = " pnav-active" if current == "Support" else ""
    active_account = " pnav-active" if current == "Account" else ""
    auth_token = str(st.query_params.get("auth", "") or "").strip()
    auth_suffix = f"&auth={auth_token}" if auth_token else ""

    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarCollapseButton"] {{
            display: none !important;
        }}
        [data-testid="stAppViewContainer"] > section.main {{
            margin-left: 0 !important;
            padding-right: 0 !important;
        }}
        .pnav-hamburger {{
            position: fixed;
            right: 16px;
            top: 58px;
            z-index: 10001;
            width: 58px;
            height: 58px;
            background: linear-gradient(135deg, #1d4ed8 0%, #0f766e 100%);
            border: 2px solid #3b82f6;
            border-radius: 14px;
            box-shadow: 0 4px 24px rgba(59,130,246,0.55), 0 2px 8px rgba(0,0,0,0.4);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: right 0.3s cubic-bezier(0.4,0,0.2,1), box-shadow 0.2s;
            user-select: none;
        }}
        .pnav-hamburger:hover {{
            box-shadow: 0 6px 32px rgba(59,130,246,0.8), 0 2px 12px rgba(0,0,0,0.5);
        }}
        .pnav-hamburger-icon {{
            display: block;
            width: 24px;
            height: 3px;
            background: #fff;
            border-radius: 3px;
            box-shadow: 0 8px 0 #fff, 0 16px 0 #fff;
            margin-top: -8px;
            pointer-events: none;
        }}
        .pnav-panel {{
            position: fixed;
            right: -260px;
            top: 0;
            height: 100vh;
            width: 240px;
            background: #0b1220;
            border-left: 1px solid #1e293b;
            z-index: 10000;
            padding: 28px 14px;
            box-shadow: -6px 0 30px rgba(0,0,0,0.55);
            transition: right 0.3s cubic-bezier(0.4,0,0.2,1);
            overflow-y: auto;
        }}
        #pnav-toggle:checked ~ .pnav-panel {{
            right: 0;
        }}
        #pnav-toggle:checked ~ .pnav-hamburger {{
            right: 252px;
        }}
        .pnav-panel-title {{
            font-size: 1rem;
            font-weight: 800;
            color: #f8fafc;
            margin: 0 0 18px 0;
            padding-bottom: 12px;
            border-bottom: 1px solid #1e293b;
            letter-spacing: 0.04em;
        }}
        .pnav-item {{
            display: block;
            color: #dbeafe;
            text-decoration: none;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 10px 14px;
            margin-bottom: 8px;
            font-weight: 600;
            font-size: 0.95rem;
            transition: background 0.15s, border-color 0.15s;
        }}
        .pnav-item:hover {{
            background: #273549;
            border-color: #60a5fa;
            color: #f8fafc;
        }}
        .pnav-item.pnav-active {{
            background: linear-gradient(135deg, #1d4ed8, #0f766e);
            border-color: #3b82f6;
            color: #fff;
            cursor: default;
            pointer-events: none;
        }}
        .pnav-account {{
            margin-top: 14px;
            border: 1px solid #334155;
            background: linear-gradient(180deg, rgba(15,23,42,0.95) 0%, rgba(17,24,39,0.95) 100%);
            border-radius: 12px;
            padding: 12px;
        }}
        .pnav-account-title {{
            color: #f8fafc;
            font-size: 0.9rem;
            font-weight: 800;
            margin: 0 0 8px 0;
        }}
        .pnav-account-row {{
            color: #cbd5e1;
            font-size: 0.82rem;
            margin: 4px 0;
        }}
        .pnav-chip-wrap {{
            margin-top: 8px;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}
        .pnav-chip {{
            padding: 2px 8px;
            border-radius: 999px;
            border: 1px solid #334155;
            background: #1e293b;
            color: #dbeafe;
            font-size: 0.72rem;
            font-weight: 700;
        }}
        </style>
        <input type="checkbox" id="pnav-toggle" style="display:none">
        <label for="pnav-toggle" class="pnav-hamburger" title="{t('Menu', 'Menu')}">
            <span class="pnav-hamburger-icon"></span>
        </label>
        <div class="pnav-panel">
            <div class="pnav-panel-title">{t('Smart Factory Suite', 'Smart Factory Suite')}</div>
            <a href="?page=Platform{auth_suffix}" target="_self" class="pnav-item{active_platform}">◈ {t('Platform', 'Platform')}</a>
            <a href="?page=About{auth_suffix}" target="_self" class="pnav-item{active_about}">{t('About us', 'Over ons')}</a>
            <a href="?page=Contact{auth_suffix}" target="_self" class="pnav-item{active_contact}">{t('Contact', 'Contact')}</a>
            <a href="?page=FAQ{auth_suffix}" target="_self" class="pnav-item{active_faq}">FAQ</a>
            <a href="?page=Support{auth_suffix}" target="_self" class="pnav-item{active_support}">{t('Support', 'Support')}</a>
            <a href="?page=Account{auth_suffix}" target="_self" class="pnav-item{active_account}">👤 {t('Account', 'Account')}</a>

        </div>
        """,
        unsafe_allow_html=True,
    )


def resolve_page_state():
    """Resolve page state, including guards that require an active device."""
    if "page" not in st.session_state:
        st.session_state.page = "Welcome"

    apply_navigation_query_params()
    page = render_page_selector(st.session_state.page)

    # Legacy route: Home bestaat niet meer, stuur door naar Welcome.
    if page == "Home":
        st.session_state.page = "Welcome"
        page = "Welcome"

    # Welkomscherm slechts één keer tonen
    if page == "Welcome" and st.session_state.get('welcome_shown', False):
        st.session_state.page = "Dashboard"
        page = "Dashboard"

    connection_prompt_required = False
    live_requested = (
        st.session_state.get("mode") == "Live"
        or st.session_state.get("pending_mode") == "Live"
    )
    if page == "Dashboard" and live_requested and not has_connected_device():
        st.session_state.page = "Device Connection"
        st.session_state.pending_mode = 'Live'
        page = "Device Connection"
        connection_prompt_required = True

    return page, connection_prompt_required


def ensure_monitoring_df():
    """Keep dataframe schema stable so charts always have valid inputs."""
    machine_count = int(st.session_state.get("num_machines", 3))
    df_local = st.session_state.get("df", pd.DataFrame())

    if not isinstance(df_local, pd.DataFrame) or df_local.empty:
        seed = {f"current_{i}": [0.0] for i in range(1, machine_count + 1)}
        df_local = pd.DataFrame(seed)
        df_local["timestamp"] = [pd.Timestamp.now()]
    else:
        for i in range(1, machine_count + 1):
            col = f"current_{i}"
            if col not in df_local.columns:
                df_local[col] = 0.0
            df_local[col] = pd.to_numeric(df_local[col], errors="coerce").fillna(0.0)

        if "timestamp" not in df_local.columns:
            df_local["timestamp"] = pd.date_range(
                end=pd.Timestamp.now(),
                periods=len(df_local),
                freq=f"{max(1, int(st.session_state.get('refresh_rate', 1)))}s",
            )
        else:
            parsed_ts = pd.to_datetime(df_local["timestamp"], errors="coerce")
            df_local["timestamp"] = parsed_ts.fillna(pd.Timestamp.now())

    st.session_state.df = df_local.tail(100).reset_index(drop=True)
    return st.session_state.df


def refresh_data_frame(active_page):
    """Refresh monitoring dataframe on pages that need live/simulated updates."""
    import time

    ensure_monitoring_df()

    if active_page in DATA_REFRESH_PAGES:
        poll_s = max(1, int(st.session_state.refresh_rate))
        now_ts = time.time()
        last_poll_ts = float(st.session_state.get("last_data_poll_ts", 0.0))
        has_target = bool(st.session_state.get("target_currents"))
        should_poll = (now_ts - last_poll_ts >= poll_s) or not has_target

        if should_poll:
            polled_row = get_live_data()
            st.session_state.target_currents = {
                key: float(value)
                for key, value in polled_row.items()
                if str(key).startswith("current_")
            }
            st.session_state.last_data_poll_ts = now_ts

        target_row = st.session_state.get("target_currents", {})
        if target_row:
            if st.session_state.get("mode") == "Live":
                display_row = {
                    key: float(value)
                    for key, value in target_row.items()
                    if str(key).startswith("current_")
                }
            else:
                display_row = smooth_current_row(target_row)
            if "current_1" in display_row:
                st.session_state.last_live_current = float(display_row["current_1"])
            st.session_state.last_current_values = {
                key: float(value)
                for key, value in display_row.items()
                if str(key).startswith("current_")
            }
            machine_count = int(st.session_state.get("num_machines", 3))
            row_values = {}
            for i in range(1, machine_count + 1):
                col = f"current_{i}"
                fallback_value = st.session_state.last_current_values.get(col, 0.0)
                row_values[col] = float(display_row.get(col, fallback_value))

            row_with_timestamp = {**row_values, "timestamp": pd.Timestamp.now()}
            st.session_state.df = pd.concat(
                [st.session_state.df, pd.DataFrame([row_with_timestamp])],
                ignore_index=True,
            )

    st.session_state.df = st.session_state.df.tail(100).reset_index(drop=True)
    ensure_monitoring_df()

    return st.session_state.df


def build_client_realtime_component_html(machine_names, endpoints, mode, refresh_seconds, panel_title, show_metrics=True, initial_history=None):
    """Return an HTML app that updates values and Plotly charts client-side."""
    color_scale = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#ec4899', '#84cc16', '#a78bfa']
    initial_history = initial_history or {"times": [], "series": {}}
    config = {
        "machineNames": list(machine_names),
        "endpoints": list(endpoints),
        "mode": str(mode),
        "refreshMs": int(max(1, refresh_seconds) * 1000),
        "animationMs": int(st.session_state.get("animation_tick_ms", 300)),
        "panelTitle": str(panel_title),
        "showMetrics": bool(show_metrics),
        "colors": color_scale,
        "initialHistory": initial_history,
        "initialSnapshot": (initial_history or {}).get("snapshot", {}),
        "initialVoltage": (initial_history or {}).get("voltage"),
    }
    config_json = json.dumps(config)

    return f"""
        <div id="rt-root" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color:#f1f5f9;">
            <div id="rt-metrics" style="display:{'grid' if show_metrics else 'none'}; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin:0 0 18px 0;"></div>
            <div style="margin:0 0 10px 0; font-size:1.1rem; font-weight:700; color:#f8fafc;">{panel_title}</div>
            <div id="rt-gauges" style="width:100%; min-height:320px;"></div>
            <div style="margin:18px 0 10px 0; font-size:1.1rem; font-weight:700; color:#f8fafc;">Stroom Over Tijd</div>
            <div id="rt-trend" style="width:100%; min-height:420px; background:#0f172a; border:1px solid #1e293b; border-radius:14px; padding:8px;"></div>
        </div>
        <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
        <script>
            const config = {config_json};
            const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
            const machineNames = config.machineNames;
            const endpoints = config.endpoints;
            const colors = config.colors;
            const maxPoints = 100;
            const initialHistory = config.initialHistory || {{ times: [], series: {{}} }};
            const targetValues = Object.fromEntries(machineNames.map((name) => [name, 0.5]));
            const displayValues = Object.fromEntries(machineNames.map((name) => [name, 0.5]));
            const historySeries = Object.fromEntries(machineNames.map((name) => [name, [...(initialHistory.series?.[name] || [])] ]));
            const historyTimes = [...(initialHistory.times || [])];
            let lastVoltage = config.initialVoltage ?? null;

            function formatClockTime(value) {{
                if (!value) return '';
                if (typeof value === 'string' && /^\\d{{2}}:\\d{{2}}(:\\d{{2}})?$/.test(value)) {{
                    return value.length === 5 ? `${{value}}:00` : value;
                }}
                const parsed = new Date(value);
                if (!Number.isNaN(parsed.getTime())) {{
                    return parsed.toLocaleTimeString('nl-NL', {{ hour12: false }});
                }}
                return String(value);
            }}

            machineNames.forEach((name) => {{
                const initialSnapshotValue = config.initialSnapshot?.[name];
                if (typeof initialSnapshotValue === 'number' && Number.isFinite(initialSnapshotValue)) {{
                    targetValues[name] = initialSnapshotValue;
                    displayValues[name] = initialSnapshotValue;
                }}
                const seeded = historySeries[name];
                if (seeded.length) {{
                    const latest = seeded[seeded.length - 1];
                    targetValues[name] = latest;
                    displayValues[name] = latest;
                }}
            }});

            function extractCurrent(payload) {{
                if (payload && typeof payload.current === 'number') return clamp(payload.current, 0.5, 6.0);
                if (payload && typeof payload.energy === 'number') return clamp(payload.energy / 40.0, 0.5, 6.0);
                const numericValues = Object.values(payload || {{}}).filter((value) => typeof value === 'number');
                if (numericValues.length) return clamp(numericValues[0], 0.5, 6.0);
                return 0.5;
            }}

            function buildMetricCard(label, value) {{
                return `
                    <div style="background:#1e293b;border:1px solid #334155;border-radius:14px;padding:14px 16px;">
                        <div style="font-size:0.8rem;color:#94a3b8;margin-bottom:6px;">${{label}}</div>
                        <div style="font-size:1.25rem;font-weight:700;color:#f8fafc;">${{value}}</div>
                    </div>
                `;
            }}

            function renderMetrics() {{
                if (!config.showMetrics) return;
                const values = machineNames.map((name) => displayValues[name] || 0);
                const avg = values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : 0;
                const peak = values.length ? Math.max(...values) : 0;
                const min = values.length ? Math.min(...values) : 0;
                const metricsEl = document.getElementById('rt-metrics');
                const cards = [
                    buildMetricCard('Avg Load', `${{avg.toFixed(2)}} A`),
                    buildMetricCard('Peak Load', `${{peak.toFixed(2)}} A`),
                    buildMetricCard('Min Load', `${{min.toFixed(2)}} A`),
                ];
                if (lastVoltage !== null && Number.isFinite(lastVoltage)) cards.push(buildMetricCard('Voltage', `${{lastVoltage.toFixed(2)}} V`));
                metricsEl.innerHTML = cards.join('');
            }}

            function renderGauges() {{
                const perRow = Math.min(machineNames.length || 1, 5);
                const rows = Math.ceil((machineNames.length || 1) / perRow);
                const gapX = perRow <= 2 ? 0.05 : 0.03;
                const gapY = 0.05;
                const data = machineNames.map((name, index) => {{
                    const col = index % perRow;
                    const row = Math.floor(index / perRow);
                    const x0 = col / perRow + gapX;
                    const x1 = (col + 1) / perRow - gapX;
                    const y0 = ((rows - 1 - row) / rows) + gapY;
                    const y1 = ((rows - row) / rows) - gapY;
                    return {{
                        type: 'indicator',
                        mode: 'gauge+number',
                        value: displayValues[name] || 0,
                        title: {{ text: name, font: {{ size: 13, color: '#f1f5f9' }} }},
                        number: {{ suffix: ' A', font: {{ size: 22, color: colors[index % colors.length], family: 'monospace' }} }},
                        gauge: {{ axis: {{ range: [0, 8] }}, bar: {{ color: colors[index % colors.length], thickness: 0.28 }}, bgcolor: '#1e293b', borderwidth: 0 }},
                        domain: {{ x: [x0, x1], y: [y0, y1] }},
                    }};
                }});
                Plotly.react('rt-gauges', data, {{
                    paper_bgcolor: '#0f172a',
                    plot_bgcolor: '#0f172a',
                    font: {{ color: '#f1f5f9' }},
                    margin: {{ l: 10, r: 10, t: 10, b: 10 }},
                    height: 230 * rows,
                }}, {{ displayModeBar: false, responsive: true }});
            }}

            function renderTrend() {{
                const root = document.getElementById('rt-trend');
                const width = Math.max(280, (root.clientWidth || 0) - 16);
                const isCompact = width < 520;
                const height = config.showMetrics ? (isCompact ? 340 : 410) : (isCompact ? 300 : 360);
                const formattedTimes = historyTimes.map((label) => formatClockTime(label));
                const maxTicks = isCompact ? 4 : 6;
                const tickValues = [];
                if (formattedTimes.length <= maxTicks) {{
                    tickValues.push(...formattedTimes);
                }} else {{
                    for (let i = 0; i < maxTicks; i += 1) {{
                        const pos = Math.round((i * (formattedTimes.length - 1)) / (maxTicks - 1));
                        tickValues.push(formattedTimes[pos]);
                    }}
                }}
                const traces = machineNames.map((name, index) => {{
                    const color = colors[index % colors.length];
                    return {{
                        x: formattedTimes,
                        y: historySeries[name] || [],
                        type: 'scatter',
                        mode: 'lines+markers',
                        name,
                        line: {{ width: 3, color, shape: 'linear' }},
                        marker: {{ size: isCompact ? 5 : 6, color }},
                        hovertemplate: `${{name}}<br>Tijd: %{{x}}<br>Stroom: %{{y:.2f}} A<extra></extra>`,
                    }};
                }});

                Plotly.react(root, traces, {{
                    template: 'plotly_dark',
                    height,
                    margin: {{ l: isCompact ? 52 : 62, r: 20, t: 22, b: isCompact ? 68 : 54 }},
                    paper_bgcolor: '#0f172a',
                    plot_bgcolor: '#0f172a',
                    hovermode: 'x unified',
                    hoverlabel: {{
                        bgcolor: '#111827',
                        bordercolor: '#334155',
                        font: {{ color: '#f8fafc', size: 12 }},
                    }},
                    legend: {{
                        orientation: 'h',
                        yanchor: 'bottom',
                        y: 1.03,
                        xanchor: 'left',
                        x: 0,
                        font: {{ size: 12, color: '#e2e8f0' }},
                        bgcolor: 'rgba(15,23,42,0.55)',
                        bordercolor: 'rgba(148,163,184,0.22)',
                        borderwidth: 1,
                    }},
                    xaxis: {{
                        title: {{ text: 'Tijd', font: {{ size: 13, color: '#f8fafc' }} }},
                        categoryorder: 'array',
                        categoryarray: formattedTimes,
                        tickmode: 'array',
                        tickvals: tickValues,
                        tickfont: {{ size: 12, color: '#dbeafe' }},
                        tickangle: isCompact ? -18 : 0,
                        showgrid: true,
                        gridcolor: 'rgba(148,163,184,0.12)',
                        linecolor: 'rgba(148,163,184,0.38)',
                        zeroline: false,
                    }},
                    yaxis: {{
                        title: {{ text: 'Stroom (A)', font: {{ size: 13, color: '#f8fafc' }} }},
                        range: [0, 8],
                        dtick: 1,
                        tickfont: {{ size: 12, color: '#dbeafe' }},
                        showgrid: true,
                        gridcolor: 'rgba(148,163,184,0.22)',
                        zeroline: true,
                        zerolinecolor: 'rgba(148,163,184,0.40)',
                        linecolor: 'rgba(148,163,184,0.38)',
                    }},
                }}, {{ displayModeBar: false, responsive: true, displaylogo: false }});
            }}

            window.addEventListener('resize', () => {{
                renderTrend();
                renderGauges();
            }});

            function pushHistory() {{
                const now = formatClockTime(new Date().toISOString());
                historyTimes.push(now);
                if (historyTimes.length > maxPoints) historyTimes.shift();
                machineNames.forEach((name) => {{
                    const hasHistory = (historySeries[name] || []).length > 0;
                    const valueToPush = config.mode === 'Live'
                        ? (targetValues[name] || displayValues[name] || 0.5)
                        : (hasHistory ? (displayValues[name] || targetValues[name] || 0.5) : (targetValues[name] || displayValues[name] || 0.5));
                    historySeries[name].push(valueToPush);
                    if (historySeries[name].length > maxPoints) historySeries[name].shift();
                }});
            }}

            function nextSimulationValue(name, index) {{
                const base = targetValues[name] || (1.2 + index * 0.35);
                const delta = (Math.random() - 0.5) * 0.6;
                return clamp(base + delta, 0.5, 6.0);
            }}

            async function pollTargets() {{
                if (config.mode === 'Simulation') {{
                    machineNames.forEach((name, index) => {{
                        targetValues[name] = nextSimulationValue(name, index);
                    }});
                    lastVoltage = null;
                    return;
                }}

                if (config.mode === 'Live') {{
                    return;
                }}

                if (!endpoints.length) {{
                    return;
                }}

                const responses = await Promise.all(endpoints.map(async (endpoint) => {{
                    try {{
                        const response = await fetch(endpoint, {{ cache: 'no-store' }});
                        if (!response.ok) throw new Error(`HTTP ${{response.status}}`);
                        return await response.json();
                    }} catch (error) {{
                        return null;
                    }}
                }}));

                machineNames.forEach((name, index) => {{
                    const payload = responses[index];
                    if (payload) {{
                        targetValues[name] = extractCurrent(payload);
                        if (typeof payload.voltage === 'number') lastVoltage = payload.voltage;
                    }}
                }});
            }}

            function animateStep() {{
                machineNames.forEach((name) => {{
                    const current = displayValues[name] || 0;
                    const target = targetValues[name] || 0;
                    if (config.mode === 'Live') {{
                        displayValues[name] = target;
                        return;
                    }}
                    const delta = target - current;
                    const maxStep = 0.45;
                    const eased = delta * 0.35;
                    const step = Math.abs(eased) > maxStep ? Math.sign(eased) * maxStep : eased;
                    displayValues[name] = Math.abs(delta) < 0.01 ? target : current + step;
                }});
                renderMetrics();
                renderGauges();
            }}

            async function pollAndRender() {{
                await pollTargets();
                pushHistory();
                renderMetrics();
                renderGauges();
                renderTrend();
            }}

            renderMetrics();
            renderGauges();
            renderTrend();
            pollAndRender();
            window.setInterval(pollAndRender, config.refreshMs);
            window.setInterval(animateStep, config.animationMs);
        </script>
        """


def render_client_realtime_panel(machine_names, panel_title, show_metrics=True):
    """Render a client-side realtime panel that updates without Streamlit reruns."""
    connected_devices = st.session_state.get("connected_devices", [])
    current_df = st.session_state.get("df", pd.DataFrame())
    endpoint_by_name = {}
    for index, device in enumerate(connected_devices):
        device_name = device.get("name") or (
            st.session_state.machine_names[index]
            if index < len(st.session_state.machine_names)
            else f"ESP32 {index + 1}"
        )
        endpoint_by_name[device_name] = device.get("endpoint") or build_device_endpoint(
            device.get("ip"),
            device.get("port", 80),
        )

    endpoints = []
    if st.session_state.get("mode") != "Live":
        for machine_name in machine_names:
            endpoint = endpoint_by_name.get(machine_name)
            if endpoint:
                endpoints.append(endpoint)

    initial_history = {
        "times": [],
        "series": {name: [] for name in machine_names},
        "snapshot": {},
        "voltage": st.session_state.get("last_voltage"),
    }

    filtered_df = current_df
    history_anchor_ts = st.session_state.get("history_anchor_ts")
    if isinstance(current_df, pd.DataFrame) and not current_df.empty and history_anchor_ts and "timestamp" in current_df.columns:
        timestamp_series = pd.to_datetime(current_df["timestamp"], errors="coerce")
        filtered_df = current_df.loc[timestamp_series >= pd.to_datetime(history_anchor_ts, errors="coerce")].copy()

    if isinstance(filtered_df, pd.DataFrame) and not filtered_df.empty:
        if "timestamp" in filtered_df.columns:
            initial_history["times"] = [
                pd.to_datetime(timestamp).strftime("%H:%M:%S")
                for timestamp in filtered_df["timestamp"].tolist()
                if not pd.isna(timestamp)
            ]

        for machine_name in machine_names:
            machine_index = next(
                (index + 1 for index, name in enumerate(st.session_state.machine_names) if name == machine_name),
                None,
            )
            if machine_index is None:
                continue
            column_name = f"current_{machine_index}"
            if column_name in filtered_df.columns:
                series_values = pd.to_numeric(filtered_df[column_name], errors="coerce").dropna().tolist()
                initial_history["series"][machine_name] = [float(value) for value in series_values]
                if series_values:
                    initial_history["snapshot"][machine_name] = float(series_values[-1])

    html = build_client_realtime_component_html(
        machine_names=machine_names,
        endpoints=endpoints,
        mode=st.session_state.get("mode", "Simulation"),
        refresh_seconds=max(1, int(st.session_state.get("refresh_rate", 2))),
        panel_title=panel_title,
        show_metrics=show_metrics,
        initial_history=initial_history,
    )
    rows = max(1, (len(machine_names) + min(len(machine_names), 5) - 1) // max(1, min(len(machine_names), 5)))
    base_height = 980 if show_metrics else 780
    components.html(html, height=base_height + (rows - 1) * 190, scrolling=False)

# --- Navigation ---
restore_auth_from_query_token()

# Determine page before login check so we can require login for specific pages
page, connection_prompt_required = resolve_page_state()

# Pages that require login
PROTECTED_PAGES = {"Dashboard", "Factory Analysis"}

# If trying to access a protected page without being logged in, show login dialog
if page in PROTECTED_PAGES and not st.session_state.get("auth_user"):
    st.title(t("Login Required", "Inloggen Vereist"))
    st.markdown(
        f"""
        <div class="page-hero">
            <p class="page-hero-title">{t('Access Denied', 'Toegang Geweigerd')}</p>
            <p class="page-hero-sub">{t('This page requires you to be logged in. Please log in with your account.', 'Deze pagina vereist dat je bent ingelogd. Log in met je account.')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs([
        t("Login", "Inloggen"),
        t("Create Account", "Account Maken"),
    ])

    with login_tab:
        login_user = st.text_input(t("Username", "Gebruikersnaam"), key="auth_login_user")
        login_pass = st.text_input(t("Password", "Wachtwoord"), type="password", key="auth_login_pass")
        if st.button(t("Login", "Inloggen"), key="auth_login_btn", type="primary", width="stretch"):
            if authenticate_user(login_user, login_pass):
                st.session_state.auth_user = login_user.strip().lower()
                st.session_state.auth_loaded_user = st.session_state.auth_user
                remember_token = set_user_remember_token(st.session_state.auth_user)
                if remember_token:
                    st.query_params["auth"] = remember_token
                db = load_user_db()
                user_state = db.get("users", {}).get(st.session_state.auth_user, {}).get("state", {})
                apply_user_state(user_state)
                send_login_email(st.session_state.auth_user)
                st.success(t("Login successful.", "Inloggen gelukt."))
                st.rerun()
            else:
                st.error(t("Invalid username or password.", "Onjuiste gebruikersnaam of wachtwoord."))

    with register_tab:
        st.write(t("Create your account and fill in your profile details.", "Maak je account en vul je profielgegevens in."))
        st.divider()
        
        # Account credentials
        st.subheader(t("Account", "Account"))
        reg_user = st.text_input(t("Username", "Gebruikersnaam"), key="auth_register_user")
        reg_pass = st.text_input(t("Password (min 6 chars)", "Wachtwoord (min 6 tekens)"), type="password", key="auth_register_pass")
        
        st.divider()
        
        # Profile details
        st.subheader("👤 " + t("Profile", "Profiel"))
        prof_name = st.text_input(t("Full name", "Volledig naam"), key="auth_register_name")
        prof_email = st.text_input(t("Email", "E-mail"), key="auth_register_email")
        prof_company = st.text_input(t("Company", "Bedrijf"), key="auth_register_company")
        
        st.divider()
        
        if st.button(t("Create Account", "Account Aanmaken"), key="auth_register_btn", type="primary", width="stretch"):
            ok, message = register_user(reg_user, reg_pass, prof_name, prof_email, prof_company)
            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    st.stop()

# Show login page if not logged in (for non-protected pages, allow browsing as guest)
# Login/register UI is only shown on protected pages that require auth


if st.session_state.get("auth_user") and st.session_state.get("auth_loaded_user") != st.session_state.get("auth_user"):
    db = load_user_db()
    user_state = db.get("users", {}).get(st.session_state.get("auth_user"), {}).get("state", {})
    apply_user_state(user_state)
    st.session_state.auth_loaded_user = st.session_state.get("auth_user")

# Remember where to return when leaving Device Connection.
if page != "Device Connection":
    st.session_state.last_non_device_page = page

# --- Scroll to top on page change ---
if st.session_state.get('_last_page') != page:
    st.session_state._last_page = page
    components.html(
        """
        <script>
        function scrollToTop() {
            var el = window.parent.document.getElementById('page-top-anchor');
            if (el) { el.scrollIntoView({behavior: 'instant', block: 'start'}); }
        }
        scrollToTop();
        setTimeout(scrollToTop, 100);
        setTimeout(scrollToTop, 400);
        </script>
        """,
        height=0,
    )
st.markdown('<div id="page-top-anchor"></div>', unsafe_allow_html=True)

if (
    st.session_state.get("mode") == "Live"
    and st.session_state.get("show_disconnect_prompt", False)
    and page != "Device Connection"
):
    _, modal_col, _ = st.columns([1, 2, 1])
    with modal_col:
        st.markdown(
            """
            <div class="disconnect-modal">
                <p class="disconnect-title">Device verbinding verloren</p>
                <p class="disconnect-sub">De ESP32 stuurt geen live data meer. Kies direct wat je wilt doen.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        action_col1, action_col2 = st.columns(2)
        with action_col1:
            if st.button("Ga naar Simulation Mode", key="disconnect_to_simulation", type="primary", width="stretch"):
                clear_device_connection_state()
                st.session_state.mode = "Simulation"
                st.session_state.pending_mode = None
                st.session_state.page = "Dashboard"
                st.rerun()
        with action_col2:
            if st.button("Reconnect Device", key="disconnect_reconnect", type="secondary", width="stretch"):
                st.session_state.show_disconnect_prompt = False
                st.session_state.page = "Device Connection"
                st.session_state.pending_mode = "Live"
                st.rerun()
    st.stop()

# --- Live refresh control ---
# Removed global pause_updates - now only per-chart controls

# Per-chart local pause state and chart snapshots
chart_keys = [
    'dashboard_realtime',
    'dashboard_distribution',
    'factory_analysis',
    'ai_table'  # Add AI table pause state
]
for ck in chart_keys:
    if f'pause_{ck}' not in st.session_state:
        st.session_state[f'pause_{ck}'] = False
    if f'{ck}_snapshot' not in st.session_state:
        st.session_state[f'{ck}_snapshot'] = None

df = st.session_state.df

# Auto-refresh: herlaad de pagina op data-pagina's zodat Python-metrics
# (bar chart, gemiddelden, snapshot) ook met live ESP32-data worden bijgewerkt.
if page in DATA_REFRESH_PAGES:
    _refresh_ms = max(1000, int(st.session_state.get("refresh_rate", 2) * 1000))
    st_autorefresh(interval=_refresh_ms, key="data_autorefresh")
    df = refresh_data_frame(page)

if page == "Welcome":
    st.title("⌂ Welkom")
    st.markdown(
        """
        <div class="page-hero">
            <p class="page-hero-title">Smart Factory Monitoring Platform</p>
            <p class="page-hero-sub">Dit platform helpt operators, maintenance teams en productiecoordinatie om machineprestaties in realtime te monitoren, afwijkingen vroeg te signaleren en onderhoud beter te plannen.</p>
            <span class="page-chip">Realtime monitoring</span>
            <span class="page-chip">AI analyse</span>
            <span class="page-chip">Device onboarding</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Wie Wij Zijn")
    col_about_a, col_about_b = st.columns(2)
    with col_about_a:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### Missie")
        st.markdown(
            "Productieteams helpen met duidelijke, betrouwbare en direct bruikbare machine-inzichten."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_about_b:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### Visie")
        st.markdown(
            "Van reactief onderhoud naar voorspelbaar en datagedreven sturen op capaciteit, uptime en kwaliteit."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Wat Wij Doen")
    st.markdown("""
    - Verzamelen van live machinegegevens via ESP32-devices
    - Visualiseren van stroom- en prestatiegegevens in overzichtelijke dashboards
    - Detecteren van afwijkingen en operationele knelpunten
    - Ondersteunen van beslissingen met AI-analyses en aanbevelingen
    - Vastleggen van gebeurtenissen voor analyse, audits en opvolging
    """)

    st.subheader("Organisatie En Team")
    col_team_a, col_team_b = st.columns(2)
    with col_team_a:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### Voor Wie")
        st.markdown("Operators, technische dienst, productieleiding en procesverbetering.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_team_b:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### Werkwijze")
        st.markdown("Kleine stappen, snelle feedback en continue verbetering op basis van meetdata.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Wat Je In Het Platform Ziet")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### Dashboard")
        st.markdown("Realtime trends, gemiddelde belasting, pieken en actuele status per machine.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### Machine Overzicht")
        st.markdown("Vergelijking tussen machines, trendanalyse en prestatieverschillen over tijd.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### AI Insights")
        st.markdown("Automatische signalering van anomalieen, bottlenecks en aanbevelingen per machine.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### History")
        st.markdown("Logboek van gebeurtenissen, connecties en afwijkingen voor analyse en rapportage.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Support En Contact")
    st.markdown("""
    - Device onboarding: via `+ Device Connect` in de bovenbalk
    - Technische support: controleer eerst Device Connection en History
    - Operationele vragen: gebruik Dashboard en AI Insights als startpunt voor diagnose
    """)

    st.subheader("Aan De Slag")
    st.markdown("""
    1. Voeg een device toe via `+ Device Connect` in de bovenbalk.
    2. Controleer of Live mode actief is en data binnenkomt.
    3. Gebruik Dashboard, Machine Overzicht en AI Insights voor monitoring en optimalisatie.
    """)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if st.button("📶 Bluetooth verbinden met ESP32", type="primary", width="stretch"):
            st.session_state.welcome_shown = True
            st.session_state.page = "Device Connection"
            st.session_state.pending_mode = 'Live'
            st.rerun()
        if st.button("Doorgaan zonder verbinden", type="secondary", width="stretch"):
            st.session_state.welcome_shown = True
            st.session_state.page = "Dashboard"
            st.rerun()

elif page == "Home":
    st.title("⌂ Smart Factory Platform")

    mode_indicator = st.session_state.get('mode', 'Simulation')
    device_status = "Live" if st.session_state.get('device_connected', False) else "Simulation"
    endpoint_info = st.session_state.get('device_endpoint', 'Local simulation')

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⦿ Mode", mode_indicator)
    with col2:
        st.metric("⦿ Device", device_status)
    with col3:
        st.caption(f"Endpoint: {endpoint_info}")

    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("""
    ### Welkom bij jouw Intelligente Fabrieksdashboard

    **Real-time monitoring • AI-gedreven inzichten • Geoptimaliseerde productie**

    Dit platform geeft je volledige controle over je fabrieksomgeving met live data, geavanceerde analyses en intelligente aanbevelingen.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("⌗ Systeem Overzicht")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        st.metric("Actieve Machines", NUM_MACHINES)
        st.caption("Machines in monitoring")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        st.metric("Data Punten", len(df))
        st.caption("Metingen verzameld")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        st.metric("Gem. Belasting", f"{float(np.mean([df[f'current_{i}'].mean() for i in range(1, NUM_MACHINES+1)])):.1f}A")
        st.caption("Stroomverbruik")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        st.metric("Status", "Online")
        st.caption("Systeem actief")
        st.markdown('</div>', unsafe_allow_html=True)

    # Feature showcase
    st.subheader("☰ Platform Mogelijkheden")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### Live Dashboard")
        st.markdown("Real-time monitoring van machine prestaties met interactieve grafieken en trends.")
        st.markdown("**Gebruik:** Bekijk huidige status en historische data")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### Fabrieks Analyse")
        st.markdown("Diepe analyse per machine met gedetailleerde prestaties en vergelijkingen.")
        st.markdown("**Gebruik:** Identificeer problemen en optimaliseer productie")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### AI Inzichten")
        st.markdown("Intelligente analyses met anomalie detectie en geautomatiseerde aanbevelingen.")
        st.markdown("**Gebruik:** Voorspel onderhoud en verbeter efficiency")
        st.markdown('</div>', unsafe_allow_html=True)

    # Quick actions
    st.subheader("☰ Snelle Acties")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⌗ Naar Dashboard", width="stretch"):
            st.session_state.page = "Dashboard"
            st.rerun()

    with col2:
        if st.button("⚒ Machine Overzicht", width="stretch"):
            st.session_state.page = "Factory Analysis"
            st.rerun()

    with col3:
        if st.button("⌬ AI Inzichten", width="stretch"):
            st.session_state.page = "AI Insights"
            st.rerun()

    # Footer info
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #94a3b8; font-size: 0.9rem;'>
    <strong>Tip:</strong> Gebruik de bovenste navigatiebalk voor snelle navigatie en instellingen<br>
    Data wordt automatisch elke 2 seconden bijgewerkt
    </div>
    """, unsafe_allow_html=True)

    st.divider()

elif page == "Dashboard":
    st.title(t("⌗ Smart Factory Dashboard", "⌗ Slimme Fabriek Dashboard"))
    # ── Static header (renders once) ──
    device_status = "Live Device" if st.session_state.get('device_connected', False) else "Simulation Mode"
    endpoint_info = st.session_state.get('device_endpoint', 'Local simulation')
    connected_devices = st.session_state.get('connected_devices', [])
    num_devices = len(connected_devices)
    dashboard_df = st.session_state.get('df', pd.DataFrame())

    current_snapshot = {}
    if isinstance(dashboard_df, pd.DataFrame) and not dashboard_df.empty:
        for machine_index in range(1, NUM_MACHINES + 1):
            column_name = f"current_{machine_index}"
            if column_name in dashboard_df.columns and not dashboard_df[column_name].dropna().empty:
                current_snapshot[column_name] = float(dashboard_df[column_name].iloc[-1])

    active_machine_count = len(current_snapshot)
    machine_name_lookup = {
        f"current_{index}": st.session_state.machine_names[index - 1]
        if index - 1 < len(st.session_state.machine_names)
        else f"M{index}"
        for index in range(1, NUM_MACHINES + 1)
    }
    avg_current = float(np.mean(list(current_snapshot.values()))) if current_snapshot else 0.0
    peak_current = float(np.max(list(current_snapshot.values()))) if current_snapshot else 0.0
    live_voltage = st.session_state.get('last_voltage', None)
    busiest_key = max(current_snapshot, key=lambda key: current_snapshot[key]) if current_snapshot else None
    quietest_key = min(current_snapshot, key=lambda key: current_snapshot[key]) if current_snapshot else None

    if peak_current >= 5.5:
        overview_status = t("High load detected", "Hoge belasting gedetecteerd")
        overview_detail = t("One or more machines are near the limit.", "Een of meer machines zitten dicht op de limiet.")
        status_color = "#f59e0b"
    elif avg_current <= 1.0 and active_machine_count > 0:
        overview_status = t("Low activity", "Lage activiteit")
        overview_detail = t("Current usage is low across the line.", "Het stroomverbruik is laag over de lijn.")
        status_color = "#38bdf8"
    else:
        overview_status = t("System stable", "Systeem stabiel")
        overview_detail = t("No direct attention needed right now.", "Op dit moment is geen directe aandacht nodig.")
        status_color = "#22c55e"

    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#111827 0%,#0f172a 100%); border:1px solid #1f2937; border-left:6px solid {status_color}; border-radius:18px; padding:18px 20px; margin:8px 0 16px 0;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:16px; flex-wrap:wrap;">
                <div>
                    <div style="font-size:0.82rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.08em;">{t('Quick status', 'Snelle status')}</div>
                    <div style="font-size:1.35rem; font-weight:800; color:#f8fafc; margin-top:4px;">{overview_status}</div>
                    <div style="font-size:0.95rem; color:#cbd5e1; margin-top:6px;">{overview_detail}</div>
                </div>
                <div style="font-size:0.82rem; color:#94a3b8; text-align:right; min-width:180px;">
                    <div>{t('Source', 'Bron')}: <span style="color:#f8fafc; font-weight:700;">{device_status}</span></div>
                    <div style="margin-top:4px;">{t('Endpoint', 'Endpoint')}: <span style="color:#e2e8f0;">{endpoint_info}</span></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stat1, stat2, stat3, stat4, stat5 = st.columns(5)
    with stat1:
        st.metric(t("⦿ Source", "⦿ Bron"), device_status)
    with stat2:
        device_delta = t(f"{num_devices} online", f"{num_devices} online") if num_devices > 0 else None
        st.metric(t("Connected Devices", "Verbonden Apparaten"), num_devices, delta=device_delta)
    with stat3:
        st.metric(t("Active Machines", "Actieve Machines"), active_machine_count)
    with stat4:
        st.metric(t("Avg Current", "Gem. Stroom"), f"{avg_current:.2f} A")
    with stat5:
        if live_voltage is not None:
            st.metric(t("Voltage", "Spanning"), f"{live_voltage:.2f} V")
        else:
            st.metric(t("Peak Current", "Piekstroom"), f"{peak_current:.2f} A")

    quick1, quick2 = st.columns(2)
    with quick1:
        busiest_label = machine_name_lookup.get(busiest_key, "-") if busiest_key else "-"
        busiest_value = current_snapshot.get(busiest_key, 0.0) if busiest_key else 0.0
        st.caption(t("Highest current right now", "Hoogste stroom nu"))
        st.markdown(f"**{busiest_label}**  |  {busiest_value:.2f} A")
    with quick2:
        quietest_label = machine_name_lookup.get(quietest_key, "-") if quietest_key else "-"
        quietest_value = current_snapshot.get(quietest_key, 0.0) if quietest_key else 0.0
        st.caption(t("Lowest current right now", "Laagste stroom nu"))
        st.markdown(f"**{quietest_label}**  |  {quietest_value:.2f} A")

    if num_devices > 0:
        device_names = ", ".join(d.get("name", d.get("ip", "?")) for d in connected_devices)
        st.caption(f"{t('Connected', 'Verbonden')}: {device_names}")
    else:
        st.caption(t("No devices connected", "Geen apparaten verbonden"))

    total_anomalies = len(st.session_state.get('anomalies', []))
    total_bottlenecks = len(st.session_state.get('bottlenecks', []))
    avg_load_full = float(
        np.mean([dashboard_df[f"current_{i}"].mean() for i in range(1, NUM_MACHINES + 1) if f"current_{i}" in dashboard_df.columns])
    ) if isinstance(dashboard_df, pd.DataFrame) and not dashboard_df.empty else avg_current
    health_score = max(0, 100 - (avg_load_full * 10) - (total_anomalies * 5))

    if isinstance(dashboard_df, pd.DataFrame) and len(dashboard_df) > 2:
        trend_columns = [
            f"current_{i}" for i in range(1, NUM_MACHINES + 1)
            if f"current_{i}" in dashboard_df.columns
        ]
        trend_series = (
            dashboard_df[trend_columns].to_numpy(dtype=float).mean(axis=1)
            if trend_columns
            else np.zeros(len(dashboard_df), dtype=float)
        )
        trend_value = np.polyfit(
            range(len(dashboard_df)),
            trend_series,
            1,
        )[0]
    else:
        trend_value = 0.0

    if trend_value > 0.05:
        trend_label = t("Rising", "Stijgend")
    elif trend_value < -0.05:
        trend_label = t("Falling", "Dalend")
    else:
        trend_label = t("Stable", "Stabiel")

    st.subheader(t("⌁ Control Overview", "⌁ Controle Overzicht"))
    overview_col1, overview_col2 = st.columns([1.4, 1])

    with overview_col1:
        machine_labels = [machine_name_lookup[key] for key in current_snapshot.keys()]
        machine_values = [current_snapshot[key] for key in current_snapshot.keys()]
        if machine_labels:
            fig_snapshot = go.Figure()
            fig_snapshot.add_trace(go.Bar(
                x=machine_labels,
                y=machine_values,
                marker=dict(color=['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#ec4899', '#84cc16', '#a78bfa'][:len(machine_labels)]),
                text=[f"{value:.2f}A" for value in machine_values],
                textposition='outside',
            ))
            fig_snapshot.update_layout(
                title=t("Machine Snapshot", "Machine Snapshot"),
                template='plotly_dark',
                height=280,
                margin=dict(l=20, r=20, t=42, b=20),
                plot_bgcolor='#0f172a',
                paper_bgcolor='#0f172a',
                yaxis=dict(title=t("Current (A)", "Stroom (A)"), range=[0, 8]),
                xaxis=dict(title=t("Machines", "Machines")),
            )
            st.plotly_chart(fig_snapshot, width="stretch", config={'displayModeBar': False, 'displaylogo': False})

    with overview_col2:
        ai1, ai2 = st.columns(2)
        with ai1:
            st.metric(t("Health", "Gezondheid"), f"{health_score:.0f}%")
        with ai2:
            st.metric(t("Trend", "Trend"), trend_label)
        ai3, ai4 = st.columns(2)
        with ai3:
            st.metric(t("Anomalies", "Afwijkingen"), total_anomalies)
        with ai4:
            st.metric(t("Bottlenecks", "Knelpunten"), total_bottlenecks)

        event_history = st.session_state.get('event_history', [])
        event_counts = {
            t('Anomaly', 'Afwijking'): len([event for event in event_history if event.get('type') == 'Anomaly']),
            t('Bottleneck', 'Knelpunt'): len([event for event in event_history if event.get('type') == 'Bottleneck']),
            t('Connection', 'Verbinding'): len([event for event in event_history if event.get('type') == 'Connection']),
        }
        fig_events = go.Figure()
        fig_events.add_trace(go.Bar(
            x=list(event_counts.keys()),
            y=list(event_counts.values()),
            marker_color=['#ef4444', '#f97316', '#10b981'],
        ))
        fig_events.update_layout(
            title=t("History Overview", "Geschiedenis Overzicht"),
            template='plotly_dark',
            height=220,
            margin=dict(l=20, r=20, t=42, b=20),
            plot_bgcolor='#0f172a',
            paper_bgcolor='#0f172a',
            yaxis=dict(title=t("Count", "Aantal"), rangemode='tozero', dtick=1),
        )
        st.plotly_chart(fig_events, width="stretch", config={'displayModeBar': False, 'displaylogo': False})

        latest_event = event_history[0] if event_history else None
        if latest_event:
            st.caption(f"{t('Latest event', 'Laatste gebeurtenis')}: {latest_event.get('type', '-') } | {latest_event.get('timestamp', '')}")
            st.markdown(f"**{latest_event.get('message', '')}**")

    render_client_realtime_panel(
        machine_names=st.session_state.machine_names[:NUM_MACHINES],
        panel_title=t("⌁ Machine Status — Live", "⌁ Machine Status — Live"),
        show_metrics=True,
    )

elif page == "Factory Analysis":
    st.title(t("⚒ Machine Overview", "⚒ Machine Overzicht"))

    st.markdown(
        f"""
        <div class="page-hero">
            <p class="page-hero-title">{t('Compare machine behavior in one view', 'Vergelijk machinegedrag in één overzicht')}</p>
            <p class="page-hero-sub">{t('Select one or more machines to inspect trends, compare current behavior and identify outliers faster.', 'Selecteer één of meer machines om trends te bekijken, huidig gedrag te vergelijken en uitschieters sneller te herkennen.')}</p>
            <span class="page-chip">{t('Available machines', 'Beschikbare machines')}: {len(st.session_state.machine_names)}</span>
            <span class="page-chip">{t('Mode', 'Modus')}: {st.session_state.get('mode', 'Simulation')}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="page-section">', unsafe_allow_html=True)
    st.subheader("Select Machines to Analyze")
    st.markdown(t(
        "**What you can do here:** Choose which machines you want to look at in detail. You can compare 1 or multiple machines side-by-side to spot patterns and differences.",
        "**Wat je hier kunt doen:** Kies welke machines je in detail wilt analyseren. Vergelijk 1 of meer machines naast elkaar om patronen te zien."
    ))

    selected = st.multiselect(
        "Machines",
        st.session_state.machine_names,
        default=st.session_state.machine_names
    )
    st.markdown('</div>', unsafe_allow_html=True)
    if not selected:
        st.warning(t("Select at least one machine.", "Selecteer minimaal één machine."))
    else:
        render_client_realtime_panel(
            machine_names=selected,
            panel_title=t("⌁ Live Snelheidsmeters", "⌁ Live Snelheidsmeters"),
            show_metrics=False,
        )


elif page == "Device Connection":
    if 'ble_prov_devices' not in st.session_state:
        st.session_state.ble_prov_devices = []

    connected_devices = st.session_state.get('connected_devices', [])
    already_connected = len(connected_devices) > 0
    connected_ip = ', '.join([device.get('ip', '') for device in connected_devices[:3]])

    if (st.session_state.get('pending_mode') == 'Live' or connection_prompt_required) and not already_connected:
        st.warning(
            "De ESP32 is nog niet met de site verbonden. Verbind eerst een apparaat; daarna opent het dashboard met de live amperewaarden."
        )

    # ── Header ──────────────────────────────────────────────────────────────
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("""
        <div class="connect-wrap">
            <p class="connect-title">Apparaten</p>
            <p class="connect-sub">Verbind een ESP32 via Bluetooth</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="connect-anim-wrap">
            <div class="connect-radar">
                <div class="connect-radar-dot"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if already_connected:
            st.markdown("""
            <div class="connect-status">
                <div class="connect-status-icon">Connected</div>
                <p class="connect-status-label" style="color:#86efac;">{count} apparaat/apparaten verbonden</p>
                <p class="connect-status-meta">{ip}</p>
            </div>
            """.format(ip=connected_ip, count=len(connected_devices)), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="connect-status">
                <div class="connect-status-icon">Ready</div>
                <p class="connect-status-label" style="color:#e2e8f0;">Nog geen apparaat verbonden</p>
                <p class="connect-status-meta">Scan eerst via Bluetooth of verbind handmatig via IP.</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Verbonden apparaten met verbreek-knop ────────────────────────────────
    if connected_devices:
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            st.markdown("<p class='connect-section-label'>Verbonden apparaten</p>", unsafe_allow_html=True)
            for device in connected_devices:
                dev_ip = device.get("ip", "")
                dev_name = device.get("name", f"ESP32 {dev_ip.split('.')[-1]}")
                col_info, col_btn = st.columns([3, 1])
                with col_info:
                    st.markdown(f"""
                    <div class="device-card" style="margin-bottom:6px">
                        <div class="device-icon">ESP</div>
                        <div class="device-info">
                            <p class="device-name">{dev_name}</p>
                            <p class="device-ip">{dev_ip}</p>
                        </div>
                        <span class="device-connected-badge">Verbonden</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_btn:
                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                    if st.button("Verbreek", key=f"disc_{dev_ip}", width="stretch", type="secondary"):
                        disconnect_device(dev_ip)
                        st.rerun()
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        # ── Al verbonden → naar dashboard ────────────────────────────────────
        if already_connected:
            if st.button("Ga naar Dashboard →", width="stretch", type="primary"):
                st.session_state.page = "Dashboard"
                st.session_state.mode = 'Live'
                st.session_state.pending_mode = None
                st.rerun()
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── BLE Provisioning – nieuwe ESP32 instellen ────────────────────────
        st.markdown(
            "<p class='connect-section-label'>"
            "Nieuwe ESP32 instellen via Bluetooth</p>",
            unsafe_allow_html=True
        )

        if st.button("Zoek nieuwe ESP32 via Bluetooth", width="stretch", type="primary"):
            with st.spinner("Bluetooth scannen… (6 seconden)"):
                found = ble_scan_for_provisioning(timeout=6.0)
            if found:
                # Haal WiFi-gegevens alvast op zodat we ze niet hoeven in te vullen
                auto_ssid = get_current_wifi_ssid()
                auto_pass = get_current_wifi_password(auto_ssid)
                st.session_state.ble_prov_devices = [
                    {**d, "auto_ssid": auto_ssid, "auto_pass": auto_pass} for d in found
                ]
            else:
                st.session_state.ble_prov_devices = []
                st.info(
                    "Geen nieuwe ESP32 gevonden via Bluetooth. "
                    "Zorg dat de ESP32 voor het eerst opgestart is (blauwe LED knippert)."
                )

        ble_devices = st.session_state.get("ble_prov_devices", [])
        for ble_dev in ble_devices:
            auto_ssid = ble_dev.get("auto_ssid", "")
            st.success("Nieuwe ESP32 gevonden. Vul je WiFi-gegevens in:")
            with st.form(f"prov_form_{ble_dev['address'].replace(':', '_')}"):
                prov_ssid = st.text_input("WiFi naam (SSID)", value=auto_ssid, placeholder="JouwWiFiNaam")
                prov_pass = st.text_input("WiFi wachtwoord", type="password", placeholder="Wachtwoord")
                submitted = st.form_submit_button(
                    "Akkoord - WiFi instellen", width="stretch", type="primary"
                )
                if submitted:
                    if not prov_ssid or not prov_pass:
                        st.error("Vul WiFi naam en wachtwoord in.")
                    else:
                        with st.spinner("ESP32 verbindt met WiFi… (kan 30 seconden duren)"):
                            try:
                                ip = ble_provision_esp32(
                                    ble_dev["address"], prov_ssid, prov_pass, timeout=35.0
                                )
                                st.session_state.ble_prov_devices = []
                            except Exception as exc:
                                st.error(f"Provisioning mislukt: {exc}")
                                ip = None

                        if ip:
                            # ESP32 herstart na provisioning – wacht tot webserver bereikbaar is
                            with st.spinner(f"Wachten tot ESP32 ({ip}) opstart…"):
                                endpoint = None
                                try:
                                    endpoint, payload, normalized = wait_for_device_endpoint(
                                        ip,
                                        80,
                                        attempts=12,
                                        delay_s=3,
                                        timeout=4,
                                    )
                                except Exception:
                                    endpoint = None

                            if endpoint:
                                activate_live_device_connection(ip, 80, timeout=4)
                                st.rerun()
                            else:
                                st.error(
                                    f"ESP32 ({ip}) is verbonden met WiFi maar de webserver reageert niet. "
                                    "Probeer handmatig te verbinden via het 'Al eerder ingesteld?' menu hieronder."
                                )

        # ── Handmatig IP (nooduitgang voor al-geprovisioneerde ESP32s) ────────
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        with st.expander("Al eerder ingesteld? Verbind via IP"):
            default_ip   = st.session_state.get('device_ip', '192.168.1.100')
            default_port = int(st.session_state.get('device_port', 80))
            device_ip    = st.text_input("IP-adres", value=default_ip, placeholder="192.168.1.100")
            device_port  = st.number_input("Poort", value=default_port, min_value=1, max_value=65535)
            if st.button("Verbinden", key="manual_connect", type="primary", width="stretch"):
                with st.spinner(f"Verbinden met {device_ip}…"):
                    try:
                        endpoint, payload, normalized = activate_live_device_connection(
                            device_ip, int(device_port),
                            timeout=st.session_state.get('connection_timeout', 5)
                        )
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Verbinden mislukt: {exc}")

        st.markdown("""
        <div class="connect-feature-grid">
            <div class="connect-feature-card">
                <p class="connect-feature-title">Snelle BLE onboarding</p>
                <p class="connect-feature-text">Scan, selecteer en zet je ESP32 binnen seconden op WiFi.</p>
            </div>
            <div class="connect-feature-card">
                <p class="connect-feature-title">Live status & reconnect</p>
                <p class="connect-feature-text">Zie direct welke devices verbonden zijn en herstel snel de link.</p>
            </div>
            <div class="connect-feature-card">
                <p class="connect-feature-title">Fallback via IP</p>
                <p class="connect-feature-text">Voor reeds ingestelde modules kun je direct handmatig via IP verbinden.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Annuleren ────────────────────────────────────────────────────────
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Annuleren", width="stretch", type="secondary"):
            st.session_state.page = st.session_state.get("last_non_device_page", "Dashboard")
            st.session_state.mode = 'Simulation'
            st.session_state.pending_mode = None
            st.rerun()

elif page == "Platform":
    render_platform_sidebar_nav()
    platform_auth_token = str(st.query_params.get("auth", "") or "").strip()
    platform_auth_suffix = f"&auth={platform_auth_token}" if platform_auth_token else ""
    st.markdown(
        f"""
        <div style="background:linear-gradient(120deg,#0b1220 0%,#1e293b 60%,#0f766e 130%); border:1px solid #334155; border-radius:22px; padding:28px; margin:6px 0 18px 0;">
            <div style="font-size:0.85rem; letter-spacing:0.08em; text-transform:uppercase; color:#93c5fd; font-weight:700;">Smart Factory Suite</div>
            <div style="font-size:2rem; line-height:1.2; font-weight:800; color:#f8fafc; margin-top:8px;">
                {t('Real-time monitoring for modern production teams.', 'Realtime monitoring voor moderne productieteams.')}
            </div>
            <div style="font-size:1rem; color:#cbd5e1; max-width:880px; margin-top:12px;">
                {t('Follow machine behavior live, prevent downtime early, and turn raw telemetry into practical production decisions.', 'Volg machinegedrag live, voorkom downtime vroegtijdig en vertaal ruwe telemetrie naar praktische productie-beslissingen.')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cta1, cta2 = st.columns(2)
    with cta1:
        st.markdown(
            f"""
            <a href="?page=Dashboard{platform_auth_suffix}" target="_self"
               style="display:block; text-align:center; text-decoration:none; background:#3b82f6; color:#ffffff; padding:12px 14px; border-radius:10px; font-weight:700; border:1px solid #2563eb;">
               {t('Open Live Demo', 'Open Live Demo')}
            </a>
            """,
            unsafe_allow_html=True,
        )
    with cta2:
        st.markdown(
            f"""
            <a href="?shortcut=action=open_device_connection{platform_auth_suffix}" target="_self"
               style="display:block; text-align:center; text-decoration:none; background:#1e293b; color:#f8fafc; padding:12px 14px; border-radius:10px; font-weight:700; border:1px solid #334155;">
               {t('Connect Device', 'Verbind apparaat')}
            </a>
            """,
            unsafe_allow_html=True,
        )

    st.subheader(t("Features", "Features"))
    feat1, feat2, feat3 = st.columns(3)
    with feat1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"### {t('Live Monitoring', 'Live Monitoring')}")
        st.markdown(t(
            "Track current trends and status changes across your line in one dashboard.",
            "Volg stroomtrends en statusveranderingen over je hele lijn in één dashboard."
        ))
        st.markdown('</div>', unsafe_allow_html=True)
    with feat2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"### {t('Anomaly Detection', 'Afwijkingsdetectie')}")
        st.markdown(t(
            "Get early warning signals when machine behavior shifts away from normal.",
            "Krijg vroege waarschuwingen wanneer machinegedrag afwijkt van normaal."
        ))
        st.markdown('</div>', unsafe_allow_html=True)
    with feat3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"### {t('Device Connectivity', 'Device Connectiviteit')}")
        st.markdown(t(
            "Connect ESP32 devices quickly and stream data to your monitoring dashboard.",
            "Verbind ESP32-devices snel en stream data naar je monitoringdashboard."
        ))
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader(t("Simulation Visual", "Simulatie Visual"))
    st.caption(t(
        "Preview of simulated machine behavior over time.",
        "Voorbeeld van gesimuleerd machinegedrag over tijd."
    ))

    sim_points = 24
    time_axis = list(range(sim_points))
    preview_count = min(NUM_MACHINES, 3)
    color_scale = ['#60a5fa', '#34d399', '#fbbf24']
    preview_tickvals = [0, 6, 12, 18, sim_points - 1]

    fig_preview = go.Figure()
    for i in range(1, preview_count + 1):
        machine_label = st.session_state.machine_names[i - 1] if i - 1 < len(st.session_state.machine_names) else f"Machine {i}"
        base = float(1.2 + (i * 0.55))
        amp = float(0.35 + (i * 0.08))
        speed = float(0.34 + (i * 0.05))
        phase = float(i * 0.9)
        sim_values = [
            float(np.clip(base + amp * np.sin((t_idx * speed) + phase) + np.random.normal(0, 0.07), 0.5, 6.0))
            for t_idx in time_axis
        ]

        fig_preview.add_trace(go.Scatter(
            x=time_axis,
            y=sim_values,
            mode='lines+markers',
            name=machine_label,
            line=dict(width=3.2, color=color_scale[(i - 1) % len(color_scale)], shape='linear'),
            marker=dict(size=6, color=color_scale[(i - 1) % len(color_scale)], line=dict(width=0)),
            hovertemplate=t("Time", "Tijd") + ": %{x}<br>" + t("Current", "Stroom") + ": %{y:.2f} A<extra>%{fullData.name}</extra>",
        ))

    fig_preview.update_layout(
        template="plotly_dark",
        height=340,
        margin=dict(l=22, r=20, t=22, b=28),
        yaxis=dict(
            title=dict(text=t("Current (A)", "Stroom (A)"), font=dict(size=13, color="#f8fafc")),
            range=[0, 8],
            dtick=1,
            gridcolor="rgba(148,163,184,0.22)",
            zerolinecolor="rgba(148,163,184,0.45)",
            tickfont=dict(size=12, color="#dbeafe"),
        ),
        xaxis=dict(
            title=dict(text=t("Time (sim)", "Tijd (sim)"), font=dict(size=13, color="#f8fafc")),
            range=[0, sim_points - 1],
            tickmode='array',
            tickvals=preview_tickvals,
            showgrid=True,
            gridcolor="rgba(148,163,184,0.12)",
            tickfont=dict(size=12, color="#dbeafe"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="left",
            x=0,
            font=dict(size=12, color="#e2e8f0"),
            bgcolor="rgba(15,23,42,0.55)",
            bordercolor="rgba(148,163,184,0.22)",
            borderwidth=1,
        ),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        hovermode="x unified",
    )
    st.plotly_chart(fig_preview, width="stretch", config={'displayModeBar': False, 'displaylogo': False})

    st.subheader(t("Benefits", "Voordelen"))
    st.markdown(t(
        "- Reduce unplanned downtime with earlier visibility\n"
        "- Improve response times with one clear operational view\n"
        "- Scale from one line to multiple machines with the same workflow",
        "- Verminder ongeplande downtime met eerder inzicht\n"
        "- Verbeter reactietijd met één duidelijk operationeel overzicht\n"
        "- Schaal van één lijn naar meerdere machines met dezelfde workflow"
    ))

    st.subheader(t("Target Audience", "Doelgroep"))
    st.markdown(t(
        "Built for production leads, operators, and maintenance teams that need reliable machine visibility.",
        "Gemaakt voor productieleiding, operators en technische teams die betrouwbare machine-inzichten nodig hebben."
    ))

    st.subheader(t("Subscription", "Abonnement"))
    st.markdown(t(
        "Choose a monthly monitoring subscription to keep cloud monitoring active, receive updates, and retain remote access history.",
        "Kies een maandelijks monitoringabonnement om cloud monitoring actief te houden, updates te ontvangen en toegang te houden tot remote historie."
    ))
    st.markdown(t(
        "- Starter: 1 line monitoring\n"
        "- Pro: multiple machines + alerts\n"
        "- Enterprise: custom rollout and support",
        "- Starter: monitoring voor 1 lijn\n"
        "- Pro: meerdere machines + alerts\n"
        "- Enterprise: maatwerk uitrol en support"
    ))

    st.subheader(t("Where to buy", "Waar product te halen"))
    st.markdown(t(
        "You can order the hardware kit and activation through our webshop or via an implementation partner.",
        "Je kunt de hardwarekit en activatie bestellen via onze webshop of via een implementatiepartner."
    ))
    buy1, buy2 = st.columns(2)
    with buy1:
        st.link_button(
            t("Open Webshop", "Open webshop"),
            "https://example.com/webshop",
            width="stretch",
        )
    with buy2:
        st.link_button(
            t("Find a partner", "Zoek partner"),
            "https://example.com/partners",
            width="stretch",
        )

    st.markdown(
        f"""
        <a href="?page=Dashboard{platform_auth_suffix}" target="_self"
           style="display:block; text-align:center; text-decoration:none; background:#14b8a6; color:#06202a; padding:12px 14px; border-radius:10px; font-weight:800; border:1px solid #2dd4bf; margin-top:10px;">
           {t('Start Monitoring Now', 'Start nu met monitoren')}
        </a>
        """,
        unsafe_allow_html=True,
    )

elif page == "About":
    render_platform_sidebar_nav()
    st.markdown(
        """
        <div style="background:linear-gradient(120deg,#0b1220 0%,#1e293b 60%,#134e4a 130%);border:1px solid #334155;border-radius:18px;padding:28px 32px;margin-bottom:22px;">
            <div style="font-size:0.8rem;letter-spacing:0.1em;text-transform:uppercase;color:#34d399;font-weight:700;">Wie zijn wij</div>
            <div style="font-size:2rem;font-weight:800;color:#f8fafc;margin-top:6px;line-height:1.25;">Over Smart Factory Suite</div>
            <div style="font-size:1.05rem;color:#cbd5e1;max-width:820px;margin-top:10px;">Wij bouwen praktische monitoringoplossingen voor productieteams die betrouwbare machine-inzichten nodig hebben — live, eenvoudig en schaalbaar.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader(t("Our mission", "Onze missie"))
    st.markdown(t(
        "Smart Factory Suite was built because existing monitoring tools are either too complex, too expensive, or too generic. "
        "We focus on one thing: giving operators and production leads real-time visibility into their machines, with hardware they can set up themselves.",
        "Smart Factory Suite is ontstaan omdat bestaande monitoringoplossingen te complex, te duur of te generiek zijn. "
        "Wij focussen op één ding: operators en productieleiding realtime inzicht geven in hun machines, met hardware die ze zelf kunnen installeren."
    ))

    st.subheader(t("Our approach", "Onze aanpak"))
    ap1, ap2, ap3 = st.columns(3)
    with ap1:
        st.markdown(
            "<div class='card'><b>📡 Device integratie</b><br><br>"
            + t(
                "ESP32-based sensors connect to your production line in minutes. No complex wiring. No specialist required.",
                "ESP32-sensors koppel je binnen minuten aan je productielijn. Geen complexe bedrading. Geen specialist nodig."
            )
            + "</div>",
            unsafe_allow_html=True
        )
    with ap2:
        st.markdown(
            "<div class='card'><b>📊 Live data & simulatie</b><br><br>"
            + t(
                "View live current data per machine, or explore with simulation mode to understand your production patterns before going live.",
                "Bekijk live stroomdata per machine, of verken met simulatiemodus om je productiepatronen te begrijpen voordat je live gaat."
            )
            + "</div>",
            unsafe_allow_html=True
        )
    with ap3:
        st.markdown(
            "<div class='card'><b>🤖 AI & afwijkingen</b><br><br>"
            + t(
                "Automatic anomaly detection alerts you when machines deviate from normal behavior — so you can act early instead of react late.",
                "Automatische afwijkingsdetectie waarschuwt wanneer machines afwijken van normaal gedrag — zodat je vroeg handelt in plaats van laat reageert."
            )
            + "</div>",
            unsafe_allow_html=True
        )

    st.subheader(t("Technology", "Technologie"))
    st.markdown(t(
        "- **ESP32** microcontrollers for affordable, reliable edge sensing\n"
        "- **Python / Streamlit** for fast, web-based dashboard delivery\n"
        "- **Plotly** for interactive, real-time charts\n"
        "- **Cloud Bridge** for optional remote access outside the local network\n"
        "- **AI Insights** powered by statistical anomaly detection and pattern analysis",
        "- **ESP32** microcontrollers voor betaalbare, betrouwbare edge-sensoriek\n"
        "- **Python / Streamlit** voor snelle, webgebaseerde dashboardlevering\n"
        "- **Plotly** voor interactieve, realtime grafieken\n"
        "- **Cloud Bridge** voor optionele externe toegang buiten het lokale netwerk\n"
        "- **AI Insights** aangedreven door statistische afwijkingsdetectie en patroonanalyse"
    ))

    st.subheader(t("Core values", "Kernwaarden"))
    v1, v2, v3, v4 = st.columns(4)
    for col, (icon, label) in zip(
        [v1, v2, v3, v4],
        [
            ("🔍", t("Transparency", "Transparantie")),
            ("⚡", t("Speed", "Snelheid")),
            ("🛠", t("Repairability", "Repareerbaarheid")),
            ("📦", t("Simplicity", "Eenvoud")),
        ],
    ):
        with col:
            st.markdown(
                f"<div style='text-align:center;padding:14px;background:#1e293b;border-radius:12px;border:1px solid #334155;'>"
                f"<div style='font-size:1.7rem;'>{icon}</div>"
                f"<div style='font-size:0.9rem;color:#f8fafc;font-weight:700;margin-top:6px;'>{label}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )


elif page == "Contact":
    render_platform_sidebar_nav()
    st.markdown(
        """
        <div style="background:linear-gradient(120deg,#0b1220 0%,#1e293b 60%,#1e3a5f 130%);border:1px solid #334155;border-radius:18px;padding:28px 32px;margin-bottom:22px;">
            <div style="font-size:0.8rem;letter-spacing:0.1em;text-transform:uppercase;color:#93c5fd;font-weight:700;">Neem contact op</div>
            <div style="font-size:2rem;font-weight:800;color:#f8fafc;margin-top:6px;line-height:1.25;">Contact</div>
            <div style="font-size:1.05rem;color:#cbd5e1;max-width:820px;margin-top:10px;">Heb je vragen, wil je een demo plannen of hulp bij de installatie? We reageren normaal binnen één werkdag.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cc1, cc2 = st.columns([3, 2])
    with cc1:
        st.subheader(t("Send a message", "Stuur een bericht"))
        contact_name = st.text_input(t("Your name", "Jouw naam"), placeholder=t("Jan de Vries", "Jan de Vries"))
        contact_email = st.text_input(t("Email address", "E-mailadres"), placeholder="jan@bedrijf.nl")
        contact_subject = st.selectbox(
            t("Subject", "Onderwerp"),
            [
                t("General question", "Algemene vraag"),
                t("Device connection help", "Hulp bij device-koppeling"),
                t("Demo request", "Demoverzoek"),
                t("Subscription / pricing", "Abonnement / prijs"),
                t("Bug report", "Foutmelding"),
                t("Other", "Anders"),
            ]
        )
        contact_msg = st.text_area(
            t("Message", "Bericht"),
            height=160,
            placeholder=t(
                "Describe your setup, question or issue as clearly as possible.",
                "Beschrijf je opstelling, vraag of probleem zo duidelijk mogelijk."
            )
        )
        if st.button(t("Send message", "Bericht versturen"), type="primary", width="stretch"):
            if contact_name and contact_email and contact_msg:
                st.success(t(
                    f"Thanks {contact_name}! We received your message and will respond within one business day.",
                    f"Bedankt {contact_name}! We hebben je bericht ontvangen en reageren binnen één werkdag."
                ))
            else:
                st.warning(t("Please fill in all fields before sending.", "Vul alle velden in voordat je verstuurt."))

    with cc2:
        st.subheader(t("Direct contact", "Direct contact"))
        st.markdown(
            "<div class='card' style='margin-bottom:12px;'>"
            "<b>📧 Email</b><br>support@smartfactorysuite.com</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='card' style='margin-bottom:12px;'>"
            "<b>📞 Telefoon</b><br>+31 20 123 45 67</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='card' style='margin-bottom:12px;'>"
            + "<b>🕐 " + t("Response time", "Reactietijd") + "</b><br>"
            + t("Within 1 business day", "Binnen 1 werkdag")
            + "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='card'>"
            + "<b>📍 " + t("Location", "Locatie") + "</b><br>"
            + t("Amsterdam, Netherlands", "Amsterdam, Nederland")
            + "</div>",
            unsafe_allow_html=True,
        )


elif page == "FAQ":
    render_platform_sidebar_nav()
    st.markdown(
        """
        <div style="background:linear-gradient(120deg,#0b1220 0%,#1e293b 60%,#3b1f5e 130%);border:1px solid #334155;border-radius:18px;padding:28px 32px;margin-bottom:22px;">
            <div style="font-size:0.8rem;letter-spacing:0.1em;text-transform:uppercase;color:#c4b5fd;font-weight:700;">Veelgestelde vragen</div>
            <div style="font-size:2rem;font-weight:800;color:#f8fafc;margin-top:6px;line-height:1.25;">FAQ</div>
            <div style="font-size:1.05rem;color:#cbd5e1;max-width:820px;margin-top:10px;">Antwoorden op de meest gestelde vragen over setup, gebruik en abonnementen.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"**{t('Getting started', 'Aan de slag')}**")
    with st.expander(t("How quickly can I start?", "Hoe snel kan ik starten?")):
        st.markdown(t(
            "Once you have an ESP32 device and the app running, you can typically be live-monitoring within 10 minutes. "
            "Open the Device Connection page, follow the BLE onboarding steps, and the dashboard activates automatically once a connection is confirmed.",
            "Als je een ESP32-device hebt en de app draait, ben je doorgaans binnen 10 minuten live aan het monitoren. "
            "Open de pagina Device Connection, volg de BLE-onboarding stappen en het dashboard activeert automatisch zodra een verbinding bevestigd is."
        ))
    with st.expander(t("Do I need technical knowledge to set up?", "Heb ik technische kennis nodig voor de installatie?")):
        st.markdown(t(
            "Basic familiarity with WiFi networks is enough. The BLE provisioning flow walks you step by step through connecting your ESP32 to the local network. "
            "No code changes or programming knowledge required for the standard setup.",
            "Basiskennis van WiFi-netwerken is voldoende. De BLE-provisioning flow begeleidt je stap voor stap bij het verbinden van je ESP32 met het lokale netwerk. "
            "Geen codewijzigingen of programmeerkennis vereist voor de standaardinstallatie."
        ))
    with st.expander(t("What hardware do I need?", "Welke hardware heb ik nodig?")):
        st.markdown(t(
            "You need at least one ESP32 development board with the Smart Factory firmware, a current sensor compatible with the board, "
            "and a computer or tablet to run the dashboard. All components are available in our hardware kit.",
            "Je hebt minimaal één ESP32-ontwikkelboard nodig met de Smart Factory-firmware, een stroommeter die compatibel is met het board, "
            "en een computer of tablet om het dashboard te draaien. Alle componenten zijn verkrijgbaar in onze hardwarekit."
        ))

    st.markdown(f"**{t('Monitoring & data', 'Monitoring & data')}**")
    with st.expander(t("Does this work for multiple machines?", "Werkt dit met meerdere machines?")):
        st.markdown(t(
            "Yes. You can connect up to 10 devices and assign each one to a named machine. The dashboard shows all machines side by side. "
            "Each machine gets its own current chart, status indicator, and anomaly log.",
            "Ja. Je kunt tot 10 devices koppelen en elk toewijzen aan een benoemde machine. Het dashboard toont alle machines naast elkaar. "
            "Elke machine krijgt zijn eigen stroomgrafiek, statusindicator en afwijkingslog."
        ))
    with st.expander(t("How does anomaly detection work?", "Hoe werkt afwijkingsdetectie?")):
        st.markdown(t(
            "The system calculates a rolling baseline (mean and standard deviation) for each machine's current draw. "
            "When a reading falls more than 2 standard deviations from the recent average, it is flagged as an anomaly. "
            "You can review flagged events in the AI Insights page.",
            "Het systeem berekent een rolling baseline (gemiddelde en standaarddeviatie) voor het stroomverbruik van elke machine. "
            "Als een meting meer dan 2 standaarddeviaties afwijkt van het recente gemiddelde, wordt dit gemarkeerd als een afwijking. "
            "Je kunt gemarkeerde gebeurtenissen bekijken op de pagina AI Insights."
        ))
    with st.expander(t("How long is my data history kept?", "Hoe lang wordt mijn datahistorie bewaard?")):
        st.markdown(t(
            "History is kept in-memory during the current session. With Cloud Bridge enabled, the latest payload is cached on disk "
            "and can be retrieved after a restart. Long-term storage requires connecting a database backend (contact us for Enterprise setup).",
            "Historie wordt in het geheugen bewaard tijdens de huidige sessie. Met Cloud Bridge ingeschakeld wordt de laatste payload op schijf gecached "
            "en kan worden opgehaald na een herstart. Langetermijnopslag vereist het koppelen van een databasebackend (neem contact op voor Enterprise-instellingen)."
        ))
    with st.expander(t("Can I monitor remotely?", "Kan ik op afstand monitoren?")):
        st.markdown(t(
            "Yes. Enable Cloud Bridge in Settings and point your ESP32 to push data to the configured endpoint. "
            "You can then view the latest machine data from any browser, even outside the local network.",
            "Ja. Schakel Cloud Bridge in via Instellingen en configureer je ESP32 om data naar het ingestelde endpoint te sturen. "
            "Je kunt dan de laatste machinedata bekijken vanuit elke browser, ook buiten het lokale netwerk."
        ))

    st.markdown(f"**{t('Subscriptions & pricing', 'Abonnementen & prijs')}**")
    with st.expander(t("What subscription plans are available?", "Welke abonnementen zijn er?")):
        st.markdown(t(
            "- **Starter** — 1 machine line, local monitoring only, no cloud bridge. Free during beta.\n"
            "- **Pro** — Up to 5 devices, cloud bridge, anomaly alerts by email.\n"
            "- **Enterprise** — Unlimited devices, custom integrations, dedicated support and SLA.",
            "- **Starter** — 1 machinegroep, alleen lokale monitoring, geen cloud bridge. Gratis tijdens beta.\n"
            "- **Pro** — Tot 5 devices, cloud bridge, afwijkingswaarschuwingen per e-mail.\n"
            "- **Enterprise** — Onbeperkte devices, maatwerk integraties, dedicated support en SLA."
        ))
    with st.expander(t("Is there a free trial?", "Is er een gratis proefperiode?")):
        st.markdown(t(
            "Yes. The Starter plan is free and fully functional for single-machine monitoring. "
            "You can upgrade to Pro at any time without losing your existing configuration.",
            "Ja. Het Starterplan is gratis en volledig functioneel voor monitoring van één machine. "
            "Je kunt op elk moment upgraden naar Pro zonder je bestaande configuratie te verliezen."
        ))


elif page == "Support":
    render_platform_sidebar_nav()
    st.markdown(
        """
        <div style="background:linear-gradient(120deg,#0b1220 0%,#1e293b 60%,#1c3a2e 130%);border:1px solid #334155;border-radius:18px;padding:28px 32px;margin-bottom:22px;">
            <div style="font-size:0.8rem;letter-spacing:0.1em;text-transform:uppercase;color:#34d399;font-weight:700;">Hulp & ondersteuning</div>
            <div style="font-size:2rem;font-weight:800;color:#f8fafc;margin-top:6px;line-height:1.25;">Support</div>
            <div style="font-size:1.05rem;color:#cbd5e1;max-width:820px;margin-top:10px;">Alles wat je nodig hebt om snel op weg te zijn of een probleem op te lossen.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader(t("Step-by-step: connecting your first device", "Stap voor stap: je eerste device koppelen"))
    st.markdown(t(
        "1. **Power on** your ESP32 and make sure the firmware is flashed.\n"
        "2. In the app, open **Device Connection** via the top navigation.\n"
        "3. Click **Start BLE Scan** and select your device from the list.\n"
        "4. Enter your WiFi credentials and confirm. The device connects to your network.\n"
        "5. The app automatically tries to reach the device endpoint. Once found, **Live mode** activates.\n"
        "6. If BLE is unavailable, use the **Connect via IP** fallback at the bottom of the page.",
        "1. **Zet je ESP32 aan** en zorg dat de firmware geflasht is.\n"
        "2. Open in de app **Device Connection** via de bovenste navigatie.\n"
        "3. Klik op **Start BLE Scan** en selecteer je device uit de lijst.\n"
        "4. Voer je WiFi-gegevens in en bevestig. Het device verbindt met je netwerk.\n"
        "5. De app probeert automatisch het device-endpoint te bereiken. Na succes activeert de **Live modus**.\n"
        "6. Als BLE niet beschikbaar is, gebruik dan de **Verbind via IP** optie onderaan de pagina."
    ))

    st.subheader(t("Troubleshooting", "Probleemoplossing"))
    with st.expander(t("Device not found during BLE scan", "Device niet gevonden tijdens BLE-scan")):
        st.markdown(t(
            "- Make sure the ESP32 is powered on and within 5 meters.\n"
            "- Verify the firmware on the device is the Smart Factory version.\n"
            "- Restart the ESP32 and wait 10 seconds before scanning again.\n"
            "- Check that Bluetooth is enabled on your computer or tablet.",
            "- Zorg dat de ESP32 aan staat en binnen 5 meter is.\n"
            "- Controleer of de firmware op het device de Smart Factory-versie is.\n"
            "- Herstart de ESP32 en wacht 10 seconden voor je opnieuw scant.\n"
            "- Controleer of Bluetooth ingeschakeld is op je computer of tablet."
        ))
    with st.expander(t("Device connected but dashboard shows no data", "Device verbonden maar dashboard toont geen data")):
        st.markdown(t(
            "- Open Settings → Device tab and check the listed device IP and port.\n"
            "- Try navigating to http://<device-ip>/data in your browser — you should see a JSON response.\n"
            "- If the page is unreachable, check firewall rules or try reconnecting via IP.\n"
            "- Increase the connection timeout in Settings if you are on a slow network.",
            "- Open Instellingen → Apparaat en controleer het vermelde device-IP en de poort.\n"
            "- Probeer http://<device-ip>/data te openen in je browser — je zou een JSON-antwoord moeten zien.\n"
            "- Als de pagina onbereikbaar is, controleer firewallregels of probeer opnieuw te verbinden via IP.\n"
            "- Verhoog de verbindingstimeout in Instellingen als je op een traag netwerk zit."
        ))
    with st.expander(t("Data looks incorrect or jumpy", "Data ziet er incorrect of sprongen uit")):
        st.markdown(t(
            "- Check that the current sensor is properly clamped around the cable.\n"
            "- Verify no other large loads are sharing the measured line.\n"
            "- In Simulation mode, data is generated by the app and is always within expected ranges — if you see similar spikes in simulation, refresh the page.\n"
            "- In Live mode, try increasing the refresh interval in Settings to reduce noise.",
            "- Controleer of de stroommeter correct om de kabel geklemd is.\n"
            "- Verifieer dat er geen andere grote verbruikers op de gemeten lijn zitten.\n"
            "- In Simulatiemodus wordt data gegenereerd door de app en valt altijd binnen verwachte ranges — als je vergelijkbare pieken in simulatie ziet, ververs de pagina.\n"
            "- In Live modus: probeer het verversinterval in Instellingen te verhogen om ruis te verminderen."
        ))
    with st.expander(t("History page is empty", "Historiepagina is leeg")):
        st.markdown(t(
            "History is built up during an active session. If you just started the app, run the dashboard in Simulation or Live mode for a few minutes first. "
            "Events and anomalies appear in History after they are detected.",
            "Historie wordt opgebouwd tijdens een actieve sessie. Als je de app net gestart hebt, laat het dashboard eerst een paar minuten draaien in Simulatie- of Live modus. "
            "Gebeurtenissen en afwijkingen verschijnen in Historie nadat ze gedetecteerd zijn."
        ))

    st.subheader(t("Useful pages in the app", "Handige pagina's in de app"))
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        if st.button("📡 " + t("Device Connection", "Device Connection"), width="stretch", key="sup_to_device"):
            st.session_state.page = "Device Connection"
            st.session_state.pending_mode = 'Live'
            st.rerun()
    with sc2:
        if st.button("🤖 " + t("AI Insights", "AI Insights"), width="stretch", key="sup_to_ai"):
            st.session_state.page = "AI Insights"
            st.rerun()
    with sc3:
        if st.button("📋 " + t("History", "Geschiedenis"), width="stretch", key="sup_to_history"):
            st.session_state.page = "History"
            st.rerun()

    st.subheader(t("Still stuck? Contact us", "Nog steeds vast? Neem contact op"))
    st.markdown("📧 support@smartfactorysuite.com")
    if st.button(t("Open contact form", "Open contactformulier"), width="stretch", type="primary", key="sup_to_contact"):
        st.session_state.page = "Contact"
        st.rerun()


elif page == "Account":
    render_platform_sidebar_nav()
    current_user = st.session_state.get("auth_user") or "gast"
    is_guest = current_user == "gast"
    mode_label = st.session_state.get("mode", "Simulation")
    language_label = st.session_state.get("language", "EN")
    machines = int(st.session_state.get("num_machines", 1))
    anomalies_total = len(st.session_state.get("anomalies", []))
    bottlenecks_total = len(st.session_state.get("bottlenecks", []))
    acct_section = st.session_state.get("account_section", "profiel")

    # ── header banner ───────────────────────────────────────────────────
    # derive initials for avatar
    _pname = st.session_state.get("profile_name", "") or current_user
    _initials = "".join(w[0].upper() for w in _pname.split()[:2]) if _pname else "?"
    _company = st.session_state.get("profile_company", "")
    _company_html = f'<span style="color:#64748b;font-size:0.85rem;">— {_company}</span>' if _company else ""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(130deg, rgba(15,23,42,0.96) 0%, rgba(17,24,39,0.96) 55%, rgba(37,99,235,0.18) 100%);
            border: 1px solid rgba(59,130,246,0.18);
            border-radius: 20px;
            padding: 20px 24px;
            margin-bottom: 18px;
            display:flex;align-items:center;gap:18px;
            box-shadow: 0 4px 24px rgba(2,8,23,0.24), inset 0 1px 0 rgba(148,163,184,0.06);
        ">
            <div style="
                width:52px;height:52px;border-radius:50%;flex-shrink:0;
                background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
                display:flex;align-items:center;justify-content:center;
                font-size:1.25rem;font-weight:800;color:#fff;
                box-shadow: 0 2px 12px rgba(37,99,235,0.4);
            ">{_initials}</div>
            <div>
                <div style="font-size:1.15rem;font-weight:700;color:#f1f5f9;line-height:1.2;">
                    {_pname} {_company_html}
                </div>
                <div style="margin-top:6px;display:flex;gap:6px;flex-wrap:wrap;">
                    <span class="settings-chip" style="font-size:0.78rem;">🔵 {mode_label}</span>
                    <span class="settings-chip" style="font-size:0.78rem;">🌐 {language_label}</span>
                    <span class="settings-chip" style="font-size:0.78rem;">💳 {st.session_state.get('subscription_plan','Starter')}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if is_guest:
        st.warning(t(
            "You are using a guest account. Log in to save your settings.",
            "Je gebruikt een gastaccount. Log in om je instellingen op te slaan."
        ))

    # ── nav sections definition ──
    _acct_sections = [
        ("profiel",      "👤 " + t("Profile",       "Profiel")),
        ("machines",     "🏭 " + t("My machines",   "Mijn machines")),
        ("meldingen",    "🔔 " + t("Notifications", "Meldingen")),
        ("overzicht",    "📊 " + t("Overview",      "Overzicht")),
        ("instellingen", "⚙️ " + t("Settings",      "Instellingen")),
        ("abonnement",   "💳 " + t("Subscription",  "Abonnement")),
        ("support",      "🛠️ " + t("Support",       "Support")),
        ("uitloggen",    "🚪 " + t("Logout",        "Uitloggen")),
    ]

    nav_col, content_col = st.columns([1, 3], gap="medium")

    # ── left nav ────────────────────────────────────────────────────────
    with nav_col:
        st.markdown('<span class="acct-nav-marker"></span><span class="acct-nav-label">Menu</span>', unsafe_allow_html=True)
        for _key, _label in _acct_sections:
            _is_active = acct_section == _key
            if st.button(_label, key=f"acct_nav_{_key}", width="stretch",
                         type="primary" if _is_active else "secondary"):
                st.session_state.account_section = _key
                st.rerun()

    # ── right content ───────────────────────────────────────────────────
    with content_col:
        st.markdown('<span class="acct-content-marker"></span>', unsafe_allow_html=True)

        # ─── 👤 Profiel ───────────────────────────────────────────────
        if acct_section == "profiel":
            account_profile_editing = bool(st.session_state.get("account_profile_editing", False))
            st.subheader("👤 " + t("Profile", "Profiel"))
            st.text_input(t("Name", "Naam"),
                value=st.session_state.get("profile_name", ""), key="profile_name", disabled=not account_profile_editing)
            st.text_input(t("Email", "E-mail"),
                value=st.session_state.get("profile_email", ""), key="profile_email", disabled=not account_profile_editing)
            st.text_input(t("Company", "Bedrijf"),
                value=st.session_state.get("profile_company", ""), key="profile_company", disabled=not account_profile_editing)
            if not account_profile_editing:
                if st.button(t("Change", "Wijzigen"), key="account_edit_details",
                             width="stretch", type="primary"):
                    st.session_state.account_profile_editing = True
                    st.rerun()
            elif st.button(t("Save changes", "Wijzigingen opslaan"), key="account_save_details",
                           width="stretch", type="primary"):
                st.session_state.account_profile_editing = False
                if not is_guest:
                    persist_active_user_state()
                    st.toast(t("Profile saved.", "Profiel opgeslagen."), icon="✅")
                else:
                    st.toast(t("Log in to save permanently.", "Log in om permanent op te slaan."), icon="ℹ️")
                st.rerun()

        # ─── 🏭 Mijn machines ─────────────────────────────────────────
        elif acct_section == "machines":
            st.subheader("🏭 " + t("My machines", "Mijn machines"))
            machine_names = list(st.session_state.get("machine_names", []))
            if len(machine_names) < machines:
                machine_names.extend([f"Machine {i}" for i in range(len(machine_names) + 1, machines + 1)])
            for idx in range(machines):
                current_value = machine_names[idx] if idx < len(machine_names) else f"Machine {idx + 1}"
                mc1, mc2 = st.columns([3, 1])
                with mc1:
                    st.text_input(
                        f"{t('Name', 'Naam')} {idx + 1}",
                        value=current_value,
                        key=f"machine_name_{idx}"
                    )
                with mc2:
                    latest_val = float(
                        st.session_state.get("last_current_values", {}).get(f"current_{idx + 1}", 0.0) or 0.0
                    )
                    status_lbl = ("🟢 " + t("Running", "Draait")) if latest_val > 0.6 else ("⚪ " + t("Idle", "Inactief"))
                    st.caption(status_lbl)
            if st.button(t("Save names", "Namen opslaan"), key="account_save_machines",
                         width="stretch", type="primary"):
                edited_names = [st.session_state.get(f"machine_name_{i}", f"Machine {i+1}") for i in range(machines)]
                st.session_state.machine_names = edited_names
                if not is_guest:
                    persist_active_user_state()
                st.toast(t("Machine names saved.", "Machinenamen opgeslagen."), icon="✅")

        # ─── 🔔 Meldingen ─────────────────────────────────────────────
        elif acct_section == "meldingen":
            st.subheader("🔔 " + t("Notifications", "Meldingen"))
            st.checkbox(
                t("Fault notifications", "Storingsmeldingen"),
                value=bool(st.session_state.get("notifications_faults", True)),
                key="notifications_faults",
            )
            st.checkbox(
                t("Email alerts", "E-mail alerts"),
                value=bool(st.session_state.get("notifications_email", True)),
                key="notifications_email",
            )
            st.checkbox(
                t("Push notifications", "Push notificaties"),
                value=bool(st.session_state.get("notifications_push", False)),
                key="notifications_push",
            )
            if st.button(t("Save", "Opslaan"), key="account_save_notifications",
                         width="stretch", type="primary"):
                if not is_guest:
                    persist_active_user_state()
                st.toast(t("Notification settings saved.", "Meldingsinstellingen opgeslagen."), icon="✅")

        # ─── 📊 Overzicht ─────────────────────────────────────────────
        elif acct_section == "overzicht":
            st.subheader("📊 " + t("Overview", "Overzicht"))
            disconnect_events = 0
            for _ev in st.session_state.get("event_history", []):
                if isinstance(_ev, dict) and _ev.get("type") == "Connection":
                    _msg = str(_ev.get("message", "")).lower()
                    if "disconnect" in _msg or "verbroken" in _msg:
                        disconnect_events += 1
            uptime_pct = max(0.0, min(100.0, 100.0 - (disconnect_events * 3.0)))
            energy_candidates = []
            df_local = st.session_state.get("df", pd.DataFrame())
            if isinstance(df_local, pd.DataFrame):
                for _i in range(1, machines + 1):
                    _col = f"current_{_i}"
                    if _col in df_local.columns and not df_local[_col].dropna().empty:
                        avg_amp = float(pd.to_numeric(df_local[_col], errors="coerce").fillna(0.0).mean())
                        energy_candidates.append((avg_amp * 230.0) / 1000.0)
            est_energy_kw = float(np.mean(energy_candidates)) if energy_candidates else 0.0
            fault_count = int(anomalies_total + bottlenecks_total)
            ov1, ov2, ov3 = st.columns(3)
            ov1.metric(t("Uptime", "Uptime"), f"{uptime_pct:.1f}%")
            ov2.metric(t("Energy use", "Energieverbruik"), f"{est_energy_kw:.2f} kW")
            ov3.metric(t("Fault count", "Aantal storingen"), str(fault_count))

        # ─── ⚙️ Instellingen ──────────────────────────────────────────
        elif acct_section == "instellingen":
            st.subheader("⚙️ " + t("Settings", "Instellingen"))
            st.selectbox(
                t("Theme", "Thema"),
                ["Dark", "Light"],
                index=0 if st.session_state.get("theme_preference", "Dark") == "Dark" else 1,
                key="theme_preference",
            )
            st.selectbox(
                t("Language", "Taal"),
                ["EN", "NL"],
                index=0 if st.session_state.get("language", "EN") == "EN" else 1,
                key="language",
            )
            if st.button(t("Save settings", "Instellingen opslaan"), key="account_save_preferences",
                         width="stretch", type="primary"):
                if not is_guest:
                    persist_active_user_state()
                st.toast(t("Settings saved.", "Instellingen opgeslagen."), icon="✅")
            st.divider()
            st.subheader("🔐 " + t("Security", "Beveiliging"))
            pw_col1, pw_col2 = st.columns(2)
            with pw_col1:
                st.text_input(
                    t("Current password", "Huidig wachtwoord"), type="password", key="account_current_password")
            with pw_col2:
                st.text_input(
                    t("New password", "Nieuw wachtwoord"), type="password", key="account_new_password")
            if st.button(t("Change password", "Wachtwoord wijzigen"), key="account_change_password",
                         width="stretch"):
                _cur_pw = st.session_state.get("account_current_password", "")
                _new_pw = st.session_state.get("account_new_password", "")
                if is_guest:
                    st.error(t("Please log in first.", "Log eerst in."))
                elif len(_new_pw or "") < 6:
                    st.error(t("New password must be at least 6 characters.",
                               "Nieuw wachtwoord moet minimaal 6 tekens hebben."))
                else:
                    _db = load_user_db()
                    _user_record = _db.get("users", {}).get(current_user)
                    if not _user_record:
                        st.error(t("User not found.", "Gebruiker niet gevonden."))
                    else:
                        _salt_hex = _user_record.get("salt", "")
                        _current_hash = _user_record.get("password_hash", "")
                        if not _salt_hex or hash_password(_cur_pw, _salt_hex) != _current_hash:
                            st.error(t("Current password is incorrect.", "Huidig wachtwoord is onjuist."))
                        else:
                            _new_salt = secrets.token_hex(16)
                            _user_record["salt"] = _new_salt
                            _user_record["password_hash"] = hash_password(_new_pw, _new_salt)
                            _db["users"][current_user] = _user_record
                            save_user_db(_db)
                            st.session_state.account_current_password = ""
                            st.session_state.account_new_password = ""
                            st.toast(t("Password changed.", "Wachtwoord gewijzigd."), icon="🔐")
                            log_event("Account", f"Password changed for user {current_user}")

        # ─── 💳 Abonnement ────────────────────────────────────────────
        elif acct_section == "abonnement":
            st.subheader("💳 " + t("Subscription", "Abonnement"))
            st.selectbox(
                t("Current plan", "Huidig plan"),
                ["Starter", "Pro", "Enterprise"],
                index=["Starter", "Pro", "Enterprise"].index(st.session_state.get("subscription_plan", "Starter"))
                if st.session_state.get("subscription_plan", "Starter") in ["Starter", "Pro", "Enterprise"] else 0,
                key="subscription_plan",
            )
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                if st.button(t("Upgrade", "Upgrade"), key="account_upgrade_plan",
                             width="stretch", type="primary"):
                    _cur_plan = st.session_state.get("subscription_plan", "Starter")
                    _new_plan = ("Pro" if _cur_plan == "Starter"
                                 else "Enterprise" if _cur_plan == "Pro" else _cur_plan)
                    st.session_state.subscription_plan = _new_plan
                    if not is_guest:
                        persist_active_user_state()
                    st.toast(t("Plan upgraded.", "Plan geupgrade."), icon="🚀")
                    st.rerun()
            with sub_col2:
                if st.button(t("Save plan", "Plan opslaan"), key="account_save_plan",
                             width="stretch"):
                    if not is_guest:
                        persist_active_user_state()
                    st.toast(t("Plan saved.", "Plan opgeslagen."), icon="✅")
            invoice_df = pd.DataFrame(st.session_state.get("invoice_history", []))
            if not invoice_df.empty:
                st.divider()
                st.caption(t("Invoices", "Facturen"))
                st.dataframe(invoice_df, width="stretch")

        # ─── 🛠️ Support ───────────────────────────────────────────────
        elif acct_section == "support":
            st.subheader("🛠️ " + t("Support", "Support"))
            st.write(t(
                "Need help? Our support team is ready to assist you.",
                "Hulp nodig? Ons supportteam staat klaar om je te helpen."
            ))
            if st.button(t("Go to Contact", "Naar Contact"), key="account_support_contact",
                         width="stretch", type="primary"):
                st.session_state.page = "Contact"
                st.rerun()

        # ─── 🚪 Uitloggen ─────────────────────────────────────────────
        elif acct_section == "uitloggen":
            st.subheader("🚪 " + t("Logout", "Uitloggen"))
            st.write(t(
                "You will be logged out and returned to the login screen.",
                "Je wordt uitgelogd en teruggestuurd naar het inlogscherm."
            ))
            if st.button("↩ " + t("Logout", "Uitloggen"), width="stretch",
                         key="account_logout_bottom", type="secondary"):
                perform_logout()

elif page == "Settings":
    st.title(t("⚙ Settings", "⚙ Instellingen"))
    connected_count = len(st.session_state.get('connected_devices', []))
    mode_label = st.session_state.get('mode', 'Simulation')
    device_label = t("Connected", "Verbonden") if st.session_state.get('device_connected', False) else t("Not connected", "Niet verbonden")

    st.markdown(
        f"""
        <div class="settings-hero">
            <div class="settings-hero-title">{t('Control Center', 'Controlecentrum')}</div>
            <div class="settings-hero-sub">{t('Manage mode, language, machines, cloud bridge and device connection in one place.', 'Beheer modus, taal, machines, cloud bridge en apparaatverbinding op één plek.')}</div>
            <div style="margin-top:10px;">
                <span class="settings-chip">{t('Mode', 'Modus')}: {mode_label}</span>
                <span class="settings-chip">{t('Devices', 'Apparaten')}: {connected_count}</span>
                <span class="settings-chip">{t('Status', 'Status')}: {device_label}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    settings_tabs = [
        ("general", "⚙ " + t("General", "Algemeen")),
        ("cloud", "☁ " + t("Cloud", "Cloud")),
        ("device", "📡 " + t("Device", "Apparaat")),
        ("account", "👤 " + t("Account", "Account")),
    ]
    settings_tab_labels = {tab_key: tab_label for tab_key, tab_label in settings_tabs}
    settings_tab_keys = list(settings_tab_labels.keys())

    if st.session_state.get("settings_active_tab") not in settings_tab_keys:
        st.session_state.settings_active_tab = "general"

    st.caption(t("Choose a section", "Kies een sectie"))
    tab_cols = st.columns(4)
    for idx, tab_key in enumerate(settings_tab_keys):
        with tab_cols[idx]:
            is_active = st.session_state.get("settings_active_tab") == tab_key
            if st.button(
                settings_tab_labels[tab_key],
                key=f"settings_top_tab_{tab_key}",
                width="stretch",
                type="primary" if is_active else "secondary",
            ):
                st.session_state.settings_active_tab = tab_key
                st.rerun()

    settings_active_tab = st.session_state.get("settings_active_tab", "general")

    if settings_active_tab == "general":
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.subheader(t("Mode", "Modus"))

        is_live_locked = connected_count > 0 and st.session_state.get('mode') == 'Live'
        if is_live_locked:
            st.success(t(
                f"Live mode is active with {connected_count} connected device(s).",
                f"Live modus is actief met {connected_count} verbonden apparaat/apparaten."
            ))
        else:
            current_mode = st.session_state.get('mode', 'Simulation')
            mode_choice = st.radio(
                t("Select mode", "Kies modus"),
                [t('Simulation', 'Simulatie'), t('Live', 'Live')],
                index=1 if current_mode == 'Live' else 0,
                horizontal=True,
                key="settings_mode_radio"
            )
            chosen = 'Live' if mode_choice == 'Live' else 'Simulation'

            if chosen == 'Live' and not st.session_state.get('device_connected', False):
                if st.button(t("Connect a device first", "Verbind eerst een apparaat"), type="primary"):
                    st.session_state.page = "Device Connection"
                    st.session_state.pending_mode = 'Live'
                    st.rerun()
            elif chosen == 'Live':
                st.session_state.mode = 'Live'
            else:
                st.session_state.mode = 'Simulation'
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.subheader(t("Language & Simulation", "Taal & Simulatie"))

        if 'language' not in st.session_state:
            st.session_state.language = 'EN'

        gen_col1, gen_col2 = st.columns(2)
        with gen_col1:
            lang = st.selectbox("Language / Taal", ['EN', 'NL'], index=0 if st.session_state.language == 'EN' else 1)
            st.session_state.language = lang
        with gen_col2:
            st.session_state.refresh_rate = st.slider(
                t("Data update interval (seconds)", "Data update interval (seconden)"),
                1,
                5,
                max(1, int(st.session_state.refresh_rate))
            )

        live_single_lock = connected_count > 0 and st.session_state.get('mode') == 'Live'
        if live_single_lock:
            st.info(t(
                f"Dashboards are locked to {connected_count} machine(s) while live devices are connected.",
                f"Dashboards staan vast op {connected_count} machine(s) zolang live devices verbonden zijn."
            ))

        new_machines = st.slider(
            t("Number of Machines", "Aantal machines"),
            1,
            10,
            st.session_state.num_machines,
            disabled=live_single_lock,
        )

        if new_machines != st.session_state.num_machines:
            st.session_state.num_machines = new_machines
            st.session_state.machine_names = [f"Machine {i}" for i in range(1, new_machines+1)]
            data = {
                f"current_{i}": np.zeros(50)
                for i in range(1, new_machines + 1)
            }
            st.session_state.df = pd.DataFrame(data)
            st.session_state.df["timestamp"] = pd.date_range(
                end=pd.Timestamp.now(),
                periods=len(st.session_state.df),
                freq=f"{int(st.session_state.refresh_rate)}s",
            )
            st.session_state.last_current_values = {
                f"current_{i}": 0.0 for i in range(1, new_machines + 1)
            }
            st.success(t("Simulation updated.", "Simulatie bijgewerkt."))

        st.caption(t("Machine Names", "Machine namen"))
        for i in range(st.session_state.num_machines):
            st.session_state.machine_names[i] = st.text_input(
                f"Machine {i+1}",
                value=st.session_state.machine_names[i]
            )
        st.markdown('</div>', unsafe_allow_html=True)

    if settings_active_tab == "cloud":
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.subheader(t("Cloud Bridge (Remote Access)", "Cloud Bridge (Remote toegang)"))
        st.caption(t(
            "Use this if your ESP32 pushes data to a public server so you can view machine data from anywhere.",
            "Gebruik dit als je ESP32 data naar een publieke server stuurt, zodat je overal machinegegevens kunt zien."
        ))

        st.session_state.cloud_bridge_enabled = st.checkbox(
            t("Enable cloud bridge fallback", "Cloud bridge fallback inschakelen"),
            value=bool(st.session_state.get("cloud_bridge_enabled", False)),
            key="settings_cloud_bridge_enabled",
        )
        st.session_state.cloud_bridge_max_age_s = st.slider(
            t("Max cloud data age (seconds)", "Max cloud data leeftijd (seconden)"),
            10,
            3600,
            int(st.session_state.get("cloud_bridge_max_age_s", 300)),
            key="settings_cloud_bridge_max_age_s",
        )
        cloud_base_input = st.text_input(
            t("Public bridge URL", "Publieke bridge URL"),
            value=st.session_state.get("cloud_bridge_public_base_url", ""),
            placeholder="https://your-server.example.com",
            key="settings_cloud_bridge_base_url",
        )
        st.session_state.cloud_bridge_public_base_url = (cloud_base_input or "").strip().rstrip("/")
        st.session_state.cloud_bridge_api_key = st.text_input(
            t("Bridge API key", "Bridge API sleutel"),
            value=st.session_state.get("cloud_bridge_api_key", "change-me"),
            type="password",
            key="settings_cloud_bridge_api_key",
        )

        bridge_base = st.session_state.get("cloud_bridge_public_base_url", "")
        if bridge_base:
            ingest_url = f"{bridge_base}/ingest"
            st.code(
                f"POST {ingest_url}\nHeader: x-api-key: <API_KEY>\nJSON body: {{\"current\": 2.1, \"voltage\": 230.5}}",
                language="text",
            )
        st.markdown('</div>', unsafe_allow_html=True)

    if settings_active_tab == "device":
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.subheader(t("Device Connection", "Apparaatverbinding"))

        if st.session_state.get('device_connected', False):
            st.success(t("Device Connected", "Apparaat verbonden"))
            st.info(t("Device is ready for Live mode", "Apparaat is klaar voor Live modus"))
            if st.session_state.get('device_endpoint'):
                st.caption(f"Endpoint: {st.session_state.get('device_endpoint')}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(t("Reconnect Device", "Herverbind apparaat"), width="stretch"):
                    st.session_state.page = "Device Connection"
                    st.session_state.pending_mode = 'Live'
                    st.rerun()
            with col2:
                if st.button(t("Disconnect Device", "Apparaat verbreken"), type="secondary", width="stretch"):
                    clear_device_connection_state()
                    if st.session_state.get('mode') == 'Live':
                        st.session_state.mode = 'Simulation'
                    log_event("Connection", "Device disconnected from Settings - Switched to Simulation mode")
                    st.success(t("Device disconnected", "Apparaat verbroken"))
                    st.rerun()
        else:
            st.warning(t("No Device Connected", "Geen apparaat verbonden"))

            if st.button(t("Connect Device", "Verbind apparaat"), width="stretch", type="primary"):
                st.session_state.page = "Device Connection"
                st.session_state.pending_mode = 'Live'
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if settings_active_tab == "account":
        account_current_user = st.session_state.get("auth_user")
        account_is_guest = not account_current_user
        account_acct_section = st.session_state.get("settings_account_section", "profiel")

        if account_is_guest:
            st.warning(t(
                "You are using a guest account. Log in to save your settings permanently.",
                "Je gebruikt een gastaccount. Log in om je instellingen permanent op te slaan."
            ))
        else:
            _pname = st.session_state.get("profile_name", "") or account_current_user
            _initials = "".join(word[0].upper() for word in _pname.split()[:2]) if _pname else "?"
            _company = st.session_state.get("profile_company", "")
            _company_html = f'<span style="color:#64748b;font-size:0.85rem;">— {_company}</span>' if _company else ""
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(130deg, rgba(15,23,42,0.96) 0%, rgba(17,24,39,0.96) 55%, rgba(37,99,235,0.18) 100%);
                    border: 1px solid rgba(59,130,246,0.18);
                    border-radius: 20px;
                    padding: 20px 24px;
                    margin-bottom: 18px;
                    display:flex;align-items:center;gap:18px;
                    box-shadow: 0 4px 24px rgba(2,8,23,0.24), inset 0 1px 0 rgba(148,163,184,0.06);
                ">
                    <div style="
                        width:52px;height:52px;border-radius:50%;flex-shrink:0;
                        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.25rem;font-weight:800;color:#fff;
                        box-shadow: 0 2px 12px rgba(37,99,235,0.4);
                    ">{_initials}</div>
                    <div>
                        <div style="font-size:1.15rem;font-weight:700;color:#f1f5f9;line-height:1.2;">
                            {_pname} {_company_html}
                        </div>
                        <div style="margin-top:6px;display:flex;gap:6px;flex-wrap:wrap;">
                            <span class="settings-chip" style="font-size:0.78rem;">🌐 {st.session_state.get('language', 'EN')}</span>
                            <span class="settings-chip" style="font-size:0.78rem;">💳 {st.session_state.get('subscription_plan', 'Starter')}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        _acct_sections = [
            ("profiel", "👤 " + t("Profile", "Profiel")),
            ("meldingen", "🔔 " + t("Notifications", "Meldingen")),
            ("abonnement", "💳 " + t("Subscription", "Abonnement")),
            ("support", "🛠️ " + t("Support", "Support")),
        ]
        if not account_is_guest:
            _acct_sections.append(("uitloggen", "🚪 " + t("Logout", "Uitloggen")))

        nav_col, content_col = st.columns([1, 3], gap="medium")

        with nav_col:
            st.markdown('<span class="acct-nav-marker"></span><span class="acct-nav-label">Menu</span>', unsafe_allow_html=True)
            for _key, _label in _acct_sections:
                _is_active = account_acct_section == _key
                if st.button(
                    _label,
                    key=f"settings_acct_nav_{_key}",
                    width="stretch",
                    type="primary" if _is_active else "secondary",
                ):
                    st.session_state.settings_account_section = _key
                    st.rerun()

        with content_col:
            st.markdown('<span class="acct-content-marker"></span>', unsafe_allow_html=True)

            if account_acct_section == "profiel":
                settings_profile_editing = bool(st.session_state.get("settings_profile_editing", False))
                st.subheader("👤 " + t("Profile", "Profiel"))
                st.text_input(t("Name", "Naam"), value=st.session_state.get("profile_name", ""), key="profile_name", disabled=not settings_profile_editing)
                st.text_input(t("Email", "E-mail"), value=st.session_state.get("profile_email", ""), key="profile_email", disabled=not settings_profile_editing)
                st.text_input(t("Company", "Bedrijf"), value=st.session_state.get("profile_company", ""), key="profile_company", disabled=not settings_profile_editing)
                if not settings_profile_editing:
                    if st.button(t("Change", "Wijzigen"), key="settings_account_edit_details", width="stretch", type="primary"):
                        st.session_state.settings_profile_editing = True
                        st.rerun()
                elif st.button(t("Save changes", "Wijzigingen opslaan"), key="settings_account_save_details", width="stretch", type="primary"):
                    st.session_state.settings_profile_editing = False
                    if account_is_guest:
                        st.toast(t("Log in to save permanently.", "Log in om permanent op te slaan."), icon="ℹ️")
                    else:
                        persist_active_user_state()
                        st.toast(t("Profile saved.", "Profiel opgeslagen."), icon="✅")
                    st.rerun()

            elif account_acct_section == "meldingen":
                st.subheader("🔔 " + t("Notifications", "Meldingen"))
                st.checkbox(
                    t("Fault notifications", "Storingsmeldingen"),
                    value=bool(st.session_state.get("notifications_faults", True)),
                    key="notifications_faults",
                )
                st.checkbox(
                    t("Email alerts", "E-mail alerts"),
                    value=bool(st.session_state.get("notifications_email", True)),
                    key="notifications_email",
                )
                st.checkbox(
                    t("Push notifications", "Push notificaties"),
                    value=bool(st.session_state.get("notifications_push", False)),
                    key="notifications_push",
                )
                if st.button(t("Save", "Opslaan"), key="settings_account_save_notifications", width="stretch", type="primary"):
                    if account_is_guest:
                        st.toast(t("Log in to save permanently.", "Log in om permanent op te slaan."), icon="ℹ️")
                    else:
                        persist_active_user_state()
                        st.toast(t("Notification settings saved.", "Meldingsinstellingen opgeslagen."), icon="✅")

            elif account_acct_section == "abonnement":
                st.subheader("💳 " + t("Subscription", "Abonnement"))
                st.selectbox(
                    t("Current plan", "Huidig plan"),
                    ["Starter", "Pro", "Enterprise"],
                    index=["Starter", "Pro", "Enterprise"].index(st.session_state.get("subscription_plan", "Starter"))
                    if st.session_state.get("subscription_plan", "Starter") in ["Starter", "Pro", "Enterprise"] else 0,
                    key="subscription_plan",
                )
                sub_col1, sub_col2 = st.columns(2)
                with sub_col1:
                    if st.button(t("Upgrade", "Upgrade"), key="settings_account_upgrade_plan", width="stretch", type="primary"):
                        _cur_plan = st.session_state.get("subscription_plan", "Starter")
                        _new_plan = "Pro" if _cur_plan == "Starter" else "Enterprise" if _cur_plan == "Pro" else _cur_plan
                        st.session_state.subscription_plan = _new_plan
                        if account_is_guest:
                            st.toast(t("Log in to save permanently.", "Log in om permanent op te slaan."), icon="ℹ️")
                        else:
                            persist_active_user_state()
                            st.toast(t("Plan upgraded.", "Plan geupgrade."), icon="🚀")
                with sub_col2:
                    if st.button(t("Save plan", "Plan opslaan"), key="settings_account_save_plan", width="stretch"):
                        if account_is_guest:
                            st.toast(t("Log in to save permanently.", "Log in om permanent op te slaan."), icon="ℹ️")
                        else:
                            persist_active_user_state()
                            st.toast(t("Plan saved.", "Plan opgeslagen."), icon="✅")
                invoice_df = pd.DataFrame(st.session_state.get("invoice_history", []))
                if not invoice_df.empty:
                    st.divider()
                    st.caption(t("Invoices", "Facturen"))
                    st.dataframe(invoice_df, width="stretch")

            elif account_acct_section == "support":
                st.subheader("🛠️ " + t("Support", "Support"))
                st.write(t(
                    "Need help? Our support team is ready to assist you.",
                    "Hulp nodig? Ons supportteam staat klaar om je te helpen."
                ))
                if st.button(t("Go to Contact", "Naar Contact"), key="settings_account_support_contact", width="stretch", type="primary"):
                    st.session_state.page = "Contact"
                    st.rerun()

            elif account_acct_section == "uitloggen" and not account_is_guest:
                st.subheader("🚪 " + t("Logout", "Uitloggen"))
                st.write(t(
                    "You will be logged out and returned to the login screen.",
                    "Je wordt uitgelogd en teruggestuurd naar het inlogscherm."
                ))
                if st.button("↩ " + t("Logout", "Uitloggen"), width="stretch", key="settings_account_logout_bottom", type="secondary"):
                    perform_logout()

        if account_is_guest:
            st.divider()
            login_tab, register_tab = st.tabs([
                t("Login", "Inloggen"),
                t("Create Account", "Account Maken"),
            ])

            with login_tab:
                login_user = st.text_input(t("Username", "Gebruikersnaam"), key="settings_auth_login_user")
                login_pass = st.text_input(t("Password", "Wachtwoord"), type="password", key="settings_auth_login_pass")
                if st.button(t("Login", "Inloggen"), key="settings_auth_login_btn", type="primary", width="stretch"):
                    if not login_user or not login_pass:
                        st.error(t("Please enter both username and password.", "Voer gebruikersnaam en wachtwoord in."))
                    elif authenticate_user(login_user, login_pass):
                        st.session_state.auth_user = login_user.strip().lower()
                        st.session_state.auth_loaded_user = st.session_state.auth_user
                        remember_token = set_user_remember_token(st.session_state.auth_user)
                        if remember_token:
                            st.query_params["auth"] = remember_token
                        db = load_user_db()
                        user_state = db.get("users", {}).get(st.session_state.auth_user, {}).get("state", {})
                        apply_user_state(user_state)
                        send_login_email(st.session_state.auth_user)
                        st.rerun()
                    else:
                        st.error(t("Invalid username or password.", "Onjuiste gebruikersnaam of wachtwoord."))

            with register_tab:
                st.write(t("Create your account and fill in your profile details.", "Maak je account en vul je profielgegevens in."))
                st.divider()
                st.subheader(t("Account", "Account"))
                reg_user = st.text_input(t("Username", "Gebruikersnaam"), key="settings_auth_register_user")
                reg_pass = st.text_input(t("Password (min 6 chars)", "Wachtwoord (min 6 tekens)"), type="password", key="settings_auth_register_pass")
                st.divider()
                st.subheader("👤 " + t("Profile", "Profiel"))
                prof_name = st.text_input(t("Full name", "Volledig naam"), key="settings_auth_register_name")
                prof_email = st.text_input(t("Email", "E-mail"), key="settings_auth_register_email")
                prof_company = st.text_input(t("Company", "Bedrijf"), key="settings_auth_register_company")
                st.divider()
                if st.button(t("Create Account", "Account Aanmaken"), key="settings_auth_register_btn", type="primary", width="stretch"):
                    ok, message = register_user(reg_user, reg_pass, prof_name, prof_email, prof_company)
                    if ok:
                        st.rerun()
                    else:
                        st.error(message)

elif page=="AI Insights":
    st.title(t("⌬ AI Insights & Recommendations", "⌬ AI Inzichten & Aanbevelingen"))

    st.markdown(
        f"""
        <div class="page-hero">
            <p class="page-hero-title">{t('AI-assisted machine review', 'AI-ondersteunde machinebeoordeling')}</p>
            <p class="page-hero-sub">{t('This section uses AI-driven logic to analyze machine behavior, detect risks and suggest practical next actions.', 'Deze sectie gebruikt AI-logica om machinegedrag te analyseren, risico’s te detecteren en praktische vervolgstappen voor te stellen.')}</p>
            <span class="page-chip">{t('Anomalies', 'Afwijkingen')}: {len(st.session_state.anomalies)}</span>
            <span class="page-chip">{t('Bottlenecks', 'Knelpunten')}: {len(st.session_state.bottlenecks)}</span>
            <span class="page-chip">{t('Machines', 'Machines')}: {NUM_MACHINES}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Overview KPIs ---
    st.markdown('<div class="page-section">', unsafe_allow_html=True)
    st.subheader(t("⌗ Key Performance Indicators", "⌗ Belangrijke Prestatie-indicatoren"))
    st.markdown(t(
        "These KPIs give you a quick overview of factory health:\n- **Anomalies** = Unexpected machine behaviors detected\n- **Bottlenecks** = Machines slowing down production\n- **Avg Load** = Average power consumption right now",
        "Deze KPI's geven je snel inzicht in fabrieksgezondheid:\n- **Afwijkingen** = Onverwacht machinegedrag\n- **Knelpunten** = Machines die productie bremmen\n- **Gem. Belasting** = Gemiddeld stroomverbruik nu"
    ))
    col1, col2, col3 = st.columns(3)
    total_anomalies = len(st.session_state.anomalies)
    total_bottlenecks = len(st.session_state.bottlenecks)
    avg_candidates = []
    for i in range(1, NUM_MACHINES + 1):
        col = f"current_{i}"
        if col in df.columns and not df[col].dropna().empty:
            avg_candidates.append(float(df[col].mean()))
    avg_load = float(np.mean(avg_candidates)) if avg_candidates else 0.0

    col1.metric(t("Anomalies Detected", "Afwijkingen"), total_anomalies)
    col2.metric(t("Bottlenecks", "Knelpunten"), total_bottlenecks)
    col3.metric(t("Avg Load (A)", "Gem. Belasting (A)"), f"{avg_load:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)


    # --- Machine Level AI Analysis ---
    st.markdown('<div class="page-section">', unsafe_allow_html=True)
    st.subheader(t("⌬ Machine Intelligence Analysis", "⌬ Machine Analyse"))
    st.markdown(t(
        "**What this shows:** Each machine is analyzed with these metrics:\n- **Current** = Amperage RIGHT NOW\n- **Avg** = Average over all time\n- **Peak** = Highest power ever used\n- **Anomaly Score** = How unusual the current reading is (higher = more unusual)\n- **Trend** = Is usage going up or down?\n- **Status** = Health assessment",
        "**Wat dit toont:** Elke machine wordt geanalyseerd op:\n- **Huidig** = Ampère RECHTS NU\n- **Gemiddeld** = Gemiddelde over tijd\n- **Piek** = Hoogste stroom ooit\n- **Afwijkingsscore** = Hoe ongewoon is de huidige meting? (hoger = vreemder)\n- **Trend** = Gaat gebruik omhoog of omlaag?\n- **Status** = Gezondheid"
    ))

    insights = []

    for i in range(1, NUM_MACHINES+1):
        col = f"current_{i}"
        series = df[col].dropna() if col in df.columns else pd.Series(dtype="float64")

        if series.empty:
            cur = 0.0
            avg = 0.0
            peak = 0.0
            std = 1.0
            anomaly_score = 0.0
            trend_machine = 0.0
        else:
            cur = float(series.iloc[-1])
            avg = float(series.mean())
            peak = float(series.max())
            std_raw = float(series.std()) if not np.isnan(series.std()) else 0.0
            std = std_raw if std_raw > 0 else 1.0
            anomaly_score = abs(cur - avg) / std

            if len(series) > 5:
                trend_machine = float(np.polyfit(range(len(series)), series.to_numpy(dtype=float), 1)[0])
            else:
                trend_machine = 0.0

        prediction = t("Stable", "Stabiel")
        if trend_machine > 0.05:
            prediction = t("Increasing load", "Stijgende belasting")
        elif trend_machine < -0.05:
            prediction = t("Decreasing load", "Dalende belasting")

        status = t("Normal", "Normaal")
        advice = t("Operating within expected parameters.", "Werkt binnen normale parameters.")
        severity = "success"

        if anomaly_score > 2.5:
            status = t("Anomaly Detected", "Afwijking Gedetecteerd")
            advice = t("Unexpected behavior detected. Inspect machine.", "Onverwacht gedrag. Controleer machine.")
            severity = "error"
        elif cur > 6:
            status = t("Overload Risk", "Overbelasting risico")
            advice = t("Reduce load or inspect machine for mechanical stress.", "Verlaag belasting of controleer machine op slijtage.")
            severity = "error"
        elif cur < 0.5:
            status = t("Idle", "Inactief")
            advice = t("Consider powering down to save energy.", "Overweeg uitschakelen om energie te besparen.")
            severity = "warning"
        elif avg > 4:
            status = t("High Usage", "Hoge belasting")
            advice = t("Monitor efficiency and cooling systems.", "Controleer efficiëntie en koeling.")
            severity = "warning"

        # Track anomalies and bottlenecks in state for repeatable insights
        if severity == "error" or anomaly_score > 2.5:
            anomaly_msg = f"M{i}:{status}:{anomaly_score:.2f}"
            st.session_state.anomalies.append(anomaly_msg)
            log_event("Anomaly", f"Machine {i} - {status} (Score: {anomaly_score:.2f})")
        if severity == "warning" and avg > 4:
            bottleneck_msg = f"M{i}:{avg:.2f}"
            st.session_state.bottlenecks.append(bottleneck_msg)
            log_event("Bottleneck", f"Machine {i} - High Load ({avg:.2f}A)")


        insights.append({
            "Machine": f"M{i}",
            "Current": round(cur,2),
            "Avg": round(avg,2),
            "Peak": round(peak,2),
            "Status": status,
            "Advice": advice,
            "AnomalyScore": round(anomaly_score,2),
            "Trend": round(trend_machine,3),
            "Prediction": prediction,
        })

        if severity == "error":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.error(f"M{i} → {status}: {advice} | Score: {anomaly_score:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        elif severity == "warning":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.warning(f"M{i} → {status}: {advice} | Score: {anomaly_score:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.success(f"M{i} → {status} | Score: {anomaly_score:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # --- Table Overview ---
    st.subheader(t("⌗ AI Summary Table", "⌗ AI Overzicht"))
    st.markdown(t(
        "**Table explanation:**\n- **Current/Avg/Peak** = Power readings in Amperes\n- **Status** = Health: Normal, Anomaly, Overload, Idle, or High Usage\n- **Advice** = What you should do about this machine\n- **AnomalyScore** = Deviation from normal (0.0 = normal, >2.5 = suspicious)\n- **Trend** = Direction: positive (↑) = more usage, negative (↓) = less usage",
        "**Tabel uitleg:**\n- **Huidig/Gem/Piek** = Stroommetingen in Ampère\n- **Status** = Gezondheid: Normaal, Afwijking, Overbelasting, Inactief, Hoge belasting\n- **Advies** = Wat je moet doen met dit machine\n- **Afwijkingsscore** = Afwijking van normaal (0.0 = normaal, >2.5 = verdacht)\n- **Trend** = Richting: positief (↑) = meer gebruik, negatief (↓) = minder gebruik"
    ))

    pause_key = 'pause_ai_table'
    if pause_key not in st.session_state:
        st.session_state[pause_key] = False
    if 'ai_insights_snapshot' not in st.session_state:
        st.session_state['ai_insights_snapshot'] = None

    if st.button(t("Start / Stop section updates", "Start / Stop sectie-updates"), key="btn_toggle_ai"):
        st.session_state[pause_key] = not st.session_state[pause_key]

    st.write(t(
        f"Section updates are currently {'paused' if st.session_state[pause_key] else 'running'}.",
        f"Sectie-updates zijn momenteel {'gepauzeerd' if st.session_state[pause_key] else 'actief'}."
    ))

    insights_df = pd.DataFrame(insights)
    if st.session_state[pause_key] and st.session_state.get('ai_insights_snapshot') is not None:
        insights_df = st.session_state['ai_insights_snapshot']
    else:
        st.session_state['ai_insights_snapshot'] = insights_df

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(insights_df, width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- System Health Score ---
    st.subheader(t("⚙ System Health Score", "⚙ Systeem Gezondheid"))
    st.markdown(t(
        "**What this means:** A score from 0-100% showing overall factory health. Calculated from power consumption and detected problems. Higher = healthier!",
        "**Wat dit betekent:** Een score van 0-100% die fabrieksgezondheid toont. Berekend uit stroomverbruik en gevonden problemen. Hoger = gezonder!"
    ))
    health = max(0, 100 - (avg_load * 10) - (total_anomalies * 5))
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.metric(t("Health Score", "Gezondheidsscore"), f"{health:.0f}%")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Smart Recommendations ---
    st.subheader(t("☰ Smart Recommendations", "☰ Slimme Aanbevelingen"))
    st.markdown(t(
        "**How this works:** The AI looks at your data and suggests actions to improve your factory. Here's what to do:",
        "**Hoe dit werkt:** De AI kijkt naar je data en geeft suggesties om je fabriek beter te maken. Hier is wat je kunt doen:"
    ))

    if total_anomalies > 5:
        st.error(t("High anomaly rate detected. Perform system diagnostics.", "Veel afwijkingen gedetecteerd. Voer systeemcontrole uit."))
    elif total_bottlenecks > 3:
        st.warning(t("Multiple bottlenecks detected. Optimize production flow.", "Meerdere knelpunten gedetecteerd. Optimaliseer productie."))
    elif avg_load > 4:
        st.warning(t("Factory running at high load. Risk of inefficiency.", "Fabriek draait zwaar belast. Risico op inefficiëntie."))
    else:
        st.success(t("Factory is operating efficiently.", "Fabriek draait efficiënt."))

    # --- Predictive Insight (simple AI simulation) ---
    st.subheader(t("⌬ Predictive Insight", "⌬ Voorspellende Inzichten"))
    st.markdown(t(
        "**What this does:** The AI looks at recent trends and predicts what might happen next:\n- **Upward trend** = Usage is increasing, might overload soon\n- **Downward trend** = Usage is decreasing, machines slowing down\n- **Stable** = Things are normal, no major changes expected",
        "**Wat dit doet:** De AI kijkt naar recente trends en voorspelt wat volgt:\n- **Stijgende trend** = Gebruik neemt toe, mogelijk overbelasting binnenkort\n- **Dalende trend** = Gebruik neemt af, machines worden minder druk\n- **Stabiel** = Alles normaal, geen grote veranderingen verwacht"
    ))
    if len(df) > 2:
        trend_columns = [f"current_{i}" for i in range(1, NUM_MACHINES+1) if f"current_{i}" in df.columns]
        trend_series = (
            df[trend_columns].to_numpy(dtype=float).mean(axis=1)
            if trend_columns
            else np.zeros(len(df), dtype=float)
        )
        trend = np.polyfit(
            range(len(df)),
            trend_series,
            1
        )[0]
    else:
        trend = 0

    if trend > 0.05:
        st.warning(t("Upward trend detected → possible overload in near future.", "Stijgende trend → mogelijke overbelasting binnenkort."))
    elif trend < -0.05:
        st.info(t("Downward trend detected → decreasing usage.", "Dalende trend → minder gebruik."))
    else:
        st.success(t("Stable usage trend.", "Stabiele trend."))

elif page == "History":
    st.title(t("⚙ Event History", "⚙ Gebeurenissen Geschiedenis"))
    total_events = len(st.session_state.event_history)
    anomaties_count = len([e for e in st.session_state.event_history if e.get("type") == "Anomaly"])
    bottleneck_count = len([e for e in st.session_state.event_history if e.get("type") == "Bottleneck"])
    connection_count = len([e for e in st.session_state.event_history if e.get("type") == "Connection"])

    st.markdown(
        f"""
        <div class="history-hero">
            <p class="history-hero-title">{t('Operational event history', 'Operationele gebeurtenissengeschiedenis')}</p>
            <p class="history-hero-sub">{t('Review anomalies, bottlenecks, device actions and system activity in one timeline.', 'Bekijk afwijkingen, knelpunten, apparaatacties en systeemactiviteit in één tijdlijn.')}</p>
            <span class="history-chip">{t('Total', 'Totaal')}: {total_events}</span>
            <span class="history-chip">{t('Anomalies', 'Afwijkingen')}: {anomaties_count}</span>
            <span class="history-chip">{t('Bottlenecks', 'Knelpunten')}: {bottleneck_count}</span>
            <span class="history-chip">{t('Connections', 'Verbindingen')}: {connection_count}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Filter options
    st.markdown('<div class="history-section">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_type = st.multiselect(
            t("Filter by type", "Filter op type"),
            ["All", "Anomaly", "Bottleneck", "Connection", "System"],
            default=["All"],
            key="history_filter_type"
        )
    with col2:
        sort_option = st.selectbox(
            t("Sort", "Sorteren"),
            [t("Newest First", "Nieuwste eerst"), t("Oldest First", "Oudste eerst")],
            key="history_sort"
        )
    with col3:
        max_events = st.slider(t("Show events", "Toon gebeurtenissen"), 5, 100, 20, key="history_max")
    st.markdown('</div>', unsafe_allow_html=True)

    # Display events
    st.subheader(t("⌗ Event Log", "⌗ Gebeurtenissenlogboek"))

    if len(st.session_state.event_history) == 0:
        st.info(t("No events recorded yet", "Nog geen gebeurtenissen opgeslagen"))
    else:
        # Reverse if oldest first
        events_to_show = st.session_state.event_history.copy()
        if sort_option == t("Oldest First", "Oudste eerst"):
            events_to_show = events_to_show[::-1]

        # Filter events
        if "All" not in filter_type:
            events_to_show = [e for e in events_to_show if e.get("type") in filter_type]

        # Limit events
        events_to_show = events_to_show[:max_events]

        # Display as cards
        for event in events_to_show:
            event_type = event.get("type", "System")
            message = event.get("message", "")
            timestamp = event.get("timestamp", "")

            # Color based on type
            color = "#6366f1"  # blue
            if event_type == "Anomaly":
                color = "#ef4444"  # red
            elif event_type == "Bottleneck":
                color = "#f97316"  # orange
            elif event_type == "Connection":
                color = "#10b981"  # green

            st.markdown(f"""
            <div class="history-event-card" style="border-left-color: {color};">
                <div class="history-event-top">
                    <span class="history-badge" style="color: {color}; border: 1px solid {color};">{event_type}</span>
                    <span class="history-timestamp">{timestamp}</span>
                </div>
                <div class="history-message">{message}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Stats
    st.subheader(t("⌗ History Statistics", "⌗ Geschiedenis Statistieken"))
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(t("Total Events", "Totale Gebeurtenissen"), total_events)
    col2.metric(t("Anomalies", "Afwijkingen"), anomaties_count)
    col3.metric(t("Bottlenecks", "Knelpunten"), bottleneck_count)
    col4.metric(t("Connections", "Verbindingen"), connection_count)

    # Clear history option
    st.divider()
    if st.button(t("Clear History", "Wis Geschiedenis"), type="secondary"):
        st.session_state.event_history = []
        st.success(t("History cleared", "Geschiedenis gewist"))
        st.rerun()

persist_active_user_state()

# ─────────────────────────────────────────────────────────────
# 🚀 PRO REALTIME BACKEND (WebSocket via FastAPI)
# Run separately with: uvicorn machine_sim:app --reload
# ─────────────────────────────────────────────────────────────

try:
    import importlib
    import asyncio
    import random

    _fastapi = importlib.import_module("fastapi")
    FastAPI = getattr(_fastapi, "FastAPI")
    WebSocket = getattr(_fastapi, "WebSocket")
    Header = getattr(_fastapi, "Header")
    HTTPException = getattr(_fastapi, "HTTPException")

    app = FastAPI()

    @app.post("/ingest")
    async def ingest_payload(payload: dict, x_api_key: str | None = Header(default=None, alias="x-api-key")):
        expected_key = os.getenv("MACHINE_MONITOR_API_KEY", "change-me")
        if expected_key and expected_key != "none" and x_api_key != expected_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
        save_cloud_payload(payload)
        return {"ok": True, "saved": True}

    @app.get("/latest")
    async def latest_payload():
        record = read_cloud_record()
        if not record:
            return {"ok": False, "payload": None}
        return {"ok": True, **record}

    @app.websocket("/ws")
    async def websocket_endpoint(ws):
        await ws.accept()
        while True:
            # Use real data if available, else simulate
            try:
                data = get_live_data()
            except Exception:
                data = {
                    f"machine_{i}": random.uniform(1, 6)
                    for i in range(1, st.session_state.get("num_machines", 3) + 1)
                }

            await ws.send_json(data)
            await asyncio.sleep(1)

except Exception:
    # FastAPI not installed -> ignore this optional websocket backend.
    pass