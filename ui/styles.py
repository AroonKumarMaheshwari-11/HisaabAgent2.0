"""
Centralized CSS for HisaabAgent2.0's light green fintech theme.
Single injection point - no CSS scattered across page files.
"""

import streamlit as st

from config import COLORS


def inject_global_styles() -> None:
    c = COLORS
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, sans-serif;
    }}

    /* ---- App background ---- */
    .stApp {{
        background-color: {c['bg_panel']};
        color: {c['text_primary']};
    }}

    /* ---- Sidebar: always open, even if browser remembered "collapsed" ---- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {c['bg_deep']} 0%, {c['bg_deep_end']} 100%);
        border-right: 1px solid {c['border']};
        min-width: 270px !important;
        width: 270px !important;
    }}
    section[data-testid="stSidebar"][aria-expanded="false"] {{
        transform: none !important;
        margin-left: 0 !important;
        display: block !important;
        visibility: visible !important;
        min-width: 270px !important;
        width: 270px !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {c['text_primary']};
    }}

    /* Hide collapse/expand buttons since sidebar is always open */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stExpandSidebarButton"] {{
        display: none !important;
    }}

    /* ---- Sidebar navigation items ---- */
    section[data-testid="stSidebar"] [role="radiogroup"] label {{
        padding: 0.45rem 0.7rem;
        border-radius: 8px;
        transition: background-color 0.15s ease;
    }}
    section[data-testid="stSidebar"] [role="radiogroup"] label:hover {{
        background-color: rgba(27, 127, 79, 0.10);
    }}
    section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{
        background-color: rgba(27, 127, 79, 0.16);
        font-weight: 600;
    }}

    /* ---- Headings ---- */
    h1, h2, h3 {{
        color: {c['text_primary']};
        font-weight: 700;
        letter-spacing: -0.01em;
    }}

    p, span, label, li {{
        color: {c['text_primary']};
    }}

    /* ---- Hide default Streamlit chrome ---- */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{background: transparent;}}

    /* ---- Buttons ---- */
    .stButton > button {{
        background-color: {c['accent_primary']};
        color: {c['on_accent']};
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.25rem;
        transition: background-color 0.15s ease;
    }}
    .stButton > button p {{
        color: {c['on_accent']};
    }}
    .stButton > button:hover {{
        background-color: {c['accent_hover']};
        color: {c['on_accent']};
    }}
    .stButton > button[kind="secondary"] {{
        background-color: {c['bg_card']};
        border: 1px solid {c['border']};
        color: {c['text_primary']};
    }}
    .stButton > button[kind="secondary"] p {{
        color: {c['text_primary']};
    }}
    .stButton > button[kind="secondary"]:hover {{
        background-color: {c['bg_deep']};
        border-color: {c['accent_primary']};
    }}

    /* ---- Inputs ---- */
    .stTextInput input, .stTextArea textarea, .stNumberInput input,
    .stSelectbox [data-baseweb="select"] > div, .stDateInput input {{
        background-color: {c['bg_card']} !important;
        color: {c['text_primary']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 8px !important;
    }}

    /* ---- Dataframes / tables ---- */
    [data-testid="stDataFrame"] {{
        border: 1px solid {c['border']};
        border-radius: 10px;
        overflow: hidden;
    }}

    /* ---- Custom component classes ---- */
    .hisaab-card {{
        background-color: {c['bg_card']};
        border: 1px solid {c['border']};
        border-radius: 12px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 1px 3px rgba(20, 40, 31, 0.06);
    }}

    .hisaab-kpi-label {{
        color: {c['text_muted']};
        font-size: 0.82rem;
        font-weight: 500;
        text-transform: none;
        margin-bottom: 0.35rem;
    }}

    .hisaab-kpi-value {{
        color: {c['text_primary']};
        font-size: 1.9rem;
        font-weight: 700;
        line-height: 1.1;
    }}

    .hisaab-kpi-delta-positive {{
        color: {c['accent_primary']};
        font-size: 0.85rem;
        font-weight: 600;
    }}
    .hisaab-kpi-delta-negative {{
        color: {c['accent_red']};
        font-size: 0.85rem;
        font-weight: 600;
    }}
    .hisaab-kpi-delta-neutral {{
        color: {c['text_muted']};
        font-size: 0.85rem;
        font-weight: 500;
    }}

    .hisaab-badge {{
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
    }}
    .hisaab-badge-green {{ background-color: rgba(27,127,79,0.12); color: {c['accent_primary']}; }}
    .hisaab-badge-amber {{ background-color: rgba(184,110,0,0.14); color: {c['accent_amber']}; }}
    .hisaab-badge-red {{ background-color: rgba(201,60,50,0.12); color: {c['accent_red']}; }}
    .hisaab-badge-blue {{ background-color: rgba(37,99,176,0.12); color: {c['accent_blue']}; }}
    .hisaab-badge-muted {{ background-color: rgba(83,102,91,0.12); color: {c['text_muted']}; }}

    .hisaab-insight-card {{
        background-color: {c['bg_card']};
        border: 1px solid {c['border']};
        border-left: 4px solid {c['accent_primary']};
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.7rem;
        font-size: 0.93rem;
        line-height: 1.5;
        box-shadow: 0 1px 3px rgba(20, 40, 31, 0.05);
    }}

    .hisaab-section-header {{
        font-size: 1.15rem;
        font-weight: 700;
        margin: 1.4rem 0 0.7rem 0;
        color: {c['text_primary']};
    }}

    .hisaab-sidebar-logo {{
        font-size: 1.35rem;
        font-weight: 800;
        color: {c['text_primary']};
        margin-bottom: 0.1rem;
    }}
    .hisaab-sidebar-tagline {{
        font-size: 0.76rem;
        color: {c['text_muted']};
        margin-bottom: 1.1rem;
        line-height: 1.3;
    }}

    .hisaab-empty-state {{
        text-align: center;
        padding: 2.5rem 1rem;
        color: {c['text_muted']};
    }}

    .hisaab-disclaimer {{
        font-size: 0.76rem;
        color: {c['text_muted']};
        font-style: italic;
        margin-top: 0.5rem;
    }}

    .hisaab-chip {{
        display: inline-block;
        background-color: {c['bg_card']};
        border: 1px solid {c['border']};
        border-radius: 999px;
        padding: 0.3rem 0.85rem;
        font-size: 0.82rem;
        color: {c['text_primary']};
        margin: 0.2rem 0.3rem 0.2rem 0;
    }}
    </style>
    """, unsafe_allow_html=True)