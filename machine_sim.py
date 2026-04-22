import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import time
import json
import os
import re
import base64
import hashlib
import secrets
import smtplib
from email.message import EmailMessage
from urllib import request as urllib_request
from urllib import error as urllib_error
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

.stApp, .stMarkdown, .stCaption, .stText, p, li, label {
    color: #e5eefb;
}

h1, h2, h3, h4, h5, h6 {
    color: #f8fafc !important;
    letter-spacing: 0.01em;
}

[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    color: #f8fafc !important;
}

.inline-btn-primary {
    background: linear-gradient(180deg, #3b82f6 0%, #1d4ed8 100%);
    color: #ffffff;
    border: 1px solid #2563eb;
    box-shadow: 0 10px 24px rgba(59, 130, 246, 0.24);
}

.inline-btn-primary:hover {
    background: linear-gradient(180deg, #2563eb 0%, #1e40af 100%);
    color: #ffffff;
}

.inline-btn-secondary {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    color: #f8fafc;
    border: 1px solid #334155;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.24);
}

.inline-btn-secondary:hover {
    background: linear-gradient(180deg, #334155 0%, #1e293b 100%);
    color: #ffffff;
}

.inline-btn-neon {
    background: linear-gradient(180deg, #14b8a6 0%, #0ea5e9 100%);
    color: #06202a;
    border: 1px solid #2dd4bf;
    box-shadow: 0 10px 24px rgba(20, 184, 166, 0.26);
    font-weight: 800;
}

.inline-btn-neon:hover {
    background: linear-gradient(180deg, #0ea5e9 0%, #0284c7 100%);
    color: #06202a;
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


@st.cache_data
def load_light_theme_overrides():
    return """
<style>
.stApp {
    background: radial-gradient(circle at top, #c7daf2 0%, #b5cfee 45%, #a5c4ea 100%) !important;
    color: #10233d !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main {
    background: transparent !important;
}

.page-section,
.settings-section,
.history-section,
.top-nav-shell,
.connect-wrap,
.history-hero,
.settings-hero,
.connect-status,
.page-hero,
.platform-hero,
.about-hero,
.contact-hero,
.faq-hero,
.support-hero {
    background: linear-gradient(180deg, rgba(194,214,238,0.95) 0%, rgba(178,203,233,0.95) 100%) !important;
    border: 1px solid #78a9df !important;
    box-shadow: 0 10px 26px rgba(59,130,246,0.22), 0 0 0 1px rgba(34,211,238,0.18) inset !important;
}

.card,
.welcome-card,
.feature-card,
.status-card,
.history-event-card,
.connect-feature-card,
.device-card,
[data-testid="column"]:has(.acct-content-marker) {
    background: linear-gradient(180deg, #cfe1f4 0%, #bed5ef 100%) !important;
    border: 1px solid #78a9df !important;
    box-shadow: 0 14px 34px rgba(37,99,235,0.2), 0 0 0 1px rgba(34,211,238,0.14) inset !important;
}

.stApp,
.stMarkdown,
.stCaption,
.stText,
p,
li,
label,
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stMetricDelta"] {
    color: #10233d !important;
}

h1,
h2,
h3,
h4,
h5,
h6,
.connect-title,
.history-hero-title,
.settings-hero-title,
.device-name,
.pnav-brand-title,
.pnav-panel-title {
    color: #10233d !important;
}

.connect-sub,
.history-hero-sub,
.settings-hero-sub,
.device-ip,
.connect-status-meta,
[data-testid="stCaptionContainer"],
.history-timestamp,
.page-hero-sub,
.pnav-account-row,
.acct-nav-label {
    color: #2e4662 !important;
}

.page-chip,
.history-chip,
.settings-chip,
.pnav-chip,
.history-badge {
    color: #1f3e62 !important;
    border-color: #78a9df !important;
    background: #c7dcf3 !important;
}

.pnav-panel,
.pnav-account {
    background: linear-gradient(180deg, #c9dcf2 0%, #bad2ee 100%) !important;
    border-color: #78a9df !important;
    box-shadow: -6px 0 24px rgba(37,99,235,0.22) !important;
}

.pnav-item {
    background: #c4d9f2 !important;
    border-color: #78a9df !important;
    color: #10233d !important;
}

.pnav-item:hover {
    background: #b7d2f0 !important;
    border-color: #4d95e2 !important;
    color: #10233d !important;
}

.pnav-item.pnav-active {
    background: linear-gradient(180deg, #a9caf1 0%, #98bfed 100%) !important;
    border-color: #3b82f6 !important;
    color: #10233d !important;
    box-shadow: 0 8px 20px rgba(59,130,246,0.24) !important;
}

.pnav-hamburger {
    background: #3b82f6 !important;
    border-color: #2563eb !important;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.28) !important;
}

.pnav-brand-kicker,
.history-timestamp,
.connect-status-meta,
.device-ip {
    color: #4f6783 !important;
}

.stButton > button,
.stForm [data-testid="stFormSubmitButton"] > button,
.stForm button,
[data-testid="stFormSubmitButton"] > button,
[data-testid="stDownloadButton"] > button,
.stDownloadButton > button,
.stLinkButton > a,
button[kind="primary"],
button[data-testid="baseButton-primary"],
button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(180deg, #3b82f6 0%, #06b6d4 100%) !important;
    color: #ffffff !important;
    border: 1px solid #3b82f6 !important;
    box-shadow: 0 10px 24px rgba(59, 130, 246, 0.3), 0 0 0 1px rgba(34,211,238,0.24) inset !important;
}

.stButton > button:hover,
.stForm [data-testid="stFormSubmitButton"] > button:hover,
.stForm button:hover,
[data-testid="stFormSubmitButton"] > button:hover,
button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
.stLinkButton > a:hover {
    background: linear-gradient(180deg, #2563eb 0%, #0ea5e9 100%) !important;
    border-color: #2563eb !important;
    color: #ffffff !important;
}

button[kind="secondary"],
button[data-testid="baseButton-secondary"],
button[data-testid="stBaseButton-secondary"] {
    background: #c6dbf3 !important;
    color: #2e4662 !important;
    border: 1px solid #78a9df !important;
}

[data-baseweb="select"] > div,
.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div,
div[role="listbox"],
div[role="option"] {
    background: #c7daf2 !important;
    color: #10233d !important;
    border-color: #78a9df !important;
}

div[role="option"][aria-selected="true"],
div[data-baseweb="popover"] [aria-selected="true"],
div[data-baseweb="popover"] li[aria-selected="true"] {
    background: #afd0f2 !important;
    color: #10233d !important;
}

.stPlotlyChart,
#rt-trend,
#snapshot-root {
    background: #c7daf2 !important;
    border: 1px solid #78a9df !important;
}

.stPlotlyChart .js-plotly-plot .plotly .main-svg,
.stPlotlyChart .js-plotly-plot .plotly .bg {
    background: #c7daf2 !important;
}

/* Readability hardening for legacy inline text colors in Settings */
[style*="color:#f8fafc"],
[style*="color:#e2e8f0"],
[style*="color:#cbd5e1"],
[style*="color:#f1f5f9"] {
    color: #0f2340 !important;
}

[style*="rgba(15,23,42,0.96)"],
[style*="rgba(17,24,39,0.96)"] {
    border-color: #78a9df !important;
}

/* Better form readability in Settings */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: #c7daf2 !important;
    color: #0f2340 !important;
    border-color: #78a9df !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder,
.stNumberInput input::placeholder {
    color: #486587 !important;
}

.inline-btn-primary {
    background: linear-gradient(180deg, #3b82f6 0%, #06b6d4 100%) !important;
    color: #ffffff !important;
    border-color: #3b82f6 !important;
    box-shadow: 0 10px 24px rgba(59, 130, 246, 0.3), 0 0 0 1px rgba(34,211,238,0.24) inset !important;
}

.inline-btn-primary:hover {
    background: linear-gradient(180deg, #2563eb 0%, #0ea5e9 100%) !important;
}

.inline-btn-secondary {
    background: #c6dbf3 !important;
    color: #2e4662 !important;
    border-color: #78a9df !important;
    box-shadow: 0 8px 18px rgba(59,130,246,0.2) !important;
}

.inline-btn-secondary:hover {
    background: #b7d2f0 !important;
    color: #10233d !important;
    border-color: #4d95e2 !important;
}

.inline-btn-neon {
    background: linear-gradient(180deg, #22d3ee 0%, #3b82f6 100%) !important;
    color: #0a2342 !important;
    border-color: #38bdf8 !important;
    box-shadow: 0 10px 24px rgba(14,165,233,0.28), 0 0 0 1px rgba(34,211,238,0.24) inset !important;
}

.inline-btn-neon:hover {
    background: linear-gradient(180deg, #0ea5e9 0%, #2563eb 100%) !important;
    color: #0a2342 !important;
}

.top-nav-shell {
    background: linear-gradient(180deg, #c4d9f2 0%, #b7d1ef 100%) !important;
    border-color: #78a9df !important;
    box-shadow: 0 14px 30px rgba(59,130,246,0.2) !important;
}

.top-nav-divider {
    background: linear-gradient(180deg, rgba(59,130,246,0.1) 0%, rgba(59,130,246,0.8) 50%, rgba(59,130,246,0.1) 100%) !important;
}

/* Top nav Streamlit buttons */
button[id^="top_nav_"] {
    border-radius: 12px !important;
}

button[id^="top_nav_"][kind="secondary"],
button[id^="top_nav_"][data-testid="baseButton-secondary"] {
    background: #c6dbf3 !important;
    color: #1f3f63 !important;
    border-color: #78a9df !important;
}

button[id^="top_nav_"][kind="primary"],
button[id^="top_nav_"][data-testid="baseButton-primary"] {
    background: linear-gradient(180deg, #22d3ee 0%, #3b82f6 100%) !important;
    color: #08233f !important;
    border-color: #38bdf8 !important;
    box-shadow: 0 8px 18px rgba(14,165,233,0.26) !important;
}

/* Simulation/Live toggles and generic mode controls in light neon mode */
[data-testid="stSegmentedControl"] [role="radiogroup"] {
    background: linear-gradient(180deg, #c5dcf7 0%, #b8d2f2 100%) !important;
    border: 1px solid #78a9df !important;
    box-shadow: 0 10px 20px rgba(59,130,246,0.18) !important;
}

[data-testid="stSegmentedControl"] [role="radio"],
[data-testid="stSegmentedControl"] button {
    color: #2b4a6f !important;
    background: transparent !important;
    border: 1px solid transparent !important;
}

[data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"],
[data-testid="stSegmentedControl"] button[aria-pressed="true"],
[data-testid="stSegmentedControl"] [data-selected="true"] {
    background: linear-gradient(180deg, #22d3ee 0%, #3b82f6 100%) !important;
    color: #08233f !important;
    border-color: #38bdf8 !important;
    box-shadow: 0 8px 18px rgba(14,165,233,0.26) !important;
}

[data-testid="stSegmentedControl"] [role="radio"]:hover,
[data-testid="stSegmentedControl"] button:hover {
    background: rgba(59,130,246,0.16) !important;
    color: #0f2340 !important;
}

.stButton > button:disabled,
button[data-testid="baseButton-primary"][disabled],
button[data-testid="baseButton-secondary"][disabled],
button[data-testid="stBaseButton-primary"][disabled],
button[data-testid="stBaseButton-secondary"][disabled] {
    opacity: 1 !important;
    background: linear-gradient(180deg, #a6d5f3 0%, #8fbfea 100%) !important;
    color: #264a70 !important;
    border-color: #78a9df !important;
}

a {
    color: #2563eb !important;
}
</style>
"""


if 'theme_preference' not in st.session_state:
    st.session_state.theme_preference = "Dark"

st.markdown(load_css(), unsafe_allow_html=True)
if st.session_state.get("theme_preference") == "Light":
    st.markdown(load_light_theme_overrides(), unsafe_allow_html=True)


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


def get_theme_tokens():
    """Central theme tokens so UI and charts stay in sync across modes."""
    is_light = st.session_state.get("theme_preference", "Dark") == "Light"
    custom_accent = str(st.session_state.get("ui_accent_color", "#3b82f6") or "#3b82f6")
    if is_light:
        return {
            "is_light": True,
            "app_bg": "#c7daf2",
            "app_bg_mid": "#b5cfee",
            "app_bg_end": "#a5c4ea",
            "surface": "#c7daf2",
            "card": "#c4d9f2",
            "border": "#78a9df",
            "text": "#1f2937",
            "muted": "#374151",
            "subtle": "#4b5563",
            "accent": custom_accent,
            "accent_hover": custom_accent,
            "accent_glow": "rgba(59,130,246,0.32)",
            "danger_glow": "rgba(244,63,94,0.28)",
            "plot_template": "plotly_dark",
            "plot_grid": "rgba(84,110,139,0.24)",
            "hero_gradient": "linear-gradient(120deg,#c4d9f2 0%,#b3cdef 60%,#87b9f1 130%)",
            "hero_gradient_alt": "linear-gradient(120deg,#c4d9f2 0%,#b3cdef 60%,#7fd8e8 130%)",
        }
    return {
        "is_light": False,
        "app_bg": "#16233b",
        "app_bg_mid": "#0f172a",
        "app_bg_end": "#0b1120",
        "surface": "#0f172a",
        "card": "#1e293b",
        "border": "#334155",
        "text": "#f8fafc",
        "muted": "#cbd5e1",
        "subtle": "#94a3b8",
        "accent": custom_accent,
        "accent_hover": custom_accent,
        "accent_glow": "rgba(59,130,246,0.28)",
        "danger_glow": "rgba(244,63,94,0.24)",
        "plot_template": "plotly_dark",
        "plot_grid": "rgba(148,163,184,0.22)",
        "hero_gradient": "linear-gradient(120deg,#0b1220 0%,#1e293b 60%,#1e3a5f 130%)",
        "hero_gradient_alt": "linear-gradient(120deg,#0b1220 0%,#1e293b 60%,#134e4a 130%)",
    }


USER_DB_FILE = os.path.join(os.path.dirname(__file__), "users.json")
LOGO_FILE = os.path.join(os.path.dirname(__file__), "image.png")


@st.cache_data
def get_logo_data_uri() -> str:
    if not os.path.exists(LOGO_FILE):
        return ""
    try:
        with open(LOGO_FILE, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
        return f"data:image/png;base64,{encoded}"
    except Exception:
        return ""


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
        "settings_active_tab": st.session_state.get("settings_active_tab", "general"),
        "settings_account_section": st.session_state.get("settings_account_section", "profiel"),
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
        "dashboard_visible_machines": list(st.session_state.get("dashboard_visible_machines", [])),
        "dashboard_machine_order": list(st.session_state.get("dashboard_machine_order", [])),
        "dashboard_show_snapshot_chart": bool(st.session_state.get("dashboard_show_snapshot_chart", True)),
        "dashboard_show_realtime_panel": bool(st.session_state.get("dashboard_show_realtime_panel", True)),
        "dashboard_show_history_chart": bool(st.session_state.get("dashboard_show_history_chart", True)),
        "alert_enabled_by_machine": dict(st.session_state.get("alert_enabled_by_machine", {})),
        "alert_threshold_watt": int(st.session_state.get("alert_threshold_watt", 1000)),
        "alert_type_fault": bool(st.session_state.get("alert_type_fault", True)),
        "alert_type_maintenance": bool(st.session_state.get("alert_type_maintenance", True)),
        "ui_accent_color": st.session_state.get("ui_accent_color", "#3b82f6"),
        "ui_density": st.session_state.get("ui_density", "Comfortable"),
        "ai_response_style": st.session_state.get("ai_response_style", "Detailed"),
        "ai_technical_level": st.session_state.get("ai_technical_level", "Simple"),
        "ai_auto_advice": bool(st.session_state.get("ai_auto_advice", True)),
        "data_time_period": st.session_state.get("data_time_period", "1h"),
        "data_update_mode": st.session_state.get("data_update_mode", "live"),
        "data_unit": st.session_state.get("data_unit", "W"),
        "machine_colors": dict(st.session_state.get("machine_colors", {})),
        "machine_groups": dict(st.session_state.get("machine_groups", {})),
        "date_format": st.session_state.get("date_format", "DD-MM-YYYY"),
        "timezone_name": st.session_state.get("timezone_name", "Europe/Amsterdam"),
        "privacy_data_sharing": bool(st.session_state.get("privacy_data_sharing", False)),
        "ai_history_enabled": bool(st.session_state.get("ai_history_enabled", True)),
        "ui_animations_enabled": bool(st.session_state.get("ui_animations_enabled", True)),
        "ui_mobile_compact": bool(st.session_state.get("ui_mobile_compact", False)),
        "ui_sidebar_default": st.session_state.get("ui_sidebar_default", "Open"),
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
    st.session_state.settings_active_tab = state.get(
        "settings_active_tab",
        st.session_state.get("settings_active_tab", "general"),
    )
    st.session_state.settings_account_section = state.get(
        "settings_account_section",
        st.session_state.get("settings_account_section", "profiel"),
    )
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
    st.session_state.dashboard_visible_machines = list(state.get("dashboard_visible_machines", st.session_state.get("dashboard_visible_machines", [])))
    st.session_state.dashboard_machine_order = list(state.get("dashboard_machine_order", st.session_state.get("dashboard_machine_order", [])))
    st.session_state.dashboard_show_snapshot_chart = bool(state.get("dashboard_show_snapshot_chart", st.session_state.get("dashboard_show_snapshot_chart", True)))
    st.session_state.dashboard_show_realtime_panel = bool(state.get("dashboard_show_realtime_panel", st.session_state.get("dashboard_show_realtime_panel", True)))
    st.session_state.dashboard_show_history_chart = bool(state.get("dashboard_show_history_chart", st.session_state.get("dashboard_show_history_chart", True)))
    st.session_state.alert_enabled_by_machine = dict(state.get("alert_enabled_by_machine", st.session_state.get("alert_enabled_by_machine", {})))
    st.session_state.alert_threshold_watt = int(state.get("alert_threshold_watt", st.session_state.get("alert_threshold_watt", 1000)))
    st.session_state.alert_type_fault = bool(state.get("alert_type_fault", st.session_state.get("alert_type_fault", True)))
    st.session_state.alert_type_maintenance = bool(state.get("alert_type_maintenance", st.session_state.get("alert_type_maintenance", True)))
    st.session_state.ui_accent_color = state.get("ui_accent_color", st.session_state.get("ui_accent_color", "#3b82f6"))
    st.session_state.ui_density = state.get("ui_density", st.session_state.get("ui_density", "Comfortable"))
    st.session_state.ai_response_style = state.get("ai_response_style", st.session_state.get("ai_response_style", "Detailed"))
    st.session_state.ai_technical_level = state.get("ai_technical_level", st.session_state.get("ai_technical_level", "Simple"))
    st.session_state.ai_auto_advice = bool(state.get("ai_auto_advice", st.session_state.get("ai_auto_advice", True)))
    st.session_state.data_time_period = state.get("data_time_period", st.session_state.get("data_time_period", "1h"))
    st.session_state.data_update_mode = state.get("data_update_mode", st.session_state.get("data_update_mode", "live"))
    st.session_state.data_unit = state.get("data_unit", st.session_state.get("data_unit", "W"))
    st.session_state.machine_colors = dict(state.get("machine_colors", st.session_state.get("machine_colors", {})))
    st.session_state.machine_groups = dict(state.get("machine_groups", st.session_state.get("machine_groups", {})))
    st.session_state.date_format = state.get("date_format", st.session_state.get("date_format", "DD-MM-YYYY"))
    st.session_state.timezone_name = state.get("timezone_name", st.session_state.get("timezone_name", "Europe/Amsterdam"))
    st.session_state.privacy_data_sharing = bool(state.get("privacy_data_sharing", st.session_state.get("privacy_data_sharing", False)))
    st.session_state.ai_history_enabled = bool(state.get("ai_history_enabled", st.session_state.get("ai_history_enabled", True)))
    st.session_state.ui_animations_enabled = bool(state.get("ui_animations_enabled", st.session_state.get("ui_animations_enabled", True)))
    st.session_state.ui_mobile_compact = bool(state.get("ui_mobile_compact", st.session_state.get("ui_mobile_compact", False)))
    st.session_state.ui_sidebar_default = state.get("ui_sidebar_default", st.session_state.get("ui_sidebar_default", "Open"))
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
if 'settings_active_tab' not in st.session_state:
    st.session_state.settings_active_tab = "general"
if 'settings_account_section' not in st.session_state:
    st.session_state.settings_account_section = "profiel"
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
if 'dashboard_visible_machines' not in st.session_state:
    st.session_state.dashboard_visible_machines = list(range(1, int(st.session_state.get('num_machines', 3)) + 1))
if 'dashboard_machine_order' not in st.session_state:
    st.session_state.dashboard_machine_order = list(range(1, int(st.session_state.get('num_machines', 3)) + 1))
if 'dashboard_show_snapshot_chart' not in st.session_state:
    st.session_state.dashboard_show_snapshot_chart = True
if 'dashboard_show_realtime_panel' not in st.session_state:
    st.session_state.dashboard_show_realtime_panel = True
if 'dashboard_show_history_chart' not in st.session_state:
    st.session_state.dashboard_show_history_chart = True
if 'alert_enabled_by_machine' not in st.session_state:
    st.session_state.alert_enabled_by_machine = {}
if 'alert_threshold_watt' not in st.session_state:
    st.session_state.alert_threshold_watt = 1000
if 'alert_type_fault' not in st.session_state:
    st.session_state.alert_type_fault = True
if 'alert_type_maintenance' not in st.session_state:
    st.session_state.alert_type_maintenance = True
if 'ui_accent_color' not in st.session_state:
    st.session_state.ui_accent_color = "#3b82f6"
if 'ui_density' not in st.session_state:
    st.session_state.ui_density = "Comfortable"
if 'ai_response_style' not in st.session_state:
    st.session_state.ai_response_style = "Detailed"
if 'ai_technical_level' not in st.session_state:
    st.session_state.ai_technical_level = "Simple"
if 'ai_auto_advice' not in st.session_state:
    st.session_state.ai_auto_advice = True
if 'data_time_period' not in st.session_state:
    st.session_state.data_time_period = "1h"
if 'data_update_mode' not in st.session_state:
    st.session_state.data_update_mode = "live"
if 'data_unit' not in st.session_state:
    st.session_state.data_unit = "W"
if 'machine_colors' not in st.session_state:
    st.session_state.machine_colors = {}
if 'machine_groups' not in st.session_state:
    st.session_state.machine_groups = {}
if 'date_format' not in st.session_state:
    st.session_state.date_format = "DD-MM-YYYY"
if 'timezone_name' not in st.session_state:
    st.session_state.timezone_name = "Europe/Amsterdam"
if 'privacy_data_sharing' not in st.session_state:
    st.session_state.privacy_data_sharing = False
if 'ai_history_enabled' not in st.session_state:
    st.session_state.ai_history_enabled = True
if 'ui_animations_enabled' not in st.session_state:
    st.session_state.ui_animations_enabled = True
if 'ui_mobile_compact' not in st.session_state:
    st.session_state.ui_mobile_compact = False
if 'ui_sidebar_default' not in st.session_state:
    st.session_state.ui_sidebar_default = "Open"
if 'ai_insights_notified' not in st.session_state:
    st.session_state.ai_insights_notified = False
if 'webshop_notified' not in st.session_state:
    st.session_state.webshop_notified = False


def get_ordered_visible_machine_indices(max_machines):
    visible = [int(v) for v in list(st.session_state.get("dashboard_visible_machines", [])) if str(v).isdigit()]
    if not visible:
        visible = list(range(1, max_machines + 1))
    visible = [idx for idx in visible if 1 <= idx <= max_machines]
    order = [int(v) for v in list(st.session_state.get("dashboard_machine_order", [])) if str(v).isdigit()]
    ordered = [idx for idx in order if idx in visible]
    remainder = [idx for idx in visible if idx not in ordered]
    return ordered + remainder


def convert_amp_value(value_a):
    unit = str(st.session_state.get("data_unit", "W"))
    watt = float(value_a) * 230.0
    if unit == "kW":
        return watt / 1000.0, "kW"
    return watt, "W"

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
                st.session_state.last_device_response_time = time.time()  # Track for disconnect detection

            device["endpoint"] = endpoint
            device["last_response"] = time.time()  # Track when device last responded
            latest_payload = payload
            latest_endpoint = endpoint
            successful_devices += 1
        except Exception as exc:
            previous = st.session_state.get("last_live_current") if index == 1 else None
            if previous is None:
                previous = st.session_state.get("last_current_values", {}).get(key, 0.5)
            row[key] = float(np.clip(float(previous), 0.5, 6.0))
            error_summary = str(exc)[:100]  # Truncate long errors for readability
            errors.append(f"{ip}:{port} -> {error_summary}")
            device["last_error"] = error_summary
            device["last_error_time"] = time.time()

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
if "event_last_seen" not in st.session_state:
    st.session_state.event_last_seen = {}

# Helper function to log events
def log_event(event_type, message, dedupe_key=None, cooldown_s=0, meta=None):
    import datetime

    if dedupe_key:
        now_ts = time.time()
        last_seen = float(st.session_state.event_last_seen.get(dedupe_key, 0.0))
        if (now_ts - last_seen) < max(0, float(cooldown_s)):
            return False
        st.session_state.event_last_seen[dedupe_key] = now_ts

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event = {"timestamp": timestamp, "type": event_type, "message": message}
    if isinstance(meta, dict):
        event.update(meta)
    st.session_state.event_history.insert(0, event)  # Add to beginning (newest first)
    # Keep only last 100 events
    if len(st.session_state.event_history) > 100:
        st.session_state.event_history = st.session_state.event_history[:100]
    return True


def build_sparkline_data_uri(points, color="#3b82f6"):
    """Build a tiny inline sparkline image for history cards."""
    if not isinstance(points, list) or len(points) < 2:
        return ""
    numeric = [float(p) for p in points if isinstance(p, (int, float))]
    if len(numeric) < 2:
        return ""

    width = 120
    height = 34
    pad = 4
    min_v = min(numeric)
    max_v = max(numeric)
    span = max(max_v - min_v, 1e-6)

    path_parts = []
    for idx, value in enumerate(numeric):
        x = pad + (idx * (width - 2 * pad) / max(1, (len(numeric) - 1)))
        y = height - pad - ((value - min_v) / span) * (height - 2 * pad)
        cmd = "M" if idx == 0 else "L"
        path_parts.append(f"{cmd}{x:.1f},{y:.1f}")

    path = " ".join(path_parts)
    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>"
        f"<rect x='0' y='0' width='{width}' height='{height}' rx='8' fill='rgba(15,23,42,0.18)'/>"
        f"<path d='{path}' fill='none' stroke='{color}' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/>"
        "</svg>"
    )
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def build_incident_detail_snapshot(event, df_local, minutes_before=2, minutes_after=1):
    """Freeze a chart window around the incident timestamp so it stays static in History.
    Falls back to the stored sparkline_points when the df has no matching timestamps."""
    if not isinstance(event, dict):
        return None

    machine_idx = event.get("machine")
    if machine_idx is None:
        return None

    try:
        machine_idx = int(machine_idx)
    except Exception:
        return None

    # Try df-based window lookup first (works within the same session)
    if isinstance(df_local, pd.DataFrame) and not df_local.empty:
        col_name = f"current_{machine_idx}"
        if col_name in df_local.columns and "timestamp" in df_local.columns:
            timestamp_series = pd.to_datetime(df_local["timestamp"], errors="coerce")
            if not timestamp_series.isna().all():
                anchor_raw = event.get("incident_anchor_ts") or event.get("event_ts_iso")
                if anchor_raw:
                    anchor_ts = pd.to_datetime(anchor_raw, errors="coerce")
                    if not pd.isna(anchor_ts):
                        window_mask = (
                            (timestamp_series >= (anchor_ts - pd.Timedelta(minutes=max(1, int(minutes_before)))))
                            & (timestamp_series <= (anchor_ts + pd.Timedelta(minutes=max(0, int(minutes_after)))))
                        )
                        window_df = df_local.loc[window_mask].copy()
                        if not window_df.empty:
                            window_timestamps = pd.to_datetime(window_df["timestamp"], errors="coerce")
                            distance = (window_timestamps - anchor_ts).abs()
                            if not distance.isna().all():
                                center_pos = int(distance.values.argmin())
                                y_values = pd.to_numeric(window_df[col_name], errors="coerce").fillna(0.0).tolist()
                                x_values = (
                                    pd.to_datetime(window_df["timestamp"], errors="coerce")
                                    .dt.strftime("%H:%M:%S")
                                    .fillna("")
                                    .tolist()
                                )
                                return {
                                    "x": x_values,
                                    "y": [float(v) for v in y_values],
                                    "incident_index": center_pos,
                                    "machine": machine_idx,
                                }

    # Fallback: rebuild from stored sparkline_points (available on all events)
    spark_points = event.get("sparkline_points", [])
    if isinstance(spark_points, list) and len(spark_points) >= 2:
        numeric = [float(p) for p in spark_points if isinstance(p, (int, float))]
        if len(numeric) >= 2:
            n = len(numeric)
            x_labels = [f"T-{n - 1 - i}" for i in range(n)]
            x_labels[-1] = t("Incident", "Incident")
            # Incident marker at the point with largest deviation from the pre-incident mean
            baseline = sum(numeric[:-1]) / max(len(numeric) - 1, 1)
            incident_pos = max(range(n), key=lambda i: abs(numeric[i] - baseline))
            return {
                "x": x_labels,
                "y": numeric,
                "incident_index": incident_pos,
                "machine": machine_idx,
            }

    return None


def build_ai_assistant_result(question):
    """Build a structured AI assistant result with message, suggested action and chart target."""
    q = str(question or "").strip().lower()
    q_norm = re.sub(r"[^a-z0-9\s]", " ", q)
    q_norm = re.sub(r"\s+", " ", q_norm).strip()
    q_tokens = [tok for tok in q_norm.split(" ") if tok]
    empty_message = t("Ask a question about your machines or settings.", "Stel een vraag over je machines of instellingen.")
    base_result = {
        "message": empty_message,
        "target_page": None,
        "target_label": None,
        "target_state": {},
        "chart_machine": None,
    }
    if not q:
        return base_result

    from difflib import SequenceMatcher

    def _sim(a, b):
        return SequenceMatcher(None, str(a), str(b)).ratio()

    def _term_match(term):
        term_norm = re.sub(r"[^a-z0-9\s]", " ", str(term).lower()).strip()
        if not term_norm:
            return False
        if term_norm in q_norm:
            return True

        term_tokens = [tok for tok in term_norm.split(" ") if tok]
        if len(term_tokens) == 1:
            t = term_tokens[0]
            for tok in q_tokens:
                if tok == t:
                    return True
                if len(tok) >= 4 and len(t) >= 4 and (tok.startswith(t[:4]) or t.startswith(tok[:4])):
                    return True
                if _sim(tok, t) >= 0.78:
                    return True
            return False

        # Multi-word phrase: allow loose token matching with typo tolerance.
        matched = 0
        for part in term_tokens:
            if any(_sim(tok, part) >= 0.78 or (len(tok) >= 4 and len(part) >= 4 and (tok.startswith(part[:4]) or part.startswith(tok[:4]))) for tok in q_tokens):
                matched += 1
        if matched >= max(1, len(term_tokens) - 1):
            return True

        return _sim(q_norm, term_norm) >= 0.72

    def _intent(*terms):
        return any(_term_match(term) for term in terms)

    df_local = st.session_state.get("df", pd.DataFrame())
    connected = bool(st.session_state.get("device_connected", False))
    mode = st.session_state.get("mode", "Simulation")
    anomalies = len(st.session_state.get("anomalies", []))
    bottlenecks = len(st.session_state.get("bottlenecks", []))
    event_history = st.session_state.get("event_history", [])
    cloud_enabled = bool(st.session_state.get("cloud_bridge_enabled", False))
    machine_names = list(st.session_state.get("machine_names", []))

    avg_load = 0.0
    machine_cols = []
    if isinstance(df_local, pd.DataFrame) and not df_local.empty:
        machine_cols = [c for c in df_local.columns if str(c).startswith("current_")]
        if machine_cols:
            avg_load = float(df_local[machine_cols].astype(float).mean().mean())

    def machine_label(machine_idx):
        if 1 <= machine_idx <= len(machine_names):
            return str(machine_names[machine_idx - 1])
        return f"Machine {machine_idx}"

    def machine_summary(machine_idx):
        col = f"current_{machine_idx}"
        if not isinstance(df_local, pd.DataFrame) or df_local.empty or col not in df_local.columns:
            return None
        series = pd.to_numeric(df_local[col], errors="coerce").dropna()
        if series.empty:
            return None
        current_value = float(series.iloc[-1])
        average_value = float(series.mean())
        peak_value = float(series.max())
        std_value = float(series.std()) if not np.isnan(series.std()) else 0.0
        std_value = std_value if std_value > 0 else 1.0
        anomaly_score = abs(current_value - average_value) / std_value
        trend_value = float(np.polyfit(range(len(series)), series.to_numpy(dtype=float), 1)[0]) if len(series) > 5 else 0.0
        if anomaly_score > 2.5 or current_value > 6:
            status = t("Needs attention", "Heeft aandacht nodig")
        elif average_value > 4:
            status = t("Monitor closely", "Extra monitoren")
        else:
            status = t("Stable", "Stabiel")
        trend_label = t("rising", "stijgend") if trend_value > 0.05 else t("falling", "dalend") if trend_value < -0.05 else t("stable", "stabiel")
        return {
            "machine": machine_idx,
            "label": machine_label(machine_idx),
            "current": current_value,
            "avg": average_value,
            "peak": peak_value,
            "anomaly": anomaly_score,
            "trend": trend_value,
            "trend_label": trend_label,
            "status": status,
            "risk": anomaly_score + max(0.0, average_value - 4.0) + max(0.0, current_value - 5.5),
        }

    machine_summaries = []
    for col_name in machine_cols:
        try:
            machine_idx = int(str(col_name).split("_")[1])
        except Exception:
            continue
        summary = machine_summary(machine_idx)
        if summary:
            machine_summaries.append(summary)

    top_risk = max(machine_summaries, key=lambda item: item["risk"], default=None)
    top_current = max(machine_summaries, key=lambda item: item["current"], default=None)
    overall_trend = 0.0
    if isinstance(df_local, pd.DataFrame) and not df_local.empty and machine_cols:
        combined = df_local[machine_cols].astype(float).mean(axis=1)
        overall_trend = float(np.polyfit(range(len(combined)), combined.to_numpy(dtype=float), 1)[0]) if len(combined) > 5 else 0.0
    overall_trend_label = t("rising", "stijgend") if overall_trend > 0.05 else t("falling", "dalend") if overall_trend < -0.05 else t("stable", "stabiel")
    latest_event = event_history[0] if event_history else None

    def result(message, target_page=None, target_label=None, chart_machine=None, target_state=None):
        payload = dict(base_result)
        payload["message"] = message
        payload["target_page"] = target_page
        payload["target_label"] = target_label
        payload["chart_machine"] = chart_machine
        payload["target_state"] = dict(target_state or {})
        return payload

    machine_match = re.search(r"(?:m|machine|lijn|line)\s*(\d+)", q_norm)
    if machine_match:
        machine_idx = int(machine_match.group(1))
        summary = machine_summary(machine_idx)
        if summary:
            action_text = t(
                "Inspect this machine first." if summary["risk"] > 3 else "Keep monitoring this machine.",
                "Controleer deze machine eerst." if summary["risk"] > 3 else "Blijf deze machine volgen."
            )
            return result(
                t(
                    f"**{summary['label']}**\n- Current: {summary['current']:.2f}A\n- Average: {summary['avg']:.2f}A\n- Peak: {summary['peak']:.2f}A\n- Trend: {summary['trend_label']}\n- Status: {summary['status']}\n- Action: {action_text}",
                    f"**{summary['label']}**\n- Huidig: {summary['current']:.2f}A\n- Gemiddeld: {summary['avg']:.2f}A\n- Piek: {summary['peak']:.2f}A\n- Trend: {summary['trend_label']}\n- Status: {summary['status']}\n- Actie: {action_text}"
                ),
                target_page="Factory Analysis",
                target_label=t("Open machine analysis", "Open machine-analyse"),
                chart_machine=machine_idx,
            )
        return result(
            t(f"I can not find data for {machine_label(machine_idx)} yet.", f"Ik kan nog geen data vinden voor {machine_label(machine_idx)}."),
            target_page="Dashboard",
            target_label=t("Open dashboard", "Open dashboard"),
        )

    asks_overall_machine_status = (
        _intent(
            "alle machines",
            "all machines",
            "check all",
            "overzicht machines",
            "machine status",
            "status van alles",
            "volledige status",
            "alle lijnen",
            "all lines",
            "hoe gaat het met de machines",
            "hoe doen de machines",
            "hoe gaat t met de machines",
            "hoe gaat het met de fabriek",
            "hoe gaat het met machine",
            "hoe is de status",
        )
        or (
            any(tok in q_tokens for tok in ["hoe", "gaat", "doen", "status"])
            and any(tok in q_tokens for tok in ["machine", "machines", "fabriek", "lijn", "lijnen"])
        )
    )

    if asks_overall_machine_status:
        if not machine_summaries:
            return result(t("No machine data is available yet.", "Er is nog geen machine-data beschikbaar."))
        if anomalies > 0 or bottlenecks > 0:
            direct_en = "Short answer: there are active issues, but monitoring is running."
            direct_nl = "Kort antwoord: er zijn actieve aandachtspunten, maar de monitoring draait."
        elif avg_load > 4.0:
            direct_en = "Short answer: machines are running, but load is relatively high."
            direct_nl = "Kort antwoord: machines draaien, maar de belasting is relatief hoog."
        else:
            direct_en = "Short answer: machines are running stable right now."
            direct_nl = "Kort antwoord: machines draaien op dit moment stabiel."

        lines_en = [f"**{direct_en}**", "", "**Fleet summary**"]
        lines_nl = [f"**{direct_nl}**", "", "**Machine-overzicht**"]
        for summary in machine_summaries[: min(5, len(machine_summaries))]:
            lines_en.append(f"- {summary['label']}: {summary['current']:.2f}A, {summary['status']}, trend {summary['trend_label']}")
            lines_nl.append(f"- {summary['label']}: {summary['current']:.2f}A, {summary['status']}, trend {summary['trend_label']}")
        if top_risk:
            lines_en.append(f"- Action: check {top_risk['label']} first")
            lines_nl.append(f"- Actie: controleer {top_risk['label']} eerst")
        return result(
            t("\n".join(lines_en), "\n".join(lines_nl)),
            target_page="Dashboard",
            target_label=t("Open live dashboard", "Open live dashboard"),
            chart_machine=top_risk["machine"] if top_risk else None,
        )

    if _intent("onderhoud", "maintenance", "service", "inspect", "inspectie", "reparatie", "slijtage", "storingsgevoelig", "which machine needs maintenance"):
        if not machine_summaries:
            return result(t("No machine data is available yet.", "Er is nog geen machine-data beschikbaar."))
        ranked = sorted(machine_summaries, key=lambda item: item["risk"], reverse=True)[:3]
        lines_en = ["**Maintenance priority**"]
        lines_nl = ["**Onderhoudsprioriteit**"]
        for summary in ranked:
            lines_en.append(f"- {summary['label']}: risk {summary['risk']:.1f}, current {summary['current']:.2f}A, status {summary['status']}")
            lines_nl.append(f"- {summary['label']}: risico {summary['risk']:.1f}, huidig {summary['current']:.2f}A, status {summary['status']}")
        lines_en.append("- Action: inspect the first machine before the next shift")
        lines_nl.append("- Actie: inspecteer de eerste machine voor de volgende shift")
        first_machine = ranked[0]["machine"] if ranked else None
        return result(
            t("\n".join(lines_en), "\n".join(lines_nl)),
            target_page="Factory Analysis",
            target_label=t("Open machine analysis", "Open machine-analyse"),
            chart_machine=first_machine,
        )

    if _intent("anomaly", "afwijking", "afwijk", "error", "fout", "storing", "alarms", "alert", "incident"):
        return result(
            t(
                f"**Current anomalies**\n- Count: {anomalies}\n- Highest risk: {(top_risk['label'] if top_risk else '-')}\n- Action: inspect the highest risk machine and check History for context.",
                f"**Huidige afwijkingen**\n- Aantal: {anomalies}\n- Hoogste risico: {(top_risk['label'] if top_risk else '-')}\n- Actie: controleer de machine met het hoogste risico en bekijk History voor context."
            ),
            target_page="History",
            target_label=t("Open history", "Open history"),
            chart_machine=top_risk["machine"] if top_risk else None,
        )

    if _intent("bottleneck", "knelpunt", "load", "belasting", "verbruik", "consumption", "energie", "power usage", "stroomverbruik", "hoger verbruik"):
        delta_pct = 0.0
        if machine_summaries:
            historical_avg = float(np.mean([item["avg"] for item in machine_summaries]))
            current_avg = float(np.mean([item["current"] for item in machine_summaries]))
            if historical_avg > 0:
                delta_pct = ((current_avg - historical_avg) / historical_avg) * 100.0
        return result(
            t(
                f"**Load review**\n- Bottlenecks: {bottlenecks}\n- Average load: {avg_load:.2f}A\n- Delta vs normal: {delta_pct:.1f}%\n- Main source: {(top_current['label'] if top_current else '-')}\n- Action: rebalance workload if the delta stays positive.",
                f"**Belastingsanalyse**\n- Knelpunten: {bottlenecks}\n- Gemiddelde belasting: {avg_load:.2f}A\n- Verschil vs normaal: {delta_pct:.1f}%\n- Belangrijkste bron: {(top_current['label'] if top_current else '-')}\n- Actie: verdeel de belasting opnieuw als dit verschil hoog blijft."
            ),
            target_page="Dashboard",
            target_label=t("Open live dashboard", "Open live dashboard"),
            chart_machine=top_current["machine"] if top_current else None,
        )

    if _intent("live", "verbinding", "connect", "device", "apparaat", "verbonden", "online", "offline", "esp32"):
        target_page = "Dashboard" if connected else "Device Connection"
        target_state = {"pending_mode": "Live"} if not connected else {}
        return result(
            t(
                f"**Live status**\n- Mode: {mode}\n- Device connected: {'yes' if connected else 'no'}\n- Cloud bridge: {'enabled' if cloud_enabled else 'disabled'}\n- Action: use Device Connection if you want live ESP32 data.",
                f"**Live status**\n- Modus: {mode}\n- Apparaat verbonden: {'ja' if connected else 'nee'}\n- Cloud bridge: {'ingeschakeld' if cloud_enabled else 'uitgeschakeld'}\n- Actie: gebruik Device Connection als je live ESP32-data wilt."
            ),
            target_page=target_page,
            target_label=t("Open device connection", "Open device connection") if not connected else t("Open live dashboard", "Open live dashboard"),
            target_state=target_state,
        )

    if _intent("trend", "voorspel", "predict", "prediction", "verwachting", "prognose", "forecast", "wat gaat er gebeuren"):
        if isinstance(df_local, pd.DataFrame) and not df_local.empty and machine_cols:
            next_risk = top_risk["label"] if top_risk else "-"
            return result(
                t(
                    f"**Prediction**\n- Overall trend: {overall_trend_label}\n- Average load: {avg_load:.2f}A\n- First machine to watch: {next_risk}\n- Action: plan a short inspection if the trend keeps rising.",
                    f"**Voorspelling**\n- Totale trend: {overall_trend_label}\n- Gemiddelde belasting: {avg_load:.2f}A\n- Eerste machine om te volgen: {next_risk}\n- Actie: plan een korte inspectie als de trend blijft stijgen."
                ),
                target_page="Factory Analysis",
                target_label=t("Open machine analysis", "Open machine-analyse"),
                chart_machine=top_risk["machine"] if top_risk else None,
            )
        return result(t("Not enough data for trend prediction yet.", "Nog niet genoeg data voor trendvoorspelling."))

    if _intent("history", "geschiedenis", "event", "melding", "notificatie", "logboek", "historie", "incident history"):
        total_events = len(st.session_state.get("event_history", []))
        return result(
            t(
                f"**History summary**\n- Events: {total_events}\n- Anomalies: {anomalies}\n- Bottlenecks: {bottlenecks}\n- Latest: {(latest_event.get('message', '-') if latest_event else '-')}\n- Action: open History for the incident window.",
                f"**History samenvatting**\n- Events: {total_events}\n- Afwijkingen: {anomalies}\n- Knelpunten: {bottlenecks}\n- Laatste: {(latest_event.get('message', '-') if latest_event else '-')}\n- Actie: open History voor het incidentvenster."
            ),
            target_page="History",
            target_label=t("Open history", "Open history"),
            chart_machine=top_risk["machine"] if top_risk else None,
        )

    if _intent("offline", "internet", "cloud", "netwerk", "verbinding cloud", "lokaal", "local mode"):
        return result(
            t(
                f"**Cloud and offline**\n- Local fallback: active\n- Cloud bridge: {'enabled' if cloud_enabled else 'disabled'}\n- Action: keep local mode as backup during network issues.",
                f"**Cloud en offline**\n- Lokale fallback: actief\n- Cloud bridge: {'ingeschakeld' if cloud_enabled else 'uitgeschakeld'}\n- Actie: houd lokale modus als back-up bij netwerkproblemen."
            ),
            target_page="Settings",
            target_label=t("Open settings", "Open settings"),
            target_state={"settings_active_tab": "general"},
        )

    if _intent("instelling", "setting", "theme", "taal", "language", "voorkeur", "preferences", "dashboard instellingen"):
        return result(
            t(
                "**Settings**\n- Theme, language, refresh speed, and machine setup are in Settings > General\n- Action: open Settings if you want to personalize the dashboard.",
                "**Instellingen**\n- Thema, taal, verversing en machine-setup staan in Settings > Algemeen\n- Actie: open Settings als je het dashboard wilt personaliseren."
            ),
            target_page="Settings",
            target_label=t("Open settings", "Open settings"),
            target_state={"settings_active_tab": "general"},
        )

    # Default fallback: always provide a useful machine status overview.
    fallback_machine = top_risk or top_current
    if machine_summaries:
        if anomalies > 0 or bottlenecks > 0:
            direct_en = "Short answer: your factory is running, but there are issues to check."
            direct_nl = "Kort antwoord: je fabriek draait, maar er zijn punten die je moet controleren."
        elif avg_load > 4.0:
            direct_en = "Short answer: performance is okay, but load is on the high side."
            direct_nl = "Kort antwoord: prestaties zijn oké, maar de belasting is aan de hoge kant."
        else:
            direct_en = "Short answer: performance looks stable right now."
            direct_nl = "Kort antwoord: prestaties lijken nu stabiel."

        lines_en = [
            f"**{direct_en}**",
            "",
            "**Current machine status**",
            f"- Average load: {avg_load:.2f}A",
            f"- Anomalies: {anomalies}",
            f"- Bottlenecks: {bottlenecks}",
        ]
        lines_nl = [
            f"**{direct_nl}**",
            "",
            "**Huidige machinestatus**",
            f"- Gemiddelde belasting: {avg_load:.2f}A",
            f"- Afwijkingen: {anomalies}",
            f"- Knelpunten: {bottlenecks}",
        ]

        for summary in machine_summaries[: min(4, len(machine_summaries))]:
            lines_en.append(f"- {summary['label']}: {summary['current']:.2f}A, {summary['status']}, trend {summary['trend_label']}")
            lines_nl.append(f"- {summary['label']}: {summary['current']:.2f}A, {summary['status']}, trend {summary['trend_label']}")

        if fallback_machine:
            lines_en.append(f"- Action: check {fallback_machine['label']} first")
            lines_nl.append(f"- Actie: controleer {fallback_machine['label']} eerst")

        return result(
            t("\n".join(lines_en), "\n".join(lines_nl)),
            target_page="Dashboard",
            target_label=t("Open live dashboard", "Open live dashboard"),
            chart_machine=fallback_machine["machine"] if fallback_machine else None,
        )

    return result(
        t(
            "No machine data available yet. Connect a device or run simulation to get live answers.",
            "Nog geen machine-data beschikbaar. Verbind een apparaat of start simulatie voor live antwoorden."
        ),
        target_page="Device Connection",
        target_label=t("Open device connection", "Open device connection"),
        target_state={"pending_mode": "Live"},
    )


def build_ai_context_snapshot(max_events=8):
    """Compact context payload for external AI so it can answer with current app data."""
    df_local = st.session_state.get("df", pd.DataFrame())
    machine_names = list(st.session_state.get("machine_names", []))
    event_history = list(st.session_state.get("event_history", []))

    machine_items = []
    if isinstance(df_local, pd.DataFrame) and not df_local.empty:
        machine_cols = [c for c in df_local.columns if str(c).startswith("current_")]
        for col_name in machine_cols:
            try:
                idx = int(str(col_name).split("_")[1])
            except Exception:
                continue
            series = pd.to_numeric(df_local[col_name], errors="coerce").dropna()
            if series.empty:
                continue
            current_value = float(series.iloc[-1])
            average_value = float(series.mean())
            peak_value = float(series.max())
            trend_value = float(np.polyfit(range(len(series)), series.to_numpy(dtype=float), 1)[0]) if len(series) > 5 else 0.0
            machine_items.append({
                "machine_index": idx,
                "machine_name": machine_names[idx - 1] if idx - 1 < len(machine_names) else f"Machine {idx}",
                "current_a": round(current_value, 3),
                "avg_a": round(average_value, 3),
                "peak_a": round(peak_value, 3),
                "trend": round(trend_value, 5),
            })

    events = []
    for event in event_history[: max(1, int(max_events))]:
        events.append({
            "timestamp": str(event.get("timestamp", "")),
            "type": str(event.get("type", "")),
            "message": str(event.get("message", "")),
            "machine": event.get("machine"),
        })

    avg_load = 0.0
    if machine_items:
        avg_load = float(np.mean([item["avg_a"] for item in machine_items]))

    return {
        "mode": str(st.session_state.get("mode", "Simulation")),
        "device_connected": bool(st.session_state.get("device_connected", False)),
        "cloud_bridge_enabled": bool(st.session_state.get("cloud_bridge_enabled", False)),
        "num_machines": int(st.session_state.get("num_machines", len(machine_items) or 0)),
        "anomalies_count": len(st.session_state.get("anomalies", [])),
        "bottlenecks_count": len(st.session_state.get("bottlenecks", [])),
        "avg_load_a": round(avg_load, 3),
        "machine_items": machine_items,
        "recent_events": events,
    }


def query_external_ai_answer(question, context_payload):
    """Query external AI if API key exists; return None when unavailable."""
    api_key = str(os.getenv("OPENAI_API_KEY", "")).strip()
    if not api_key:
        try:
            api_key = str(st.secrets.get("OPENAI_API_KEY", "")).strip()
        except Exception:
            api_key = ""
    if not api_key:
        return None

    model_name = str(os.getenv("OPENAI_MODEL", "gpt-4.1-mini")).strip() or "gpt-4.1-mini"
    response_style = str(st.session_state.get("ai_response_style", "Detailed"))
    technical_level = str(st.session_state.get("ai_technical_level", "Simple"))
    auto_advice = bool(st.session_state.get("ai_auto_advice", True))
    style_instruction = "Keep answers short (max 4 bullets)." if response_style == "Short" else "Give a complete but concise answer (max 8 bullets)."
    level_instruction = "Use plain language and avoid jargon." if technical_level == "Simple" else "Use technical terms where useful."
    advice_instruction = "Always include one next action." if auto_advice else "Do not include advice unless explicitly asked."
    system_prompt = (
        "You are an industrial monitoring assistant inside a Streamlit app. "
        "Answer using ONLY provided context. Keep answers concise and practical. "
        "Use bullet points. "
        "If question language is Dutch, answer in Dutch; otherwise English."
        f" {style_instruction} {level_instruction} {advice_instruction}"
    )
    user_prompt = (
        f"Question: {str(question or '').strip()}\n\n"
        f"Context JSON:\n{json.dumps(context_payload, ensure_ascii=False)}"
    )

    payload = {
        "model": model_name,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    req = urllib_request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib_request.urlopen(req, timeout=15) as resp:
            response_data = json.loads(resp.read().decode("utf-8"))
        text = (
            response_data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        text = str(text or "").strip()
        return text or None
    except (urllib_error.URLError, TimeoutError, ValueError, KeyError, IndexError):
        return None


def build_conversation_context_prompt(question, conversation_history):
    """Build a prompt that includes recent conversation history for follow-up understanding."""
    if not conversation_history or len(conversation_history) == 0:
        return question
    
    # Include last 3 conversation turns for context
    recent_turns = conversation_history[-3:]
    context_lines = []
    for turn in recent_turns:
        context_lines.append(f"Q: {turn.get('question', '')}")
        context_lines.append(f"A: {turn.get('answer', '')}")
    
    context_text = "\n".join(context_lines)
    enhanced_prompt = f"""Previous conversation context:
{context_text}

Follow-up question:
{question}"""
    return enhanced_prompt


def resolve_ai_assistant_result(question, conversation_history=None):
    """Use external AI with app context when configured; fallback to local assistant logic."""
    # Enhance question with conversation context if available
    if conversation_history and len(conversation_history) > 0:
        enhanced_question = build_conversation_context_prompt(question, conversation_history)
    else:
        enhanced_question = question
    
    local_result = build_ai_assistant_result(question)  # Always use original question for local intent matching
    context_payload = build_ai_context_snapshot()
    ai_text = query_external_ai_answer(enhanced_question, context_payload)  # Use enhanced question for external AI
    if ai_text:
        local_result["message"] = ai_text
        local_result["source"] = "external"
    else:
        local_result["source"] = "local"
    if not bool(st.session_state.get("ai_auto_advice", True)):
        lines = [line for line in str(local_result.get("message", "")).splitlines() if line.strip()]
        lines = [line for line in lines if ("action:" not in line.lower() and "actie:" not in line.lower())]
        local_result["message"] = "\n".join(lines)
    if str(st.session_state.get("ai_response_style", "Detailed")) == "Short":
        lines = [line for line in str(local_result.get("message", "")).splitlines() if line.strip()]
        local_result["message"] = "\n".join(lines[:5])
    return local_result


def generate_ai_assistant_response(question):
    return resolve_ai_assistant_result(question)["message"]


def render_ai_assistant_machine_chart(machine_idx, df_local):
    """Render a focused trend chart for the machine referenced by the AI assistant."""
    if not machine_idx or not isinstance(df_local, pd.DataFrame) or df_local.empty:
        return
    col_name = f"current_{int(machine_idx)}"
    if col_name not in df_local.columns:
        return

    chart_df = df_local.copy().tail(60)
    y_values = pd.to_numeric(chart_df[col_name], errors="coerce")
    if y_values.dropna().empty:
        return

    if "timestamp" in chart_df.columns:
        x_values = pd.to_datetime(chart_df["timestamp"], errors="coerce")
        if x_values.isna().all():
            x_values = list(range(len(chart_df)))
    else:
        x_values = list(range(len(chart_df)))

    machine_names = list(st.session_state.get("machine_names", []))
    machine_label = machine_names[int(machine_idx) - 1] if int(machine_idx) - 1 < len(machine_names) else f"Machine {int(machine_idx)}"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode="lines",
        name=machine_label,
        line=dict(color="#3b82f6", width=3),
        fill="tozeroy",
        fillcolor="rgba(59, 130, 246, 0.18)",
    ))
    fig.update_layout(
        title=t(f"Trend for {machine_label}", f"Trend voor {machine_label}"),
        template=plotly_template,
        height=280,
        margin=dict(l=20, r=20, t=44, b=20),
        plot_bgcolor=plot_bg_color,
        paper_bgcolor=plot_bg_color,
        font=dict(color=plot_text_color),
        xaxis=dict(gridcolor=plot_grid_color, tickfont=dict(color=plot_tick_color)),
        yaxis=dict(title=t("Current (A)", "Stroom (A)"), gridcolor=plot_grid_color, zerolinecolor=plot_line_color, tickfont=dict(color=plot_tick_color)),
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False, "displaylogo": False})


def render_capability_action_grid(section_key, scope="all", show_buttons=True):
    """Functional value section with page-specific item sets."""
    items = [
        {
            "id": "smart_ai",
            "title": t("Smart AI", "Slimme AI"),
            "desc": t("Automatic insights and predictions.", "Automatische inzichten en voorspellingen."),
            "btn": t("Open AI Insights", "Open AI Inzichten"),
            "action": "ai_insights",
        },
        {
            "id": "easy_use",
            "title": t("Easy to use", "Makkelijk gebruik"),
            "desc": t("One-click flow for key actions.", "Eén-klik flow voor kernacties."),
            "btn": t("Go to Dashboard", "Ga naar Dashboard"),
            "action": "dashboard",
        },
        {
            "id": "clear_ui",
            "title": t("Clear UI", "Duidelijke UI"),
            "desc": t("Keep the default clean overview.", "Behoud het standaard overzicht."),
            "btn": t("Open Overview", "Open Overzicht"),
            "action": "overview",
        },
        {
            "id": "smart_alerts",
            "title": t("Smart notifications", "Slimme meldingen"),
            "desc": t("Only relevant alerts.", "Alleen relevante meldingen."),
            "btn": t("Notification settings", "Meldingsinstellingen"),
            "action": "notifications",
        },
        {
            "id": "live_data",
            "title": t("Live data", "Live data"),
            "desc": t("Real-time status and performance.", "Real-time status en prestaties."),
            "btn": t("Switch to Live", "Schakel naar Live"),
            "action": "live",
        },
        {
            "id": "personalization",
            "title": t("Personalization", "Personalisatie"),
            "desc": t("Adjust app behavior to preference.", "Pas de app aan naar voorkeur."),
            "btn": t("Open Personalization", "Open Personalisatie"),
            "action": "personalization",
        },
        {
            "id": "ai_assistant",
            "title": t("AI assistant", "AI assistent"),
            "desc": t("Ask questions directly in the app.", "Stel direct vragen in de app."),
            "btn": t("Open Assistant", "Open Assistent"),
            "action": "assistant",
        },
        {
            "id": "plug_play",
            "title": t("Plug & play + offline", "Plug & play + offline"),
            "desc": t("Quick setup and local fallback behavior.", "Snelle setup en lokaal fallback gedrag."),
            "btn": t("Connect Device", "Verbind apparaat"),
            "action": "connect_device",
        },
    ]

    scope_map = {
        "all": ["smart_ai", "easy_use", "clear_ui", "smart_alerts", "live_data", "personalization", "ai_assistant", "plug_play"],
        "demo": ["easy_use", "clear_ui", "plug_play", "personalization"],
        "live": ["live_data", "smart_alerts", "smart_ai", "ai_assistant"],
        "platform": ["smart_ai", "easy_use", "smart_alerts", "live_data", "personalization", "ai_assistant", "plug_play"],
    }
    selected_ids = set(scope_map.get(scope, scope_map["all"]))
    visible_items = [item for item in items if item["id"] in selected_ids]

    cols = st.columns(2)
    for idx, item in enumerate(visible_items):
        with cols[idx % 2]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"### {item['title']}")
            st.caption(item["desc"])
            if show_buttons and st.button(item["btn"], key=f"{section_key}_{item['id']}", width="stretch", type="secondary"):
                action = item["action"]
                if action == "ai_insights":
                    st.session_state.page = "AI Insights"
                    st.rerun()
                elif action == "dashboard":
                    st.session_state.page = "Dashboard"
                    st.rerun()
                elif action == "overview":
                    st.session_state.dashboard_preference = "Overview"
                    st.session_state.page = "Dashboard"
                    st.rerun()
                elif action == "notifications":
                    st.session_state.page = "Settings"
                    st.session_state.settings_active_tab = "account"
                    st.session_state.settings_account_section = "meldingen"
                    st.rerun()
                elif action == "live":
                    if st.session_state.get("device_connected", False):
                        st.session_state.mode = "Live"
                        st.session_state.page = "Dashboard"
                    else:
                        st.session_state.page = "Device Connection"
                        st.session_state.pending_mode = "Live"
                    st.rerun()
                elif action == "personalization":
                    st.session_state.page = "Settings"
                    st.session_state.settings_active_tab = "general"
                    st.rerun()
                elif action == "assistant":
                    st.session_state.page = "AI Insights"
                    st.session_state.ai_assistant_open = True
                    st.rerun()
                elif action == "connect_device":
                    st.session_state.page = "Device Connection"
                    st.session_state.pending_mode = "Live"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

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

theme_tokens = get_theme_tokens()
is_light_theme = bool(theme_tokens["is_light"])
plotly_template = theme_tokens["plot_template"]
plot_bg_color = theme_tokens["surface"]
plot_text_color = theme_tokens["text"]
plot_tick_color = theme_tokens["muted"]
plot_grid_color = theme_tokens["plot_grid"]
plot_line_color = theme_tokens["border"]
plot_legend_bg = theme_tokens["card"]
plot_legend_border = theme_tokens["border"]

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
    "Webshop",
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
CLIENT_RENDERED_PAGES = {"Dashboard", "Factory Analysis"}

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
    "Webshop": "🛒 Webshop",
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

    protected_pages = {"Dashboard", "Factory Analysis"}
    if not st.session_state.get("auth_user") and current_page in protected_pages:
        return current_page

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
            is_disabled = page_name == "AI Insights"
            help_text = None
            if is_disabled:
                help_text = t("Coming soon", "Binnenkort beschikbaar")
            
            if st.button(
                label,
                key=f"top_nav_{page_name.replace(' ', '_').lower()}",
                width="stretch",
                type="primary" if is_active else "secondary",
                disabled=is_active or is_disabled,
                help=help_text,
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
    theme = get_theme_tokens()

    active_platform = " pnav-active" if current == "Platform" else ""
    active_about = " pnav-active" if current == "About" else ""
    active_contact = " pnav-active" if current == "Contact" else ""
    active_faq = " pnav-active" if current == "FAQ" else ""
    active_support = " pnav-active" if current == "Support" else ""
    active_account = " pnav-active" if current == "Account" else ""
    auth_token = str(st.query_params.get("auth", "") or "").strip()
    auth_suffix = f"&auth={auth_token}" if auth_token else ""
    logo_data_uri = get_logo_data_uri()
    logo_markup = (
        f'<img src="{logo_data_uri}" alt="Smart Factory logo" '
        'style="width:34px; height:34px; border-radius:10px; object-fit:cover; box-shadow:0 6px 16px rgba(14,165,233,0.28);">'
        if logo_data_uri
        else '<div class="pnav-brand-badge">SF</div>'
    )

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
            top: 84px;
            z-index: 10001;
            width: 58px;
            height: 58px;
            background: linear-gradient(135deg, {theme['accent']} 0%, #22d3ee 100%);
            border: 2px solid {theme['accent_hover']};
            border-radius: 14px;
            box-shadow: 0 4px 24px {theme['accent_glow']}, 0 2px 8px rgba(0,0,0,0.25);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: right 0.3s cubic-bezier(0.4,0,0.2,1), box-shadow 0.2s;
            user-select: none;
        }}
        .pnav-hamburger:hover {{
            box-shadow: 0 6px 32px {theme['accent_glow']}, 0 2px 12px rgba(0,0,0,0.28);
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
            top: 72px;
            height: calc(100vh - 72px);
            width: 240px;
            background: {theme['card']};
            border-left: 1px solid {theme['border']};
            z-index: 10000;
            padding: 28px 14px;
            box-shadow: -6px 0 30px rgba(0,0,0,0.22);
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
            color: {theme['text']};
            margin: 0 0 18px 0;
            padding-bottom: 12px;
            border-bottom: 1px solid {theme['border']};
            letter-spacing: 0.04em;
        }}
        .pnav-brand {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 0 0 16px 0;
            padding: 0 0 12px 0;
            border-bottom: 1px solid {theme['border']};
        }}
        .pnav-brand-badge {{
            width: 34px;
            height: 34px;
            border-radius: 10px;
            background: linear-gradient(135deg, #14b8a6, #0ea5e9);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 0.82rem;
            letter-spacing: 0.02em;
            box-shadow: 0 6px 16px rgba(14,165,233,0.28);
        }}
        .pnav-brand-text {{
            display: flex;
            flex-direction: column;
            line-height: 1.05;
        }}
        .pnav-brand-kicker {{
            font-size: 0.64rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {theme['accent']};
            font-weight: 700;
        }}
        .pnav-brand-title {{
            font-size: 0.9rem;
            color: {theme['text']};
            font-weight: 700;
            margin-top: 2px;
        }}
        .pnav-item {{
            display: block;
            color: {theme['text']};
            text-decoration: none;
            background: {theme['surface']};
            border: 1px solid {theme['border']};
            border-radius: 10px;
            padding: 10px 14px;
            margin-bottom: 8px;
            font-weight: 600;
            font-size: 0.95rem;
            transition: background 0.15s, border-color 0.15s;
        }}
        .pnav-item:hover {{
            background: rgba(59,130,246,0.16);
            border-color: {theme['accent']};
            color: {theme['text']};
        }}
        .pnav-item.pnav-active {{
            background: linear-gradient(135deg, {theme['accent']} 0%, #22d3ee 100%);
            border-color: {theme['accent_hover']};
            color: #06223f;
            cursor: default;
            pointer-events: none;
        }}
        .pnav-account {{
            margin-top: 14px;
            border: 1px solid {theme['border']};
            background: {theme['surface']};
            border-radius: 12px;
            padding: 12px;
        }}
        .pnav-account-title {{
            color: {theme['text']};
            font-size: 0.9rem;
            font-weight: 800;
            margin: 0 0 8px 0;
        }}
        .pnav-account-row {{
            color: {theme['muted']};
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
            border: 1px solid {theme['border']};
            background: rgba(59,130,246,0.12);
            color: {theme['muted']};
            font-size: 0.72rem;
            font-weight: 700;
        }}
        </style>
        <input type="checkbox" id="pnav-toggle" style="display:none">
        <label for="pnav-toggle" class="pnav-hamburger" title="{t('Menu', 'Menu')}">
            <span class="pnav-hamburger-icon"></span>
        </label>
        <div class="pnav-panel">
            <div class="pnav-brand">
                {logo_markup}
                <div class="pnav-brand-text">
                    <span class="pnav-brand-kicker">{t('Smart Factory', 'Smart Factory')}</span>
                    <span class="pnav-brand-title">{t('Monitoring Suite', 'Monitoring Suite')}</span>
                </div>
            </div>
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
    is_light = st.session_state.get("theme_preference", "Dark") == "Light"
    theme = {
        "surface": "#dfe8f3" if is_light else "#0f172a",
        "card": "#d8e3f0" if is_light else "#1e293b",
        "border": "#b6c8dc" if is_light else "#334155",
        "text": "#0f172a" if is_light else "#f8fafc",
        "muted": "#2e4662" if is_light else "#94a3b8",
        "grid": "rgba(148,163,184,0.25)" if is_light else "rgba(148,163,184,0.22)",
        "template": "plotly_white" if is_light else "plotly_dark",
    }
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
        "theme": theme,
    }
    config_json = json.dumps(config)

    return f"""
        <div id="rt-root" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color:{theme['text']};">
            <div id="rt-metrics" style="display:{'grid' if show_metrics else 'none'}; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin:0 0 18px 0;"></div>
            <div style="margin:0 0 10px 0; font-size:1.1rem; font-weight:700; color:{theme['text']};">{panel_title}</div>
            <div id="rt-gauges" style="width:100%; min-height:320px;"></div>
            <div style="margin:18px 0 10px 0; font-size:1.1rem; font-weight:700; color:{theme['text']};">Stroom Over Tijd</div>
            <div id="rt-trend" style="width:100%; min-height:420px; background:{theme['surface']}; border:1px solid {theme['border']}; border-radius:14px; padding:8px;"></div>
        </div>
        <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
        <script>
            const config = {config_json};
            const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
            const machineNames = config.machineNames;
            const endpoints = config.endpoints;
            const colors = config.colors;
            const theme = config.theme || {{}};
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
                    <div style="background:${{theme.card}};border:1px solid ${{theme.border}};border-radius:14px;padding:14px 16px;">
                        <div style="font-size:0.8rem;color:${{theme.muted}};margin-bottom:6px;">${{label}}</div>
                        <div style="font-size:1.25rem;font-weight:700;color:${{theme.text}};">${{value}}</div>
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
                        title: {{ text: name, font: {{ size: 13, color: theme.text }} }},
                        number: {{ suffix: ' A', font: {{ size: 23, color: colors[index % colors.length], family: 'monospace' }} }},
                        gauge: {{
                            axis: {{
                                range: [0, 8],
                                tickmode: 'linear',
                                dtick: 1,
                                tickwidth: 1,
                                tickcolor: theme.border,
                                tickfont: {{ size: 11, color: theme.muted }},
                            }},
                            bar: {{ color: colors[index % colors.length], thickness: 0.34 }},
                            bgcolor: theme.card,
                            borderwidth: 2,
                            bordercolor: 'rgba(59,130,246,0.25)',
                            steps: [
                                {{ range: [0, 2], color: 'rgba(16,185,129,0.26)' }},
                                {{ range: [2, 4], color: 'rgba(56,189,248,0.24)' }},
                                {{ range: [4, 6], color: 'rgba(245,158,11,0.24)' }},
                                {{ range: [6, 8], color: 'rgba(239,68,68,0.26)' }},
                            ],
                            threshold: {{
                                line: {{ color: '#f43f5e', width: 4 }},
                                thickness: 0.8,
                                value: 6.2,
                            }},
                        }},
                        domain: {{ x: [x0, x1], y: [y0, y1] }},
                    }};
                }});
                Plotly.react('rt-gauges', data, {{
                    template: theme.template,
                    paper_bgcolor: theme.surface,
                    plot_bgcolor: theme.surface,
                    font: {{ color: theme.text }},
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
                    template: theme.template,
                    height,
                    margin: {{ l: isCompact ? 52 : 62, r: 20, t: 22, b: isCompact ? 68 : 54 }},
                    paper_bgcolor: theme.surface,
                    plot_bgcolor: theme.surface,
                    hovermode: 'x unified',
                    hoverlabel: {{
                        bgcolor: theme.card,
                        bordercolor: theme.border,
                        font: {{ color: theme.text, size: 12 }},
                    }},
                    legend: {{
                        orientation: 'h',
                        yanchor: 'bottom',
                        y: 1.03,
                        xanchor: 'left',
                        x: 0,
                        font: {{ size: 12, color: theme.text }},
                        bgcolor: theme.card,
                        bordercolor: theme.border,
                        borderwidth: 1,
                    }},
                    xaxis: {{
                        title: {{ text: 'Tijd', font: {{ size: 13, color: theme.text }} }},
                        categoryorder: 'array',
                        categoryarray: formattedTimes,
                        tickmode: 'array',
                        tickvals: tickValues,
                        tickfont: {{ size: 12, color: theme.muted }},
                        tickangle: isCompact ? -18 : 0,
                        showgrid: true,
                        gridcolor: theme.grid,
                        linecolor: theme.border,
                        zeroline: false,
                    }},
                    yaxis: {{
                        title: {{ text: 'Stroom (A)', font: {{ size: 13, color: theme.text }} }},
                        range: [0, 8],
                        dtick: 1,
                        tickfont: {{ size: 12, color: theme.muted }},
                        showgrid: true,
                        gridcolor: theme.grid,
                        zeroline: true,
                        zerolinecolor: theme.border,
                        linecolor: theme.border,
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

                const availableEndpoints = endpoints.filter((endpoint) => Boolean(endpoint));
                if (!availableEndpoints.length) {{
                    return;
                }}

                const responses = await Promise.all(endpoints.map(async (endpoint) => {{
                    if (!endpoint) return null;
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


def build_client_snapshot_component_html(snapshot_items, panel_title):
    """Return a lightweight client-side snapshot bar chart to avoid Streamlit chart flicker."""
    color_scale = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#ec4899', '#84cc16', '#a78bfa']
    is_light = st.session_state.get("theme_preference", "Dark") == "Light"
    config = {
        "items": list(snapshot_items),
        "panelTitle": str(panel_title),
        "colors": color_scale,
        "template": "plotly_white" if is_light else "plotly_dark",
        "surface": "#dfe8f3" if is_light else "#0f172a",
        "border": "#b6c8dc" if is_light else "#1e293b",
        "text": "#0f172a" if is_light else "#f8fafc",
    }
    config_json = json.dumps(config)
    html = """
        <div id="snapshot-root" style="width:100%; min-height:280px; background:__SNAP_SURFACE__; border:1px solid __SNAP_BORDER__; border-radius:14px; padding:8px;"></div>
        <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
        <script>
            const snapshotConfig = __SNAPSHOT_CONFIG__;
            const root = document.getElementById('snapshot-root');

            function renderSnapshot() {
                const items = snapshotConfig.items || [];
                const labels = items.map((item) => item.label);
                const values = items.map((item) => item.value);
                const colors = values.map((_, index) => snapshotConfig.colors[index % snapshotConfig.colors.length]);

                Plotly.react(root, [{
                    x: labels,
                    y: values,
                    type: 'bar',
                    marker: { color: colors },
                    text: values.map((value) => `${Number(value).toFixed(2)}A`),
                    textposition: 'outside',
                    hovertemplate: '%{x}<br>Stroom: %{y:.2f} A<extra></extra>',
                }], {
                    title: snapshotConfig.panelTitle,
                    template: snapshotConfig.template,
                    height: 280,
                    margin: { l: 20, r: 20, t: 42, b: 20 },
                    plot_bgcolor: snapshotConfig.surface,
                    paper_bgcolor: snapshotConfig.surface,
                    font: { color: snapshotConfig.text },
                    yaxis: { title: 'Stroom (A)', range: [0, 8] },
                    xaxis: { title: 'Machines' },
                }, { displayModeBar: false, responsive: true, displaylogo: false });
            }

            renderSnapshot();
            window.addEventListener('resize', renderSnapshot);
        </script>
        """
    html = html.replace("__SNAPSHOT_CONFIG__", config_json)
    html = html.replace("__SNAP_SURFACE__", config["surface"])
    html = html.replace("__SNAP_BORDER__", config["border"])
    return html


def render_client_snapshot_panel(snapshot_items, panel_title):
    if not isinstance(snapshot_items, list) or len(snapshot_items) == 0:
        st.info(t("No machine snapshot available yet.", "Nog geen machine-snapshot beschikbaar."))
        return

    labels = [str(item.get("label", "-")) for item in snapshot_items]
    values_amp = []
    for item in snapshot_items:
        raw_value = pd.to_numeric(item.get("value", 0.0), errors="coerce")
        value = float(raw_value) if pd.notna(raw_value) and np.isfinite(float(raw_value)) else 0.0
        values_amp.append(value)
    converted = [convert_amp_value(v) for v in values_amp]
    values = [v[0] for v in converted]
    unit = converted[0][1] if converted else "W"
    color_scale = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#ec4899', '#84cc16', '#a78bfa']
    machine_colors = dict(st.session_state.get("machine_colors", {}))
    bar_colors = []
    for idx, label in enumerate(labels):
        color = machine_colors.get(label)
        if not color:
            color = color_scale[idx % len(color_scale)]
        bar_colors.append(color)

    fig_snapshot = go.Figure()
    fig_snapshot.add_trace(go.Bar(
        x=labels,
        y=values,
        marker_color=bar_colors,
        text=[f"{value:.2f}{unit}" for value in values],
        textposition='outside',
        hovertemplate=t(f'%{{x}}<br>Value: %{{y:.2f}} {unit}<extra></extra>', f'%{{x}}<br>Waarde: %{{y:.2f}} {unit}<extra></extra>'),
    ))
    y_max = max(values) * 1.25 if values else 8.0
    fig_snapshot.update_layout(
        title=str(panel_title),
        template=plotly_template,
        height=290,
        margin=dict(l=20, r=20, t=42, b=20),
        plot_bgcolor=plot_bg_color,
        paper_bgcolor=plot_bg_color,
        font=dict(color=plot_text_color),
        yaxis=dict(title=t(f'Value ({unit})', f'Waarde ({unit})'), range=[0, max(2.0, y_max)], gridcolor=plot_grid_color),
        xaxis=dict(title=t('Machines', 'Machines')),
    )
    st.plotly_chart(fig_snapshot, width="stretch", config={'displayModeBar': False, 'displaylogo': False})


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

    endpoints = [endpoint_by_name.get(machine_name) for machine_name in machine_names]

    initial_history = {
        "times": [],
        "series": {name: [] for name in machine_names},
        "snapshot": {},
        "voltage": st.session_state.get("last_voltage"),
    }

    filtered_df = current_df
    period = str(st.session_state.get("data_time_period", "1h"))
    if isinstance(current_df, pd.DataFrame) and not current_df.empty and "timestamp" in current_df.columns:
        timestamp_series = pd.to_datetime(current_df["timestamp"], errors="coerce")
        now_ts = pd.Timestamp.now()
        cutoff = None
        if period == "1h":
            cutoff = now_ts - pd.Timedelta(hours=1)
        elif period == "1d":
            cutoff = now_ts - pd.Timedelta(days=1)
        elif period == "1w":
            cutoff = now_ts - pd.Timedelta(days=7)
        if cutoff is not None:
            filtered_df = current_df.loc[timestamp_series >= cutoff].copy()
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
hero_logo_data_uri = get_logo_data_uri()
hero_logo_markup = (
    f'<img src="{hero_logo_data_uri}" alt="Smart Factory logo" '
    'style="width:44px; height:44px; border-radius:12px; object-fit:cover; box-shadow:0 8px 20px rgba(14,165,233,0.28);">'
    if hero_logo_data_uri
    else '<div style="width:44px; height:44px; border-radius:12px; background:linear-gradient(135deg,#14b8a6,#0ea5e9); color:white; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:1rem; letter-spacing:0.02em; box-shadow:0 8px 20px rgba(14,165,233,0.28);">SF</div>'
)

# If trying to access a protected page without being logged in, show login dialog
if page in PROTECTED_PAGES and not st.session_state.get("auth_user"):
    st.title(t("Login Required", "Inloggen Vereist"))
    st.markdown(
        f"""
        <div class="page-hero">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                {hero_logo_markup}
                <div style="display:flex; flex-direction:column; line-height:1.1;">
                    <span style="font-size:0.76rem; text-transform:uppercase; letter-spacing:0.08em; color:#93c5fd; font-weight:700;">{t('Smart Factory', 'Smart Factory')}</span>
                    <span style="font-size:0.96rem; color:#e2e8f0; font-weight:600;">{t('Monitoring Platform', 'Monitoring Platform')}</span>
                </div>
            </div>
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
    'dashboard_snapshot',
    'factory_analysis',
    'ai_table'  # Add AI table pause state
]
for ck in chart_keys:
    if f'pause_{ck}' not in st.session_state:
        st.session_state[f'pause_{ck}'] = False
    if f'{ck}_snapshot' not in st.session_state:
        st.session_state[f'{ck}_snapshot'] = None

df = st.session_state.df

# Auto-refresh: avoid full-page reruns on client-rendered chart pages
# to prevent visible Plotly remount flicker.
if page in DATA_REFRESH_PAGES and page not in CLIENT_RENDERED_PAGES:
    _refresh_ms = max(1000, int(st.session_state.get("refresh_rate", 2) * 1000))
    st_autorefresh(interval=_refresh_ms, key="data_autorefresh")

df = refresh_data_frame(page)

# Show notification for AI Insights being under construction
if page == "AI Insights" and not st.session_state.ai_insights_notified:
    st.toast(t("🔨 AI Insights is under construction.", "🔨 AI Inzichten is in aanbouw."), icon="⏳")
    st.session_state.ai_insights_notified = True

# Show notification for Webshop being under construction
if page == "Webshop" and not st.session_state.webshop_notified:
    st.toast(t("🔨 Webshop is under construction. Expected Q3 2026.", "🔨 Webshop is in aanbouw. Verwacht Q3 2026."), icon="⏳")
    st.session_state.webshop_notified = True

if page == "Welcome":
    st.title("⌂ Welkom")
    st.markdown(
        f"""
        <div class="page-hero">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                {hero_logo_markup}
                <div style="display:flex; flex-direction:column; line-height:1.1;">
                    <span style="font-size:0.76rem; text-transform:uppercase; letter-spacing:0.08em; color:#93c5fd; font-weight:700;">Smart Factory</span>
                    <span style="font-size:0.96rem; color:#e2e8f0; font-weight:600;">Monitoring Platform</span>
                </div>
            </div>
            <p class="page-hero-title">Smart Factory Monitoring Platform</p>
            <p class="page-hero-sub">Dit platform helpt operators, maintenance teams en productiecoordinatie om machineprestaties in realtime te monitoren, afwijkingen vroeg te signaleren en onderhoud beter te plannen.</p>
            <span class="page-chip">Realtime monitoring</span>
            <span class="page-chip">AI analyse</span>
            <span class="page-chip">Device onboarding</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader(t("Who We Are", "Wie Wij Zijn"))
    col_about_a, col_about_b = st.columns(2)
    with col_about_a:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### " + t("Mission", "Missie"))
        st.markdown(t(
            "Help production teams with clear, reliable and immediately usable machine insights.",
            "Productieteams helpen met duidelijke, betrouwbare en direct bruikbare machine-inzichten."
        ))
        st.markdown('</div>', unsafe_allow_html=True)

    with col_about_b:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### " + t("Vision", "Visie"))
        st.markdown(t(
            "From reactive maintenance to predictable and data-driven steering on capacity, uptime and quality.",
            "Van reactief onderhoud naar voorspelbaar en datagedreven sturen op capaciteit, uptime en kwaliteit."
        ))
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader(t("What We Do", "Wat Wij Doen"))
    st.markdown(t(
        """- Collection of live machine data via ESP32 devices
- Visualization of current and performance data in clear dashboards
- Detection of anomalies and operational bottlenecks
- Decision support with AI analysis and recommendations
- Recording of events for analysis, audits and follow-up
""",
        """- Verzamelen van live machinegegevens via ESP32-devices
- Visualiseren van stroom- en prestatiegegevens in overzichtelijke dashboards
- Detecteren van afwijkingen en operationele knelpunten
- Ondersteunen van beslissingen met AI-analyses en aanbevelingen
- Vastleggen van gebeurtenissen voor analyse, audits en opvolging
"""
    ))

    st.subheader(t("Organization And Team", "Organisatie En Team"))
    col_team_a, col_team_b = st.columns(2)
    with col_team_a:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### " + t("For Whom", "Voor Wie"))
        st.markdown(t(
            "Operators, technical service, production management and process improvement.",
            "Operators, technische dienst, productieleiding en procesverbetering."
        ))
        st.markdown('</div>', unsafe_allow_html=True)

    with col_team_b:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### " + t("Working Method", "Werkwijze"))
        st.markdown(t(
            "Small steps, fast feedback and continuous improvement based on measurement data.",
            "Kleine stappen, snelle feedback en continue verbetering op basis van meetdata."
        ))
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader(t("What You See In The Platform", "Wat Je In Het Platform Ziet"))
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### " + t("Dashboard", "Dashboard"))
        st.markdown(t(
            "Real-time trends, average load, peaks and current status per machine.",
            "Realtime trends, gemiddelde belasting, pieken en actuele status per machine."
        ))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### " + t("Machine Overview", "Machine Overzicht"))
        st.markdown(t(
            "Comparison between machines, trend analysis and performance differences over time.",
            "Vergelijking tussen machines, trendanalyse en prestatieverschillen over tijd."
        ))
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### " + t("AI Insights", "AI Insights"))
        st.markdown(t(
            "Automatic signaling of anomalies, bottlenecks and recommendations per machine.",
            "Automatische signalering van anomalieen, bottlenecks en aanbevelingen per machine."
        ))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### " + t("History", "Geschiedenis"))
        st.markdown(t(
            "Log of events, connections and anomalies for analysis and reporting.",
            "Logboek van gebeurtenissen, connecties en afwijkingen voor analyse en rapportage."
        ))
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader(t("Support And Contact", "Support En Contact"))
    st.markdown(t(
        """- Device onboarding: via `+ Device Connect` in the top bar
- Technical support: check Device Connection and History first
- Operational questions: use Dashboard and AI Insights as starting point for diagnosis
""",
        """- Device onboarding: via `+ Device Connect` in de bovenbalk
- Technische support: controleer eerst Device Connection en History
- Operationele vragen: gebruik Dashboard en AI Insights als startpunt voor diagnose
"""
    ))

    st.subheader(t("Get Started", "Aan De Slag"))
    st.markdown(t(
        """1. Add a device via `+ Device Connect` in the top bar.
2. Check if Live mode is active and data is coming in.
3. Use Dashboard, Machine Overview and AI Insights for monitoring and optimization.
""",
        """1. Voeg een device toe via `+ Device Connect` in de bovenbalk.
2. Controleer of Live mode actief is en data binnenkomt.
3. Gebruik Dashboard, Machine Overzicht en AI Insights voor monitoring en optimalisatie.
"""
    ))

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if st.button(t("📶 Connect Bluetooth to ESP32", "📶 Bluetooth verbinden met ESP32"), type="primary", width="stretch"):
            st.session_state.welcome_shown = True
            st.session_state.page = "Device Connection"
            st.session_state.pending_mode = 'Live'
            st.rerun()
        if st.button(t("Continue without connecting", "Doorgaan zonder verbinden"), type="secondary", width="stretch"):
            st.session_state.welcome_shown = True
            st.session_state.page = "Dashboard"
            st.rerun()

elif page == "Home":
    st.title(t("⌂ Smart Factory Platform", "⌂ Slimme Fabriek Platform"))

    mode_indicator = st.session_state.get('mode', t('Simulation', 'Simulatie'))
    device_status = t("Live", "Live") if st.session_state.get('device_connected', False) else t("Simulation", "Simulatie")
    endpoint_info = st.session_state.get('device_endpoint', t('Local simulation', 'Lokale simulatie'))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⦿ " + t("Mode", "Modus"), mode_indicator)
    with col2:
        st.metric(t("⦿ Device", "⦿ Apparaat"), device_status)
    with col3:
        st.caption(f"{t('Endpoint', 'Eindpunt')}: {endpoint_info}")

    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown(t(
        """### Welcome to Your Intelligent Factory Dashboard

**Real-time monitoring • AI-driven insights • Optimized production**

This platform gives you complete control over your factory environment with live data, advanced analytics and intelligent recommendations.
""",
        """### Welkom bij jouw Intelligente Fabrieksdashboard

**Real-time monitoring • AI-gedreven inzichten • Geoptimaliseerde productie**

Dit platform geeft je volledige controle over je fabrieksomgeving met live data, geavanceerde analyses en intelligente aanbevelingen.
"""
    ))
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader(t("Quick Demo", "Snelle Demo"))
    quick1, quick2, quick3 = st.columns(3)
    with quick1:
        if st.button(t("Open Demo", "Open Demo"), width="stretch"):
            st.session_state.page = "Dashboard"
            st.rerun()
    with quick2:
        if st.button(t("Connect Device", "Verbind apparaat"), width="stretch"):
            st.session_state.page = "Device Connection"
            st.session_state.pending_mode = "Live"
            st.rerun()
    with quick3:
        if st.button(t("⌬ Ask AI", "⌬ Vraag AI"), width="stretch", type="secondary"):
            st.session_state.page = "AI Insights"
            st.session_state.ai_assistant_open = True
            st.rerun()

    demo_col1, demo_col2 = st.columns(2)
    with demo_col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric(t("Active Machines", "Actieve Machines"), NUM_MACHINES)
        st.metric(t("Data Points", "Data Punten"), len(df))
        st.markdown('</div>', unsafe_allow_html=True)
    with demo_col2:
        avg_demo = float(np.mean([df[f"current_{i}"].mean() for i in range(1, NUM_MACHINES + 1)])) if NUM_MACHINES > 0 else 0.0
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric(t("Avg Load", "Gem. Belasting"), f"{avg_demo:.1f}A")
        st.caption(t("Start with Dashboard for live status, then use AI Insights for recommendations.", "Start met Dashboard voor live status en gebruik daarna AI Insights voor aanbevelingen."))
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer info
    st.markdown("---")
    st.markdown(t(
        """<div style='text-align: center; color: #94a3b8; font-size: 0.9rem;'>
<strong>Tip:</strong> Use the top navigation bar for quick navigation and settings<br>
Data is automatically updated every 2 seconds
</div>
""",
        """<div style='text-align: center; color: #94a3b8; font-size: 0.9rem;'>
<strong>Tip:</strong> Gebruik de bovenste navigatiebalk voor snelle navigatie en instellingen<br>
Data wordt automatisch elke 2 seconden bijgewerkt
</div>
"""
    ), unsafe_allow_html=True)

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
                series_num = pd.to_numeric(dashboard_df[column_name], errors="coerce").dropna()
                if not series_num.empty:
                    current_snapshot[column_name] = float(series_num.iloc[-1])

    if current_snapshot:
        st.session_state['dashboard_snapshot_snapshot'] = current_snapshot.copy()
    else:
        current_snapshot = dict(st.session_state.get('dashboard_snapshot_snapshot') or {})

    if not current_snapshot:
        last_values = dict(st.session_state.get("last_current_values", {}))
        for machine_index in range(1, NUM_MACHINES + 1):
            key = f"current_{machine_index}"
            if key in last_values:
                current_snapshot[key] = float(last_values.get(key, 0.0) or 0.0)

    active_machine_count = len(current_snapshot)
    machine_name_lookup = {
        f"current_{index}": st.session_state.machine_names[index - 1]
        if index - 1 < len(st.session_state.machine_names)
        else f"M{index}"
        for index in range(1, NUM_MACHINES + 1)
    }
    ordered_visible_machine_indices = get_ordered_visible_machine_indices(NUM_MACHINES)
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
        <div style="background:{theme_tokens['hero_gradient']}; border:1px solid {theme_tokens['border']}; border-left:6px solid {status_color}; border-radius:18px; padding:18px 20px; margin:8px 0 16px 0; box-shadow:0 14px 28px {theme_tokens['accent_glow']};">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:16px; flex-wrap:wrap;">
                <div>
                    <div style="font-size:0.82rem; color:{theme_tokens['subtle']}; text-transform:uppercase; letter-spacing:0.08em;">{t('Quick status', 'Snelle status')}</div>
                    <div style="font-size:1.35rem; font-weight:800; color:{theme_tokens['text']}; margin-top:4px;">{overview_status}</div>
                    <div style="font-size:0.95rem; color:{theme_tokens['muted']}; margin-top:6px;">{overview_detail}</div>
                </div>
                <div style="font-size:0.82rem; color:{theme_tokens['subtle']}; text-align:right; min-width:180px;">
                    <div>{t('Source', 'Bron')}: <span style="color:{theme_tokens['text']}; font-weight:700;">{device_status}</span></div>
                    <div style="margin-top:4px;">{t('Endpoint', 'Endpoint')}: <span style="color:{theme_tokens['muted']};">{endpoint_info}</span></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="page-section">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

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

    st.markdown('<div class="page-section">', unsafe_allow_html=True)
    st.subheader(t("⌁ Control Overview", "⌁ Controle Overzicht"))
    overview_col1, overview_col2 = st.columns([1.4, 1])

    with overview_col1:
        machine_labels = []
        machine_values = []
        for machine_idx in ordered_visible_machine_indices:
            key = f"current_{machine_idx}"
            if key in current_snapshot:
                machine_labels.append(machine_name_lookup.get(key, f"Machine {machine_idx}"))
                machine_values.append(current_snapshot[key])

        if not machine_labels and current_snapshot:
            for key in sorted(current_snapshot.keys()):
                machine_labels.append(machine_name_lookup.get(key, key))
                machine_values.append(float(current_snapshot.get(key, 0.0) or 0.0))

        show_snapshot = bool(st.session_state.get("dashboard_show_snapshot_chart", True))
        if not show_snapshot:
            st.info(t("Machine Snapshot is hidden in settings.", "Machine Snapshot is verborgen in instellingen."))
            if st.button(t("Show Machine Snapshot", "Toon Machine Snapshot"), key="dashboard_enable_snapshot", type="secondary"):
                st.session_state.dashboard_show_snapshot_chart = True
                st.rerun()
        elif machine_labels:
            render_client_snapshot_panel(
                snapshot_items=[
                    {"label": label, "value": value}
                    for label, value in zip(machine_labels, machine_values)
                ],
                panel_title=t("Machine Snapshot", "Machine Snapshot"),
            )
            last_ts = None
            if isinstance(dashboard_df, pd.DataFrame) and not dashboard_df.empty and "timestamp" in dashboard_df.columns:
                try:
                    last_ts = pd.to_datetime(dashboard_df["timestamp"].iloc[-1], errors="coerce")
                except Exception:
                    last_ts = None
            if last_ts is not None and not pd.isna(last_ts):
                st.caption(t(f"Snapshot updated: {last_ts.strftime('%H:%M:%S')}", f"Snapshot bijgewerkt: {last_ts.strftime('%H:%M:%S')}"))
        else:
            st.warning(t("No snapshot data available yet.", "Nog geen snapshotdata beschikbaar."))

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
        if bool(st.session_state.get("dashboard_show_history_chart", True)):
            fig_events = go.Figure()
            fig_events.add_trace(go.Bar(
                x=list(event_counts.keys()),
                y=list(event_counts.values()),
                marker_color=['#ef4444', '#f97316', "#10b91e"],
            ))
            fig_events.update_layout(
                title=t("History Overview", "Geschiedenis Overzicht"),
                template=plotly_template,
                height=220,
                margin=dict(l=20, r=20, t=42, b=20),
                plot_bgcolor=plot_bg_color,
                paper_bgcolor=plot_bg_color,
                font=dict(color=plot_text_color),
                yaxis=dict(title=t("Count", "Aantal"), rangemode='tozero', dtick=1),
            )
            st.plotly_chart(fig_events, width="stretch", config={'displayModeBar': False, 'displaylogo': False})

        latest_event = event_history[0] if event_history else None
        if latest_event:
            st.caption(f"{t('Latest event', 'Laatste gebeurtenis')}: {latest_event.get('type', '-') } | {latest_event.get('timestamp', '')}")
            st.markdown(f"**{latest_event.get('message', '')}**")
    st.markdown('</div>', unsafe_allow_html=True)

    if bool(st.session_state.get("dashboard_show_realtime_panel", True)):
        st.markdown('<div class="page-section">', unsafe_allow_html=True)
        machine_names_for_panel = [
            st.session_state.machine_names[idx - 1]
            for idx in ordered_visible_machine_indices
            if 0 < idx <= len(st.session_state.machine_names)
        ]
        if machine_names_for_panel:
            render_client_realtime_panel(
                machine_names=machine_names_for_panel,
                panel_title=t("⌁ Machine Status — Live", "⌁ Machine Status — Live"),
                show_metrics=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

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
    st.subheader(t("Select Machines to Analyze", "Selecteer Machines te Analyseren"))
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
        st.warning(t(
            "The ESP32 is not yet connected to the site. Connect a device first; then the dashboard opens with the live ampere values.",
            "De ESP32 is nog niet met de site verbonden. Verbind eerst een apparaat; daarna opent het dashboard met de live amperewaarden."
        ))

    # ── Header ──────────────────────────────────────────────────────────────
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown(f"""
        <div class="connect-wrap">
            <p class="connect-title">{t('Devices', 'Apparaten')}</p>
            <p class="connect-sub">{t('Connect an ESP32 via Bluetooth', 'Verbind een ESP32 via Bluetooth')}</p>
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
            st.markdown(f"""
            <div class="connect-status">
                <div class="connect-status-icon">Connected</div>
                <p class="connect-status-label" style="color:#86efac;">{len(connected_devices)} {t('device/devices connected', 'apparaat/apparaten verbonden')}</p>
                <p class="connect-status-meta">{connected_ip}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="connect-status">
                <div class="connect-status-icon">Ready</div>
                <p class="connect-status-label" style="color:#e2e8f0;">{t('No device connected yet', 'Nog geen apparaat verbonden')}</p>
                <p class="connect-status-meta">{t('Scan first via Bluetooth or connect manually via IP.', 'Scan eerst via Bluetooth of verbind handmatig via IP.')}</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Connected devices with disconnect button ────────────────────────────
    if connected_devices:
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            st.markdown(f"<p class='connect-section-label'>{t('Connected devices', 'Verbonden apparaten')}</p>", unsafe_allow_html=True)
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
                        <span class="device-connected-badge">{t('Connected', 'Verbonden')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_btn:
                    st.markdown(f"<div style='height:8px'></div>", unsafe_allow_html=True)
                    if st.button(t("Disconnect", "Verbreek"), key=f"disc_{dev_ip}", width="stretch", type="secondary"):
                        disconnect_device(dev_ip)
                        st.rerun()
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        # ── Already connected → go to dashboard ────────────────────────────────────
        if already_connected:
            if st.button(t("Go to Dashboard →", "Ga naar Dashboard →"), width="stretch", type="primary"):
                st.session_state.page = "Dashboard"
                st.session_state.mode = 'Live'
                st.session_state.pending_mode = None
                st.rerun()
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── BLE Provisioning – set up new ESP32 ────────────────────────
        st.markdown(
            f"<p class='connect-section-label'>"
            f"{t('Set up new ESP32 via Bluetooth', 'Nieuwe ESP32 instellen via Bluetooth')}</p>",
            unsafe_allow_html=True
        )

        if st.button(t("Search for new ESP32 via Bluetooth", "Zoek nieuwe ESP32 via Bluetooth"), width="stretch", type="primary"):
            with st.spinner(t("Scanning Bluetooth… (6 seconds)", "Bluetooth scannen… (6 seconden)")):
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
                st.info(t(
                    "No new ESP32 found via Bluetooth. Make sure the ESP32 is started for the first time (blue LED flashing).",
                    "Geen nieuwe ESP32 gevonden via Bluetooth. Zorg dat de ESP32 voor het eerst opgestart is (blauwe LED knippert)."
                ))

        ble_devices = st.session_state.get("ble_prov_devices", [])
        for ble_dev in ble_devices:
            auto_ssid = ble_dev.get("auto_ssid", "")
            auto_pass = ble_dev.get("auto_pass", "")
            form_key = ble_dev['address'].replace(':', '_')

            if auto_ssid:
                st.success(t("New ESP32 found!", "Nieuwe ESP32 gevonden!"))
                st.markdown(t(
                    f"📶 Your laptop is connected to **{auto_ssid}**. Do you want the ESP32 to also connect to this network?",
                    f"📶 Je laptop is verbonden met **{auto_ssid}**. Wil je dat de ESP32 ook op dit netwerk aansluit?"
                ))
                if auto_pass:
                    # Password found in keychain – customer doesn't need to do anything
                    with st.form(f"prov_form_{form_key}"):
                        submitted = st.form_submit_button(
                            f"✅ {t('Yes, use', 'Ja, gebruik')} {auto_ssid}", width="stretch", type="primary"
                        )
                        prov_ssid = auto_ssid
                        prov_pass = auto_pass
                else:
                    # SSID known, password still needed
                    with st.form(f"prov_form_{form_key}"):
                        st.text_input(t("WiFi network", "WiFi netwerk"), value=auto_ssid, disabled=True)
                        prov_pass = st.text_input(t("WiFi password", "WiFi wachtwoord"), type="password", placeholder=t("Password", "Wachtwoord"))
                        submitted = st.form_submit_button(
                            t("OK - Set WiFi", "Akkoord - WiFi instellen"), width="stretch", type="primary"
                        )
                        prov_ssid = auto_ssid
            else:
                # No network automatically detectable – fill in manually
                st.success(t("New ESP32 found. Enter your WiFi details:", "Nieuwe ESP32 gevonden. Vul je WiFi-gegevens in:"))
                with st.form(f"prov_form_{form_key}"):
                    prov_ssid = st.text_input(t("WiFi name (SSID)", "WiFi naam (SSID)"), placeholder=t("YourWiFiName", "JouwWiFiNaam"))
                    prov_pass = st.text_input(t("WiFi password", "WiFi wachtwoord"), type="password", placeholder=t("Password", "Wachtwoord"))
                    submitted = st.form_submit_button(
                        t("OK - Set WiFi", "Akkoord - WiFi instellen"), width="stretch", type="primary"
                    )
                if submitted:
                    if not prov_ssid or not prov_pass:
                        st.error(t("Enter WiFi name and password.", "Vul WiFi naam en wachtwoord in."))
                    else:
                        with st.spinner(t("ESP32 connecting to WiFi… (can take 30 seconds)", "ESP32 verbindt met WiFi… (kan 30 seconden duren)")):
                            try:
                                ip = ble_provision_esp32(
                                    ble_dev["address"], prov_ssid, prov_pass, timeout=35.0
                                )
                                st.session_state.ble_prov_devices = []
                            except Exception as exc:
                                st.error(t(f"Provisioning failed: {exc}", f"Provisioning mislukt: {exc}"))
                                ip = None

                        if ip:
                            # ESP32 restarts after provisioning – wait until webserver is reachable
                            with st.spinner(t(f"Waiting for ESP32 ({ip}) to start…", f"Wachten tot ESP32 ({ip}) opstart…")):
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
                                st.error(t(
                                    f"ESP32 ({ip}) is connected to WiFi but the web server is not responding. "
                                    "Try connecting manually via the 'Already set up?' menu below.",
                                    f"ESP32 ({ip}) is verbonden met WiFi maar de webserver reageert niet. "
                                    "Probeer handmatig te verbinden via het 'Al eerder ingesteld?' menu hieronder."
                                ))

        # ── Manual IP (emergency for already-provisioned ESP32s) ────────
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        with st.expander(t("Already set up? Connect via IP", "Al eerder ingesteld? Verbind via IP")):
            default_ip   = st.session_state.get('device_ip', '192.168.1.100')
            default_port = int(st.session_state.get('device_port', 80))
            device_ip    = st.text_input(t("IP address", "IP-adres"), value=default_ip, placeholder="192.168.1.100")
            device_port  = st.number_input(t("Port", "Poort"), value=default_port, min_value=1, max_value=65535)
            if st.button(t("Connect", "Verbinden"), key="manual_connect", type="primary", width="stretch"):
                with st.spinner(t(f"Connecting to {device_ip}…", f"Verbinden met {device_ip}…")):
                    try:
                        endpoint, payload, normalized = activate_live_device_connection(
                            device_ip, int(device_port),
                            timeout=st.session_state.get('connection_timeout', 5)
                        )
                        st.rerun()
                    except Exception as exc:
                        st.error(t(f"Connection failed: {exc}", f"Verbinden mislukt: {exc}"))

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
        <div style="background:{theme_tokens['hero_gradient_alt']}; border:1px solid {theme_tokens['border']}; border-radius:22px; padding:28px; margin:6px 0 18px 0; box-shadow:0 14px 28px {theme_tokens['accent_glow']};">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                {hero_logo_markup}
                <div style="display:flex; flex-direction:column; line-height:1.1;">
                    <span style="font-size:0.76rem; text-transform:uppercase; letter-spacing:0.08em; color:{theme_tokens['accent']}; font-weight:700;">{t('Smart Factory', 'Smart Factory')}</span>
                    <span style="font-size:0.96rem; color:{theme_tokens['muted']}; font-weight:600;">{t('Monitoring Platform', 'Monitoring Platform')}</span>
                </div>
            </div>
            <div style="font-size:0.85rem; letter-spacing:0.08em; text-transform:uppercase; color:{theme_tokens['accent']}; font-weight:700;">Smart Factory Suite</div>
            <div style="font-size:2rem; line-height:1.2; font-weight:800; color:{theme_tokens['text']}; margin-top:8px;">
                {t('Real-time monitoring for modern production teams.', 'Realtime monitoring voor moderne productieteams.')}
            </div>
            <div style="font-size:1rem; color:{theme_tokens['muted']}; max-width:880px; margin-top:12px;">
                {t('Follow machine behavior live, prevent downtime, and turn raw telemetry into practical production decisions.', 'Volg machinegedrag live, voorkom downtime en vertaal ruwe telemetrie naar praktische productie-beslissingen.')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cta1, cta2 = st.columns(2)
    with cta1:
        if st.button(t("Open Demo", "Open Demo"), key="platform_open_demo", width="stretch"):
            st.session_state.page = "Dashboard"
            st.rerun()
    with cta2:
        if st.button(t("Connect Device", "Verbind apparaat"), key="platform_connect_device", width="stretch"):
            st.session_state.page = "Device Connection"
            st.session_state.pending_mode = "Live"
            st.rerun()

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

    st.subheader(t("What makes this platform smart", "Wat dit platform slim maakt"))
    render_capability_action_grid("platform_smart", scope="platform", show_buttons=False)
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
        template=plotly_template,
        height=340,
        margin=dict(l=22, r=20, t=22, b=28),
        yaxis=dict(
            title=dict(text=t("Current (A)", "Stroom (A)"), font=dict(size=13, color=plot_text_color)),
            range=[0, 8],
            dtick=1,
            gridcolor=plot_grid_color,
            zerolinecolor=plot_line_color,
            tickfont=dict(size=12, color=plot_tick_color),
        ),
        xaxis=dict(
            title=dict(text=t("Time (sim)", "Tijd (sim)"), font=dict(size=13, color=plot_text_color)),
            range=[0, sim_points - 1],
            tickmode='array',
            tickvals=preview_tickvals,
            showgrid=True,
            gridcolor=plot_grid_color,
            tickfont=dict(size=12, color=plot_tick_color),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="left",
            x=0,
            font=dict(size=12, color=plot_text_color),
            bgcolor=plot_legend_bg,
            bordercolor=plot_legend_border,
            borderwidth=1,
        ),
        plot_bgcolor=plot_bg_color,
        paper_bgcolor=plot_bg_color,
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

    st.subheader(t("Where to buy", "Waar te koop"))
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
        st.markdown(
            f"""
            <a href="?page=Contact{platform_auth_suffix}" target="_self"
               class="inline-btn inline-btn-secondary">
               {t('Contact us', 'Neem contact op')}
            </a>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <a href="?page=Dashboard{platform_auth_suffix}" target="_self"
           class="inline-btn inline-btn-neon" style="margin-top:10px;">
           {t('Start Monitoring Now', 'Start nu met monitoren')}
        </a>
        """,
        unsafe_allow_html=True,
    )

elif page == "About":
    render_platform_sidebar_nav()
    st.markdown(
        f"""
        <div style="background:{theme_tokens['hero_gradient_alt']};border:1px solid {theme_tokens['border']};border-radius:18px;padding:28px 32px;margin-bottom:22px;box-shadow:0 14px 28px {theme_tokens['accent_glow']};">
            <div style="font-size:0.8rem;letter-spacing:0.1em;text-transform:uppercase;color:{theme_tokens['accent']};font-weight:700;">Over ons</div>
            <div style="font-size:2rem;font-weight:800;color:{theme_tokens['text']};margin-top:6px;line-height:1.25;">Wie zijn wij?</div>
            <div style="font-size:1.05rem;color:{theme_tokens['muted']};max-width:820px;margin-top:10px;">Wij helpen bedrijven slimmer en efficiënter werken door middel van data en technologie. Met onze oplossingen krijg je direct inzicht in je machines, processen en prestaties.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(t(
"""
We help companies work smarter and more efficiently through data and technology. With our solutions, you gain direct insight into your machines, processes and performance, so you can make better and faster decisions.

Our focus is on machine monitoring, smart dashboards and data analysis. This helps you recognize failures faster, reduce energy consumption and optimize your production.
""",
"""
Wij helpen bedrijven slimmer en efficiënter werken door middel van data en technologie. Met onze oplossingen krijg je direct inzicht in je machines, processen en prestaties, zodat je betere en snellere beslissingen kunt maken.

Onze focus ligt op machine monitoring, slimme dashboards en data-analyse. Hiermee kun je storingen sneller herkennen, energieverbruik verlagen en je productie optimaliseren.
"""
    ))

    st.subheader(t("Our philosophy", "Onze filosofie"))
    st.markdown(t(
"""
We believe that technology doesn't have to be complicated. That's why we develop systems that are not only powerful, but also clear and easy to use.
""",
"""
Wij geloven dat technologie niet ingewikkeld hoeft te zijn. Daarom ontwikkelen wij systemen die niet alleen krachtig zijn, maar ook overzichtelijk en makkelijk te gebruiken.
"""
    ))

    st.subheader(t("For your business", "Voor jouw bedrijf"))
    st.markdown(t(
"""
Whether you're a small company or a growing organization, we provide a solution that grows with you. This way you get the most out of your data and your business.
""",
"""
Of je nu een klein bedrijf bent of een groeiende organisatie, wij zorgen voor een oplossing die met je meegroeit. Zo haal je het maximale uit je data én je bedrijf.
"""
    ))


elif page == "Contact":
    render_platform_sidebar_nav()
    st.markdown(f"""<div style='background:{theme_tokens['hero_gradient']};border:1px solid {theme_tokens['border']};border-radius:18px;padding:28px 32px;margin-bottom:22px;box-shadow:0 14px 28px {theme_tokens['accent_glow']};'>
            <div style='font-size:0.8rem;letter-spacing:0.1em;text-transform:uppercase;color:{theme_tokens['accent']};font-weight:700;'>{t('Get in touch', 'Neem contact op')}</div>
            <div style='font-size:2rem;font-weight:800;color:{theme_tokens['text']};margin-top:6px;line-height:1.25;'>Contact</div>
            <div style='font-size:1.05rem;color:{theme_tokens['muted']};max-width:820px;margin-top:10px;'>{t('Have questions, want to schedule a demo or need installation help? We typically respond within one business day.', 'Heb je vragen, wil je een demo plannen of hulp bij de installatie? We reageren normaal binnen één werkdag.')}</div>
        </div>""", unsafe_allow_html=True)

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
        st.link_button(
            t("Email customer service", "Mail klantenservice"),
            "mailto:support@smartfactorysuite.com",
            width="stretch",
        )
        st.link_button(
            t("Call customer service", "Bel klantenservice"),
            "tel:+31201234567",
            width="stretch",
        )
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
    st.markdown(f"""<div style="background:{theme_tokens['hero_gradient']};border:1px solid {theme_tokens['border']};border-radius:18px;padding:28px 32px;margin-bottom:22px;box-shadow:0 14px 28px {theme_tokens['accent_glow']};">
            <div style="font-size:0.8rem;letter-spacing:0.1em;text-transform:uppercase;color:{theme_tokens['accent']};font-weight:700;">{t('Frequently asked questions', 'Veelgestelde vragen')}</div>
            <div style="font-size:2rem;font-weight:800;color:{theme_tokens['text']};margin-top:6px;line-height:1.25;">FAQ</div>
            <div style="font-size:1.05rem;color:{theme_tokens['muted']};max-width:820px;margin-top:10px;">{t('Answers to the most common questions about setup, usage and subscriptions.', 'Antwoorden op de meest gestelde vragen over setup, gebruik en abonnementen.')}</div>
        </div>""", unsafe_allow_html=True)

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
    st.markdown(f"""
        <div style="background:{theme_tokens['hero_gradient_alt']};border:1px solid {theme_tokens['border']};border-radius:18px;padding:28px 32px;margin-bottom:22px;box-shadow:0 14px 28px {theme_tokens['accent_glow']};">
            <div style="font-size:0.8rem;letter-spacing:0.1em;text-transform:uppercase;color:{theme_tokens['accent']};font-weight:700;">{t('Help & support', 'Hulp & ondersteuning')}</div>
            <div style="font-size:2rem;font-weight:800;color:{theme_tokens['text']};margin-top:6px;line-height:1.25;">Support</div>
            <div style="font-size:1.05rem;color:{theme_tokens['muted']};max-width:820px;margin-top:10px;">{t('Everything you need to get going quickly or fix a problem.', 'Alles wat je nodig hebt om snel op weg te zijn of een probleem op te lossen.')}</div>
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
    if is_guest and acct_section not in {"inloggen", "account_maken", "support"}:
        acct_section = "inloggen"
        st.session_state.account_section = "inloggen"

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

    # ── nav sections definition ──
    if is_guest:
        _acct_sections = [
            ("inloggen",      "🔐 " + t("Login", "Inloggen")),
            ("account_maken", "🆕 " + t("Create account", "Account aanmaken")),
            ("support",       "🛠️ " + t("Support", "Support")),
        ]
    else:
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

        if acct_section == "inloggen":
            st.subheader("🔐 " + t("Login", "Inloggen"))
            login_user = st.text_input(t("Username", "Gebruikersnaam"), key="account_guest_login_user")
            login_pass = st.text_input(t("Password", "Wachtwoord"), type="password", key="account_guest_login_pass")
            if st.button(t("Login now", "Nu inloggen"), key="account_guest_login_btn", type="primary", width="stretch"):
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
                    st.success(t("Login successful.", "Inloggen gelukt."))
                    st.rerun()
                else:
                    st.error(t("Invalid username or password.", "Onjuiste gebruikersnaam of wachtwoord."))

        elif acct_section == "account_maken":
            st.subheader("🆕 " + t("Create account", "Account aanmaken"))
            reg_user = st.text_input(t("Username", "Gebruikersnaam"), key="account_guest_register_user")
            reg_pass = st.text_input(t("Password (min 6 chars)", "Wachtwoord (min 6 tekens)"), type="password", key="account_guest_register_pass")
            reg_name = st.text_input(t("Full name", "Volledige naam"), key="account_guest_register_name")
            reg_email = st.text_input(t("Email", "E-mail"), key="account_guest_register_email")
            reg_company = st.text_input(t("Company", "Bedrijf"), key="account_guest_register_company")
            if st.button(t("Create account", "Account aanmaken"), key="account_guest_register_btn", type="primary", width="stretch"):
                ok, message = register_user(reg_user, reg_pass, reg_name, reg_email, reg_company)
                if ok:
                    st.success(message)
                    st.session_state.account_section = "inloggen"
                    st.rerun()
                else:
                    st.error(message)

        # ─── 👤 Profiel ───────────────────────────────────────────────
        elif acct_section == "profiel":
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
                persist_active_user_state()
                st.toast(t("Profile saved.", "Profiel opgeslagen."), icon="✅")
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
                persist_active_user_state()
                st.toast(t("Settings saved.", "Instellingen opgeslagen."), icon="✅")
                st.rerun()
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
                    persist_active_user_state()
                    st.toast(t("Plan upgraded.", "Plan geupgrade."), icon="🚀")
                    st.rerun()
            with sub_col2:
                if st.button(t("Save plan", "Plan opslaan"), key="account_save_plan",
                             width="stretch"):
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
        st.subheader(t("Language, Theme & Simulation", "Taal, thema & simulatie"))

        if 'language' not in st.session_state:
            st.session_state.language = 'EN'
        if 'theme_preference' not in st.session_state:
            st.session_state.theme_preference = 'Dark'

        gen_col1, gen_col2, gen_col3 = st.columns(3)
        with gen_col1:
            lang = st.selectbox("Language / Taal", ['EN', 'NL'], index=0 if st.session_state.language == 'EN' else 1)
            if st.session_state.language != lang:
                st.session_state.language = lang
                persist_active_user_state()
                st.rerun()
        with gen_col2:
            selected_theme = st.selectbox(
                t("Theme", "Thema"),
                ["Dark", "Light"],
                index=0 if st.session_state.get("theme_preference", "Dark") == "Dark" else 1,
            )
            if st.session_state.get("theme_preference", "Dark") != selected_theme:
                st.session_state.theme_preference = selected_theme
                persist_active_user_state()
                st.rerun()
        with gen_col3:
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
            st.session_state.dashboard_visible_machines = list(range(1, new_machines + 1))
            st.session_state.dashboard_machine_order = list(range(1, new_machines + 1))
            st.success(t("Simulation updated.", "Simulatie bijgewerkt."))

        st.caption(t("Machine Names", "Machine namen"))
        for i in range(st.session_state.num_machines):
            st.session_state.machine_names[i] = st.text_input(
                f"Machine {i+1}",
                value=st.session_state.machine_names[i]
            )

        st.divider()
        st.caption(t("Advanced settings are grouped below for faster navigation.", "Geavanceerde instellingen zijn hieronder gegroepeerd voor sneller gebruik."))
        focus_section = st.selectbox(
            t("Focus section", "Focus-sectie"),
            [
                "All",
                t("Dashboard", "Dashboard"),
                t("Alerts", "Meldingen"),
                t("Theme / UI", "Thema / UI"),
                t("AI", "AI"),
                t("Data", "Data"),
                t("Machines", "Machines"),
                t("Region", "Regio"),
                t("Privacy", "Privacy"),
                t("Quick actions", "Quick actions"),
                t("Experience", "Ervaring"),
            ],
            key="settings_general_focus",
        )

        if focus_section in ["All", t("Dashboard", "Dashboard")]:
            with st.expander("📊 " + t("Dashboard customization", "Dashboard aanpassen"), expanded=True):
                machine_options = [
                    (
                        idx + 1,
                        f"M{idx + 1} — {st.session_state.machine_names[idx] if idx < len(st.session_state.machine_names) else f'Machine {idx+1}'}"
                    )
                    for idx in range(st.session_state.num_machines)
                ]
                option_map = {label: idx for idx, label in machine_options}
                default_visible_labels = [
                    label for idx, label in machine_options
                    if idx in set(get_ordered_visible_machine_indices(st.session_state.num_machines))
                ]
                selected_visible_labels = st.multiselect(
                    t("Visible machines", "Zichtbare machines"),
                    options=[label for _, label in machine_options],
                    default=default_visible_labels,
                    key="settings_visible_machine_labels",
                )
                ordered_labels = st.multiselect(
                    t("Machine order (select in desired order)", "Machinevolgorde (selecteer in gewenste volgorde)"),
                    options=[label for _, label in machine_options],
                    default=[label for label in selected_visible_labels if label in [opt for _, opt in machine_options]],
                    key="settings_machine_order_labels",
                )
                st.session_state.dashboard_visible_machines = [option_map[label] for label in selected_visible_labels if label in option_map]
                st.session_state.dashboard_machine_order = [option_map[label] for label in ordered_labels if label in option_map]
                dcol1, dcol2, dcol3 = st.columns(3)
                with dcol1:
                    st.session_state.dashboard_show_snapshot_chart = st.checkbox(t("Show machine snapshot", "Toon machine-snapshot"), value=bool(st.session_state.get("dashboard_show_snapshot_chart", True)), key="settings_show_snapshot")
                with dcol2:
                    st.session_state.dashboard_show_realtime_panel = st.checkbox(t("Show realtime panel", "Toon realtime panel"), value=bool(st.session_state.get("dashboard_show_realtime_panel", True)), key="settings_show_realtime")
                with dcol3:
                    st.session_state.dashboard_show_history_chart = st.checkbox(t("Show history chart", "Toon geschiedenisgrafiek"), value=bool(st.session_state.get("dashboard_show_history_chart", True)), key="settings_show_history_chart")

        if focus_section in ["All", t("Alerts", "Meldingen")]:
            with st.expander("🔔 " + t("Alert settings", "Meldingen instellen"), expanded=(focus_section != "All")):
                st.session_state.alert_threshold_watt = st.slider(
                    t("Alert threshold (W)", "Meldingsdrempel (W)"),
                    min_value=100,
                    max_value=6000,
                    value=int(st.session_state.get("alert_threshold_watt", 1000)),
                    step=50,
                    key="settings_alert_threshold_watt",
                )
                acol1, acol2 = st.columns(2)
                with acol1:
                    st.session_state.alert_type_fault = st.checkbox(t("Fault alerts", "Storingmeldingen"), value=bool(st.session_state.get("alert_type_fault", True)), key="settings_alert_type_fault")
                with acol2:
                    st.session_state.alert_type_maintenance = st.checkbox(t("Maintenance alerts", "Onderhoudsmeldingen"), value=bool(st.session_state.get("alert_type_maintenance", True)), key="settings_alert_type_maintenance")
                for i in range(1, st.session_state.num_machines + 1):
                    current_map = dict(st.session_state.get("alert_enabled_by_machine", {}))
                    machine_label = st.session_state.machine_names[i - 1] if i - 1 < len(st.session_state.machine_names) else f"Machine {i}"
                    current_map[str(i)] = st.checkbox(
                        t(f"Alerts for {machine_label}", f"Meldingen voor {machine_label}"),
                        value=bool(current_map.get(str(i), True)),
                        key=f"settings_alert_machine_{i}",
                    )
                    st.session_state.alert_enabled_by_machine = current_map

        if focus_section in ["All", t("Theme / UI", "Thema / UI")]:
            with st.expander("🎨 " + t("Theme / UI", "Thema / UI"), expanded=(focus_section != "All")):
                accent_color = st.color_picker(
                    t("Accent color", "Accentkleur"),
                    value=str(st.session_state.get("ui_accent_color", "#3b82f6"))
                )
                if accent_color != st.session_state.get("ui_accent_color"):
                    st.session_state.ui_accent_color = accent_color
                    persist_active_user_state()
                    st.rerun()
                
                ui_col1, ui_col2 = st.columns(2)
                with ui_col1:
                    density_choice = st.selectbox(
                        t("Density", "Dichtheid"),
                        ["Comfortable", "Compact"],
                        index=0 if st.session_state.get("ui_density", "Comfortable") == "Comfortable" else 1
                    )
                    if density_choice != st.session_state.get("ui_density"):
                        st.session_state.ui_density = density_choice
                        persist_active_user_state()
                        st.rerun()
                
                with ui_col2:
                    mobile_compact = st.checkbox(
                        t("Mobile compact mode", "Mobiele compacte modus"),
                        value=bool(st.session_state.get("ui_mobile_compact", False))
                    )
                    if mobile_compact != st.session_state.get("ui_mobile_compact"):
                        st.session_state.ui_mobile_compact = mobile_compact
                        persist_active_user_state()
                        st.rerun()

        if focus_section in ["All", t("AI", "AI")]:
            with st.expander("🤖 " + t("AI behavior", "AI gedrag"), expanded=(focus_section != "All")):
                ai_col1, ai_col2, ai_col3 = st.columns(3)
                with ai_col1:
                    st.session_state.ai_response_style = st.selectbox(t("Answer length", "Antwoordlengte"), ["Short", "Detailed"], index=1 if st.session_state.get("ai_response_style", "Detailed") == "Detailed" else 0, key="settings_ai_response_style")
                with ai_col2:
                    st.session_state.ai_technical_level = st.selectbox(t("Technical level", "Technisch niveau"), ["Simple", "Expert"], index=0 if st.session_state.get("ai_technical_level", "Simple") == "Simple" else 1, key="settings_ai_technical_level")
                with ai_col3:
                    st.session_state.ai_auto_advice = st.checkbox(t("Auto advice", "Automatisch advies"), value=bool(st.session_state.get("ai_auto_advice", True)), key="settings_ai_auto_advice")

        if focus_section in ["All", t("Data", "Data")]:
            with st.expander("📈 " + t("Data settings", "Data instellingen"), expanded=(focus_section != "All")):
                data_col1, data_col2, data_col3 = st.columns(3)
                with data_col1:
                    st.session_state.data_time_period = st.selectbox(t("Time period", "Tijdsperiode"), ["1h", "1d", "1w"], index=["1h", "1d", "1w"].index(st.session_state.get("data_time_period", "1h")), key="settings_data_time_period")
                with data_col2:
                    st.session_state.data_update_mode = st.selectbox(t("Update mode", "Update mode"), ["live", "per_minute"], index=0 if st.session_state.get("data_update_mode", "live") == "live" else 1, key="settings_data_update_mode")
                with data_col3:
                    st.session_state.data_unit = st.selectbox(t("Units", "Eenheden"), ["W", "kW"], index=0 if st.session_state.get("data_unit", "W") == "W" else 1, key="settings_data_unit")
                st.session_state.refresh_rate = 1 if st.session_state.get("data_update_mode") == "live" else 60

        if focus_section in ["All", t("Machines", "Machines")]:
            with st.expander("🏷️ " + t("Machine personalization", "Machines personaliseren"), expanded=(focus_section != "All")):
                machine_colors = dict(st.session_state.get("machine_colors", {}))
                machine_groups = dict(st.session_state.get("machine_groups", {}))
                for i in range(st.session_state.num_machines):
                    m_name = st.session_state.machine_names[i]
                    pcol1, pcol2 = st.columns([1, 1])
                    with pcol1:
                        machine_colors[m_name] = st.color_picker(t(f"Color {m_name}", f"Kleur {m_name}"), value=machine_colors.get(m_name, "#3b82f6"), key=f"settings_machine_color_{i}")
                    with pcol2:
                        machine_groups[m_name] = st.text_input(t(f"Group {m_name}", f"Groep {m_name}"), value=machine_groups.get(m_name, "Werkplaats"), key=f"settings_machine_group_{i}")
                st.session_state.machine_colors = machine_colors
                st.session_state.machine_groups = machine_groups

        if focus_section in ["All", t("Quick actions", "Quick actions")]:
            with st.expander("⚡ " + t("Quick actions", "Quick actions"), expanded=(focus_section != "All")):
                q1, q2, q3 = st.columns(3)
                with q1:
                    if st.button(t("Check everything", "Check alles"), key="settings_quick_check_all", width="stretch"):
                        st.session_state.page = "AI Insights"
                        st.session_state.ai_assistant_open = True
                        st.rerun()
                with q2:
                    if st.button(t("Reset filters", "Reset filters"), key="settings_quick_reset_filters", width="stretch"):
                        st.session_state.history_filter_type = ["All"]
                        st.session_state.history_sort = t("Newest First", "Nieuwste eerst")
                        st.rerun()
                with q3:
                    if st.button(t("Focus problems", "Focus op problemen"), key="settings_quick_focus_problems", width="stretch"):
                        st.session_state.page = "History"
                        st.session_state.history_filter_type = ["Anomaly", "Bottleneck"]
                        st.rerun()

        if focus_section in ["All", t("Region", "Regio")]:
            with st.expander("🌐 " + t("Language & region", "Taal & regio"), expanded=(focus_section != "All")):
                lr1, lr2 = st.columns(2)
                with lr1:
                    st.session_state.date_format = st.selectbox(t("Date format", "Datumformaat"), ["DD-MM-YYYY", "YYYY-MM-DD"], index=0 if st.session_state.get("date_format", "DD-MM-YYYY") == "DD-MM-YYYY" else 1, key="settings_date_format")
                with lr2:
                    st.session_state.timezone_name = st.selectbox(t("Timezone", "Tijdzone"), ["Europe/Amsterdam", "UTC"], index=0 if st.session_state.get("timezone_name", "Europe/Amsterdam") == "Europe/Amsterdam" else 1, key="settings_timezone")

        if focus_section in ["All", t("Privacy", "Privacy")]:
            with st.expander("🔒 " + t("Account / privacy", "Account / privacy"), expanded=(focus_section != "All")):
                pv1, pv2 = st.columns(2)
                with pv1:
                    st.session_state.privacy_data_sharing = st.checkbox(t("Allow data sharing", "Data delen toestaan"), value=bool(st.session_state.get("privacy_data_sharing", False)), key="settings_privacy_data_sharing")
                with pv2:
                    st.session_state.ai_history_enabled = st.checkbox(t("Save AI history", "AI-geschiedenis opslaan"), value=bool(st.session_state.get("ai_history_enabled", True)), key="settings_ai_history_enabled")
                export_payload = {
                    "timestamp": pd.Timestamp.now().isoformat(),
                    "mode": st.session_state.get("mode", "Simulation"),
                    "machine_names": st.session_state.get("machine_names", []),
                    "event_history": st.session_state.get("event_history", []),
                    "anomalies": st.session_state.get("anomalies", []),
                    "bottlenecks": st.session_state.get("bottlenecks", []),
                }
                st.download_button(
                    label=t("Export data (JSON)", "Exporteer data (JSON)"),
                    data=json.dumps(export_payload, ensure_ascii=False, indent=2),
                    file_name="machine_monitor_export.json",
                    mime="application/json",
                    key="settings_export_data",
                )

        if focus_section in ["All", t("Experience", "Ervaring")]:
            with st.expander("📱 " + t("Usage experience", "Gebruikservaring"), expanded=(focus_section != "All")):
                ux1, ux2, ux3 = st.columns(3)
                with ux1:
                    st.session_state.ui_animations_enabled = st.checkbox(t("Enable animations", "Animaties aan"), value=bool(st.session_state.get("ui_animations_enabled", True)), key="settings_ui_animations_enabled")
                with ux2:
                    st.session_state.ui_sidebar_default = st.selectbox(t("Sidebar default", "Sidebar standaard"), ["Open", "Closed"], index=0 if st.session_state.get("ui_sidebar_default", "Open") == "Open" else 1, key="settings_ui_sidebar_default")
                with ux3:
                    st.caption(t("Compact mode is optimized for mobile screens.", "Compacte modus is geoptimaliseerd voor mobiel."))

        st.session_state.animation_tick_ms = 300 if st.session_state.get("ui_animations_enabled", True) else 1200
        if not st.session_state.get("ai_history_enabled", True):
            st.session_state.ai_conversation_history = []

        if st.button(t("Save all settings", "Alle instellingen opslaan"), key="settings_save_all_extended", type="primary", width="stretch"):
            persist_active_user_state()
            st.toast(t("Settings saved.", "Instellingen opgeslagen."), icon="✅")
            st.rerun()
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
                    background: {theme_tokens['hero_gradient']};
                    border: 1px solid {theme_tokens['border']};
                    border-radius: 20px;
                    padding: 20px 24px;
                    margin-bottom: 18px;
                    display:flex;align-items:center;gap:18px;
                    box-shadow: 0 8px 24px {theme_tokens['accent_glow']}, inset 0 1px 0 rgba(148,163,184,0.08);
                ">
                    <div style="
                        width:52px;height:52px;border-radius:50%;flex-shrink:0;
                        background: linear-gradient(135deg, {theme_tokens['accent']} 0%, #22d3ee 100%);
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.25rem;font-weight:800;color:#fff;
                        box-shadow: 0 2px 12px {theme_tokens['accent_glow']};
                    ">{_initials}</div>
                    <div>
                        <div style="font-size:1.15rem;font-weight:700;color:{theme_tokens['text']};line-height:1.2;">
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
        <div style="background: linear-gradient(135deg, {theme_tokens['accent']}15, {theme_tokens['accent']}08); border: 2px solid {theme_tokens['accent']}; border-radius: 12px; padding: 24px; text-align: center; margin-bottom: 24px;">
            <div style="font-size: 3rem; margin-bottom: 12px;">🔨</div>
            <h2 style="color: {theme_tokens['text']}; margin: 12px 0;">{t('Coming Soon', 'Binnenkort beschikbaar')}</h2>
            <p style="color: {theme_tokens['muted']}; font-size: 1.05rem; margin: 8px 0;">
                {t('AI Insights is currently under construction and will be available in the next release.', 'AI Inzichten is momenteel in aanbouw en zal beschikbaar zijn in de volgende update.')}
            </p>
            <p style="color: {theme_tokens['subtle']}; font-size: 0.95rem; margin-top: 16px;">
                {t('Expected availability: Q3 2026', 'Verwachte beschikbaarheid: Q3 2026')}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.info(t("Please visit the Dashboard to monitor your machines.", "Bezoek het Dashboard om uw machines te controleren."))
    if st.button(t("Go to Dashboard", "Ga naar Dashboard"), type="primary", key="ai_to_dashboard"):
        st.session_state.page = "Dashboard"
        st.rerun()
    st.stop()

    if "ai_assistant_open" not in st.session_state:
        st.session_state.ai_assistant_open = True
    if "ai_assistant_result" not in st.session_state:
        st.session_state.ai_assistant_result = None
    if "ai_conversation_history" not in st.session_state:
        st.session_state.ai_conversation_history = []

    def run_ai_assistant_query(question_text):
        """Always return a usable assistant result, even if parsing fails."""
        try:
            conversation_history = st.session_state.get("ai_conversation_history", [])
            result = resolve_ai_assistant_result(question_text, conversation_history)
            if isinstance(result, dict) and result.get("message"):
                # Store in conversation history
                if bool(st.session_state.get("ai_history_enabled", True)):
                    st.session_state.ai_conversation_history.append({
                        "question": question_text,
                        "answer": result.get("message", ""),
                        "timestamp": pd.Timestamp.now().isoformat()
                    })
                return result
        except Exception:
            pass
        return {
            "message": t(
                "I could not process that question yet. Try: 'status machine 2', 'check all machines', or 'predict maintenance'.",
                "Ik kon die vraag nog niet verwerken. Probeer: 'status machine 2', 'check alle machines' of 'voorspel onderhoud'."
            ),
            "target_page": "Dashboard",
            "target_label": t("Open live dashboard", "Open live dashboard"),
            "target_state": {},
            "chart_machine": None,
        }

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

    st.markdown('<div class="page-section">', unsafe_allow_html=True)
    ai_top_col1, ai_top_col2 = st.columns([3, 1])
    with ai_top_col1:
        st.subheader(t("AI Assistant", "AI Assistent"))
        st.caption(t("Ask about machine status, anomalies, trend predictions, live connection, settings, or history.", "Vraag naar machinestatus, afwijkingen, trendvoorspellingen, live verbinding, instellingen of history."))
        st.caption(t(
            "Uses external AI when OPENAI_API_KEY is configured; otherwise local fallback logic is used.",
            "Gebruikt externe AI wanneer OPENAI_API_KEY is ingesteld; anders wordt lokale fallback-logica gebruikt."
        ))
    with ai_top_col2:
        if st.button(
            t("Open assistant", "Open assistent") if not st.session_state.ai_assistant_open else t("Hide assistant", "Verberg assistent"),
            key="ai_assistant_toggle",
            width="stretch",
            type="secondary",
        ):
            st.session_state.ai_assistant_open = not st.session_state.ai_assistant_open
            st.rerun()

    if st.session_state.ai_assistant_open:
        with st.form("ai_assistant_form", clear_on_submit=False):
            q = st.text_input(t("Ask your question", "Stel je vraag"), key="ai_assistant_question")
            ask_col1, ask_col2 = st.columns([1, 1])
            with ask_col1:
                submitted = st.form_submit_button(t("Get answer", "Krijg antwoord"), type="primary", use_container_width=True)
            with ask_col2:
                example_submit = st.form_submit_button(t("Examples", "Voorbeelden"), use_container_width=True)

        if submitted:
            st.session_state.ai_assistant_result = run_ai_assistant_query(q)
        if example_submit:
            st.session_state.ai_assistant_result = {
                "message": t(
                    "**Examples**\n- status machine 2\n- check all machines\n- why is usage higher\n- predict maintenance\n- history summary\n- live status",
                    "**Voorbeelden**\n- status machine 2\n- check alle machines\n- waarom is verbruik hoger\n- voorspel onderhoud\n- history samenvatting\n- live status"
                ),
                "target_page": None,
                "target_label": None,
                "target_state": {},
                "chart_machine": None,
            }

        quick_ai1, quick_ai2, quick_ai3, quick_ai4 = st.columns(4)
        with quick_ai1:
            if st.button(t("Check all machines", "Check alle machines"), key="ai_quick_all", width="stretch"):
                st.session_state.ai_assistant_result = run_ai_assistant_query("check all machines")
        with quick_ai2:
            if st.button(t("See alerts", "Zie storingen"), key="ai_quick_alerts", width="stretch"):
                st.session_state.ai_assistant_result = run_ai_assistant_query("anomalies and alerts")
        with quick_ai3:
            if st.button(t("Predict maintenance", "Voorspel onderhoud"), key="ai_quick_maintenance", width="stretch"):
                st.session_state.ai_assistant_result = run_ai_assistant_query("predict maintenance")
        with quick_ai4:
            if st.button(t("Live status", "Live status"), key="ai_quick_live", width="stretch"):
                st.session_state.ai_assistant_result = run_ai_assistant_query("live status")

        result = st.session_state.get("ai_assistant_result") or {}
        if result.get("message"):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(result.get("message", ""))
            target_page = result.get("target_page")
            target_label = result.get("target_label")
            if target_page and target_label:
                if st.button(target_label, key="ai_assistant_open_target", width="stretch", type="secondary"):
                    for state_key, state_value in dict(result.get("target_state") or {}).items():
                        st.session_state[state_key] = state_value
                    st.session_state.page = target_page
                    st.rerun()
            chart_machine = result.get("chart_machine")
            if chart_machine:
                render_ai_assistant_machine_chart(chart_machine, df)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display conversation history
        conversation_history = st.session_state.get("ai_conversation_history", [])
        if conversation_history and len(conversation_history) > 0:
            with st.expander(t("💬 Conversation History", "💬 Gespreksgeschiedenis"), expanded=False):
                for i, turn in enumerate(reversed(conversation_history[-10:]), 1):  # Show last 10
                    st.markdown(f"**Q{len(conversation_history)-i}:** {turn.get('question', '')}")
                    st.markdown(f"**A{len(conversation_history)-i}:** {turn.get('answer', '')}")
                    if i < len(conversation_history):
                        st.divider()
        
        # Button to clear conversation history
        if conversation_history and st.button(t("Clear conversation history", "Verwijder gespreksgeschiedenis"), key="ai_clear_history"):
            st.session_state.ai_conversation_history = []
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

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

        sparkline_points = [float(v) for v in series.tail(24).tolist()] if not series.empty else []
        incident_anchor_ts = None
        if "timestamp" in df.columns and len(df.index) > 0:
            try:
                incident_anchor_ts = pd.to_datetime(df["timestamp"].iloc[-1], errors="coerce")
                if not pd.isna(incident_anchor_ts):
                    incident_anchor_ts = incident_anchor_ts.isoformat()
                else:
                    incident_anchor_ts = None
            except Exception:
                incident_anchor_ts = None

        # Track anomalies and bottlenecks with cooldown so one issue doesn't spam history.
        machine_alert_flags = dict(st.session_state.get("alert_enabled_by_machine", {}))
        machine_alert_enabled = bool(machine_alert_flags.get(str(i), True))
        alert_threshold_watt = float(st.session_state.get("alert_threshold_watt", 1000))
        current_watt = float(cur) * 230.0
        avg_watt = float(avg) * 230.0

        if machine_alert_enabled and bool(st.session_state.get("alert_type_fault", True)) and (severity == "error" or anomaly_score > 2.5) and current_watt >= alert_threshold_watt:
            anomaly_msg = f"M{i}:{status}:{anomaly_score:.2f}"
            logged = log_event(
                "Anomaly",
                f"Machine {i} - {status} (Score: {anomaly_score:.2f})",
                dedupe_key=f"anomaly:M{i}:{status}",
                cooldown_s=120,
                meta={"machine": i, "sparkline_points": sparkline_points, "incident_anchor_ts": incident_anchor_ts},
            )
            if logged:
                st.session_state.anomalies.insert(0, anomaly_msg)
                st.session_state.anomalies = st.session_state.anomalies[:300]
        if machine_alert_enabled and bool(st.session_state.get("alert_type_maintenance", True)) and severity == "warning" and avg > 4 and avg_watt >= alert_threshold_watt:
            bottleneck_msg = f"M{i}:{avg:.2f}"
            logged = log_event(
                "Bottleneck",
                f"Machine {i} - High Load ({avg:.2f}A)",
                dedupe_key=f"bottleneck:M{i}",
                cooldown_s=180,
                meta={"machine": i, "sparkline_points": sparkline_points, "incident_anchor_ts": incident_anchor_ts},
            )
            if logged:
                st.session_state.bottlenecks.insert(0, bottleneck_msg)
                st.session_state.bottlenecks = st.session_state.bottlenecks[:300]


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

elif page == "Webshop":
    st.title(t("🛒 Webshop", "🛒 Webshop"))
    
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {theme_tokens['accent']}15, {theme_tokens['accent']}08); border: 2px solid {theme_tokens['accent']}; border-radius: 12px; padding: 24px; text-align: center; margin-bottom: 24px;">
            <div style="font-size: 3rem; margin-bottom: 12px;">🔨</div>
            <h2 style="color: {theme_tokens['text']}; margin: 12px 0;">{t('Coming Soon', 'Binnenkort beschikbaar')}</h2>
            <p style="color: {theme_tokens['muted']}; font-size: 1.05rem; margin: 8px 0;">
                {t('We are building an integrated webshop for hardware kits, licenses, and upgrades.', 'We bouwen een geïntegreerde webshop voor hardwarekits, licenties en upgrades.')}
            </p>
            <p style="color: {theme_tokens['subtle']}; font-size: 0.95rem; margin-top: 16px;">
                {t('Expected launch: Q3 2026', 'Verwachte lancering: Q3 2026')}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.info(t("Contact us for hardware and license inquiries.", "Neem contact met ons op voor vragen over hardware en licenties."))
    if st.button(t("Go to Dashboard", "Ga naar Dashboard"), type="primary", key="webshop_to_dashboard"):
        st.session_state.page = "Dashboard"
        st.rerun()
    st.stop()

elif page == "History":
    st.title(t("⚙ Event History", "⚙ Gebeurenissen Geschiedenis"))
    if "history_selected_event" not in st.session_state:
        st.session_state.history_selected_event = None

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
    fcol1, fcol2, fcol3, fcol4 = st.columns([2, 2, 2, 2])
    with fcol1:
        filter_type = st.multiselect(
            t("Filter by type", "Filter op type"),
            ["All", "Anomaly", "Bottleneck", "Connection", "System"],
            default=["All"],
            key="history_filter_type"
        )
    with fcol2:
        machine_options = [t("All machines", "Alle machines")] + [
            st.session_state.machine_names[i] if i < len(st.session_state.machine_names) else f"Machine {i+1}"
            for i in range(NUM_MACHINES)
        ]
        filter_machine = st.selectbox(t("Filter by machine", "Filter op machine"), machine_options, key="history_filter_machine")
    with fcol3:
        sort_option = st.selectbox(
            t("Sort", "Sorteren"),
            [t("Newest First", "Nieuwste eerst"), t("Oldest First", "Oudste eerst")],
            key="history_sort"
        )
    with fcol4:
        max_events = st.slider(t("Show events", "Toon gebeurtenissen"), 5, 100, 25, key="history_max")
    st.markdown('</div>', unsafe_allow_html=True)

    # Display events
    st.subheader(t("⌗ Event Log", "⌗ Gebeurtenissenlogboek"))

    if len(st.session_state.event_history) == 0:
        st.info(t("No events recorded yet", "Nog geen gebeurtenissen opgeslagen"))
    else:
        events_to_show = st.session_state.event_history.copy()
        if sort_option == t("Oldest First", "Oudste eerst"):
            events_to_show = events_to_show[::-1]

        if "All" not in filter_type:
            events_to_show = [e for e in events_to_show if e.get("type") in filter_type]

        # Machine filter
        selected_machine_label = filter_machine
        if selected_machine_label != t("All machines", "Alle machines"):
            # Match by machine index via machine_names
            try:
                machine_idx_filter = machine_options.index(selected_machine_label)  # 1-based after "All"
                events_to_show = [e for e in events_to_show if e.get("machine") == machine_idx_filter]
            except (ValueError, IndexError):
                pass

        total_filtered = len(events_to_show)
        events_to_show = events_to_show[:max_events]

        if total_filtered == 0:
            st.info(t("No events match the current filter.", "Geen gebeurtenissen komen overeen met het huidige filter."))
        else:
            # Summary bar
            shown = len(events_to_show)
            st.caption(
                t(f"Showing {shown} of {total_filtered} event(s)", f"{shown} van {total_filtered} gebeurtenis(sen) getoond")
            )

            # Compact event rows
            TYPE_COLORS = {
                "Anomaly":    "#ef4444",
                "Bottleneck": "#f97316",
                "Connection": "#10b981",
                "System":     "#6366f1",
            }
            TYPE_ICONS = {
                "Anomaly":    "⚠",
                "Bottleneck": "⬆",
                "Connection": "⦿",
                "System":     "ℹ",
            }

            current_date = None
            for idx, event in enumerate(events_to_show):
                event_type = event.get("type", "System")
                message = event.get("message", "")
                timestamp = event.get("timestamp", "")
                machine_label = event.get("machine")
                color = TYPE_COLORS.get(event_type, "#6366f1")
                icon = TYPE_ICONS.get(event_type, "•")

                ts_fmt = pd.to_datetime(timestamp, errors="coerce")
                if not pd.isna(ts_fmt):
                    try:
                        ts_fmt = ts_fmt.tz_localize("UTC").tz_convert(st.session_state.get("timezone_name", "Europe/Amsterdam"))
                    except Exception:
                        pass
                    if st.session_state.get("date_format", "DD-MM-YYYY") == "YYYY-MM-DD":
                        event_date_str = ts_fmt.strftime("%Y-%m-%d")
                    else:
                        event_date_str = ts_fmt.strftime("%d-%m-%Y")
                    time_part = ts_fmt.strftime("%H:%M:%S")
                else:
                    event_date_str = str(timestamp)[:10] if timestamp else ""
                    time_part = str(timestamp)[11:19] if len(str(timestamp)) >= 19 else str(timestamp)

                # Date separator
                event_date = event_date_str
                if event_date and event_date != current_date:
                    current_date = event_date
                    st.markdown(
                        f"<div style='margin:14px 0 4px 0; font-size:0.75rem; font-weight:600; "
                        f"color:#64748b; letter-spacing:0.06em; text-transform:uppercase;'>"
                        f"{'📅 ' + event_date}</div>",
                        unsafe_allow_html=True,
                    )

                machine_tag = (
                    f"<span style='font-size:0.72rem; background:{color}18; color:{color}; "
                    f"border:1px solid {color}55; border-radius:4px; padding:1px 6px; margin-right:6px;'>"
                    f"M{machine_label}</span>"
                    if machine_label is not None else ""
                )

                st.markdown(
                    f"""<div style='display:flex; align-items:center; gap:10px; padding:6px 10px;
                        border-left:3px solid {color}; border-radius:0 6px 6px 0;
                        background:{color}0d; margin-bottom:4px; flex-wrap:wrap;'>
                        <span style='font-size:0.78rem; font-weight:700; color:{color}; min-width:22px;'>{icon}</span>
                        <span style='font-size:0.72rem; color:#94a3b8; min-width:60px;'>{time_part}</span>
                        {machine_tag}
                        <span style='font-size:0.82rem; color:inherit; flex:1;'>{message}</span>
                    </div>""",
                    unsafe_allow_html=True,
                )

                if event_type in ["Anomaly", "Bottleneck"]:
                    if st.button(
                        t("View analysis", "Bekijk analyse"),
                        key=f"history_event_detail_{idx}_{timestamp}",
                        type="secondary",
                    ):
                        selected_event = dict(event)
                        detail_snapshot = build_incident_detail_snapshot(selected_event, st.session_state.get("df", pd.DataFrame()))
                        if detail_snapshot:
                            selected_event["detail_snapshot"] = detail_snapshot
                        st.session_state.history_selected_event = selected_event
                        st.rerun()

        selected_event = st.session_state.get("history_selected_event")
        if isinstance(selected_event, dict):
            sel_type = str(selected_event.get("type", "System"))
            sel_msg = str(selected_event.get("message", ""))
            sel_machine = selected_event.get("machine")
            sel_points = selected_event.get("sparkline_points", [])
            detail_snapshot = selected_event.get("detail_snapshot")

            st.markdown('<div class="history-section">', unsafe_allow_html=True)
            title_col, close_col = st.columns([5, 1])
            with title_col:
                st.subheader(t("⌬ Problem Analysis", "⌬ Probleemanalyse"))
            with close_col:
                if st.button(t("Close", "Sluiten"), key="history_close_detail", type="secondary", width="stretch"):
                    st.session_state.history_selected_event = None
                    st.rerun()

            machine_idx = None
            try:
                machine_idx = int(sel_machine) if sel_machine is not None else None
            except Exception:
                machine_idx = None

            fig_detail = go.Figure()
            has_series = False
            y_all = []

            if isinstance(detail_snapshot, dict) and detail_snapshot.get("x") and detail_snapshot.get("y"):
                snap_x = detail_snapshot["x"]
                snap_y = detail_snapshot["y"]
                incident_idx = int(detail_snapshot.get("incident_index", 0))
                chart_color = "#ef4444" if sel_type == "Anomaly" else "#f97316"
                machine_name = (
                    st.session_state.machine_names[machine_idx - 1]
                    if machine_idx and 0 < machine_idx <= len(st.session_state.machine_names)
                    else f"Machine {machine_idx}"
                )

                y_all = snap_y
                baseline_val = float(sum(snap_y) / max(len(snap_y), 1))

                # Fill under line
                fig_detail.add_trace(go.Scatter(
                    x=snap_x, y=snap_y,
                    mode="none",
                    fill="tozeroy",
                    fillcolor="rgba(239,68,68,0.09)" if sel_type == "Anomaly" else "rgba(249,115,22,0.09)",
                    showlegend=False,
                    hoverinfo="skip",
                ))

                # Main data line
                fig_detail.add_trace(go.Scatter(
                    x=snap_x, y=snap_y,
                    mode="lines+markers",
                    name=machine_name,
                    line=dict(width=2.5, color=chart_color),
                    marker=dict(size=4, color=chart_color),
                    hovertemplate="%{y:.2f} A<extra>" + machine_name + "</extra>",
                ))

                # Baseline / avg reference line
                fig_detail.add_hline(
                    y=baseline_val,
                    line=dict(dash="dash", color="#94a3b8", width=1.5),
                    annotation_text=t(f"Avg {baseline_val:.2f}A", f"Gem. {baseline_val:.2f}A"),
                    annotation_position="bottom right",
                    annotation_font=dict(size=11, color="#94a3b8"),
                )

                # Incident marker (diamond)
                if 0 <= incident_idx < len(snap_x):
                    inc_x = snap_x[incident_idx]
                    inc_y = snap_y[incident_idx]
                    fig_detail.add_trace(go.Scatter(
                        x=[inc_x], y=[inc_y],
                        mode="markers",
                        name=t("Problem moment", "Probleemmoment"),
                        marker=dict(size=16, color="#f59e0b", symbol="diamond",
                                    line=dict(width=2, color="#fff")),
                        hovertemplate=f"<b>{t('Incident', 'Incident')}</b><br>%{{y:.2f}} A<extra></extra>",
                    ))

                    # Vertical line at incident
                    fig_detail.add_vline(
                        x=inc_x,
                        line=dict(dash="dot", color="#f59e0b", width=1.5),
                        annotation_text=t("Incident", "Incident"),
                        annotation_position="top",
                        annotation_font=dict(size=11, color="#f59e0b"),
                    )

                has_series = True

            elif isinstance(sel_points, list) and len(sel_points) > 1:
                numeric_fb = [float(v) for v in sel_points if isinstance(v, (int, float))]
                x_fb = list(range(len(numeric_fb)))
                y_all = numeric_fb
                baseline_fb = sum(numeric_fb[:-1]) / max(len(numeric_fb) - 1, 1)
                inc_pos_fb = max(range(len(numeric_fb)), key=lambda i: abs(numeric_fb[i] - baseline_fb))
                fb_color = "#ef4444" if sel_type == "Anomaly" else "#f97316"

                fig_detail.add_trace(go.Scatter(
                    x=x_fb, y=numeric_fb,
                    mode="none", fill="tozeroy",
                    fillcolor="rgba(239,68,68,0.09)" if sel_type == "Anomaly" else "rgba(249,115,22,0.09)",
                    showlegend=False, hoverinfo="skip",
                ))
                fig_detail.add_trace(go.Scatter(
                    x=x_fb, y=numeric_fb,
                    mode="lines+markers",
                    name=t("Snapshot", "Momentopname"),
                    line=dict(width=2.5, color=fb_color),
                    marker=dict(size=4, color=fb_color),
                    hovertemplate="%{y:.2f} A<extra></extra>",
                ))
                fig_detail.add_hline(
                    y=baseline_fb,
                    line=dict(dash="dash", color="#94a3b8", width=1.5),
                    annotation_text=t(f"Avg {baseline_fb:.2f}A", f"Gem. {baseline_fb:.2f}A"),
                    annotation_position="bottom right",
                    annotation_font=dict(size=11, color="#94a3b8"),
                )
                fig_detail.add_trace(go.Scatter(
                    x=[x_fb[inc_pos_fb]], y=[numeric_fb[inc_pos_fb]],
                    mode="markers",
                    name=t("Problem moment", "Probleemmoment"),
                    marker=dict(size=16, color="#f59e0b", symbol="diamond",
                                line=dict(width=2, color="#fff")),
                    hovertemplate=f"<b>{t('Incident', 'Incident')}</b><br>%{{y:.2f}} A<extra></extra>",
                ))
                fig_detail.add_vline(
                    x=x_fb[inc_pos_fb],
                    line=dict(dash="dot", color="#f59e0b", width=1.5),
                    annotation_text=t("Incident", "Incident"),
                    annotation_position="top",
                    annotation_font=dict(size=11, color="#f59e0b"),
                )
                has_series = True

            if has_series:
                # Auto-scale Y with 20% headroom so the spike is visible
                if y_all:
                    y_min = max(0.0, min(y_all) - 0.3)
                    y_max = max(y_all) * 1.25
                else:
                    y_min, y_max = 0, 8

                fig_detail.update_layout(
                    template=plotly_template,
                    height=400,
                    margin=dict(l=10, r=10, t=36, b=10),
                    plot_bgcolor=plot_bg_color,
                    paper_bgcolor=plot_bg_color,
                    yaxis=dict(
                        title=dict(text=t("Current (A)", "Stroom (A)"), font=dict(size=12)),
                        range=[y_min, y_max],
                        gridcolor=plot_grid_color,
                        tickfont=dict(size=11),
                        zeroline=False,
                    ),
                    xaxis=dict(
                        title=dict(text=t("Time", "Tijd"), font=dict(size=12)),
                        gridcolor=plot_grid_color,
                        tickfont=dict(size=10),
                        tickangle=-30,
                    ),
                    showlegend=True,
                    legend=dict(
                        orientation="h", yanchor="bottom", y=1.02,
                        xanchor="left", x=0,
                        font=dict(size=11),
                        bgcolor=plot_legend_bg,
                        bordercolor=plot_legend_border,
                        borderwidth=1,
                    ),
                    hovermode="x unified",
                )
                st.plotly_chart(fig_detail, use_container_width=True, config={"displayModeBar": False, "displaylogo": False})
                st.caption(
                    t("◆ = problem moment  —  dashed line = average load before incident  —  window: 2 min before, 1 min after",
                      "◆ = probleemmoment  —  stippellijn = gemiddelde belasting vóór incident  —  venster: 2 min vóór, 1 min erna")
                )

            score_match = re.search(r"Score:\s*([0-9]+\.[0-9]+)", sel_msg)
            load_match = re.search(r"\(([0-9]+\.[0-9]+)A\)", sel_msg)
            score_text = score_match.group(1) if score_match else "-"
            load_text = load_match.group(1) if load_match else "-"

            if sel_type == "Anomaly":
                st.markdown(t(
                    f"**What happened:** Unexpected behavior was detected for machine M{machine_idx or '?'} (anomaly score: {score_text}).",
                    f"**Wat gebeurde er:** Onverwacht gedrag gedetecteerd voor machine M{machine_idx or '?'} (afwijkingsscore: {score_text})."
                ))
                st.markdown(t(
                    "**How to improve:**\n- Check sensor wiring and calibration\n- Inspect for abrupt load changes or mechanical friction\n- Compare with previous stable shift and tune alert thresholds",
                    "**Hoe verbeteren:**\n- Controleer sensorbekabeling en kalibratie\n- Inspecteer op plotselinge belasting of mechanische wrijving\n- Vergelijk met vorige stabiele shift en stel alarmdrempels bij"
                ))
            elif sel_type == "Bottleneck":
                st.markdown(t(
                    f"**What happened:** Sustained high load was detected for machine M{machine_idx or '?'} (avg load: {load_text}A).",
                    f"**Wat gebeurde er:** Aanhoudend hoge belasting gedetecteerd voor machine M{machine_idx or '?'} (gem. belasting: {load_text}A)."
                ))
                st.markdown(t(
                    "**How to improve:**\n- Redistribute work across parallel machines\n- Reduce cycle-time peaks with smoother feed rates\n- Plan preventive maintenance on bearings/cooling",
                    "**Hoe verbeteren:**\n- Verdeel werk over parallelle machines\n- Verminder cycluspiek met gelijkmatigere toevoersnelheid\n- Plan preventief onderhoud op lagers/koeling"
                ))

            st.caption(t("Source event", "Brongebeurtenis") + f": {sel_msg}")
            st.markdown('</div>', unsafe_allow_html=True)

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
        st.session_state.history_selected_event = None
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


# ============================================================================
# PAGE RENDERING FUNCTIONS
# ============================================================================

def render_top_nav():
    """Render top navigation and return current page."""
    return st.session_state.get("page", "Dashboard")

def render_dashboard_page():
    """Dashboard page is rendered inline in main application section."""
    pass

def render_factory_analysis_page():
    """Factory Analysis page is rendered inline in main application section."""
    pass

def render_history_page():
    """History page is rendered inline in main application section."""
    pass

def render_settings_page():
    """Settings page is rendered inline in main application section."""
    pass

def render_device_connection_page():
    """Device Connection page is rendered inline in main application section."""
    pass

def render_platform_page():
    """Platform page is rendered inline in main application section."""
    pass

def render_about_page():
    """About page is rendered inline in main application section."""
    pass

def render_contact_page():
    """Contact page is rendered inline in main application section."""
    pass

def render_faq_page():
    """FAQ page is rendered inline in main application section."""
    pass

def render_support_page():
    """Support page is rendered inline in main application section."""
    pass

def render_account_page():
    """Account page is rendered inline in main application section."""
    pass

# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'
if 'mode' not in st.session_state:
    st.session_state.mode = 'Simulation'
if 'num_machines' not in st.session_state:
    st.session_state.num_machines = 3
if 'connected_devices' not in st.session_state:
    st.session_state.connected_devices = []
if 'device_connected' not in st.session_state:
    st.session_state.device_connected = False

# Inject CSS
st.markdown(load_css(), unsafe_allow_html=True)

# Get current page
current_page = render_top_nav()
page = st.session_state.get("page", "Dashboard")

# Render based on page
if page == "Dashboard":
    render_dashboard_page()

elif page == "Factory Analysis":
    render_factory_analysis_page()

elif page == "AI Insights":
    st.info("🔨 AI Insights is under construction (Q2 2026)")

elif page == "History":
    render_history_page()

elif page == "Settings":
    render_settings_page()

elif page == "Device Connection":
    render_device_connection_page()

elif page == "Platform":
    render_platform_page()

elif page == "About":
    render_about_page()

elif page == "Contact":
    render_contact_page()

elif page == "FAQ":
    render_faq_page()

elif page == "Support":
    render_support_page()

elif page == "Account":
    render_account_page()

else:
    st.error(f"Unknown page: {page}")

# Platform navigation sidebar
render_platform_sidebar_nav()
