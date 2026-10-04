"""
HisaabAgent - main entry point.

This file is intentionally thin: it wires up the sidebar and routes to the
view modules in views/. All business logic and page content lives there.
"""

import streamlit as st

from config import APP_NAME, APP_TAGLINE
from database.db import init_db
from database import queries
from ui.styles import inject_global_styles
from ui.components import status_badge_html
from services.analytics_service import build_health_score_data
from ai.gemini_client import is_configured

from views import (
    dashboard, record_activity, analytics, inventory, cashflow, advisor,
    action_plan, settings,
)

st.set_page_config(
    page_title=APP_NAME,
    page_icon="\U0001F4B0",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
inject_global_styles()

NAV_ITEMS = [
    "\U0001F3E0 Dashboard",
    "\U0001F4DD Record Activity",
    "\U0001F4CA Analytics",
    "\U0001F4E6 Inventory",
    "\U0001F4B0 Cash Flow",
    "\U0001F916 AI Business Advisor",
    "\U0001F3AF Action Plan",
    "\u2699\uFE0F Settings",
]

PAGE_RENDERERS = {
    "\U0001F3E0 Dashboard": dashboard.render,
    "\U0001F4DD Record Activity": record_activity.render,
    "\U0001F4CA Analytics": analytics.render,
    "\U0001F4E6 Inventory": inventory.render,
    "\U0001F4B0 Cash Flow": cashflow.render,
    "\U0001F916 AI Business Advisor": advisor.render,
    "\U0001F3AF Action Plan": action_plan.render,
    "\u2699\uFE0F Settings": settings.render,
}

if "nav" not in st.session_state:
    st.session_state["nav"] = NAV_ITEMS[0]

# Apply any programmatic navigation request (e.g. from Dashboard's empty-state
# button) BEFORE the sidebar radio widget below is instantiated - Streamlit
# forbids writing to a widget's session_state key after that widget has
# already been created in the same script run.
if st.session_state.get("nav_override"):
    st.session_state["nav"] = st.session_state.pop("nav_override")

with st.sidebar:
    st.markdown(f"""
    <div class="hisaab-sidebar-logo">\U0001F4B0 {APP_NAME}</div>
    <div class="hisaab-sidebar-tagline">{APP_TAGLINE}</div>
    """, unsafe_allow_html=True)

    selected = st.radio(
        "Navigate", NAV_ITEMS,
        label_visibility="collapsed",
        key="nav",
    )

    st.markdown("---")

    profile = queries.get_business_profile()
    st.markdown(f"**{profile.get('business_name', 'My Business')}**")

    try:
        if queries.count_transactions() > 0:
            health = build_health_score_data("30d")
            label, color_key = health["label"], health["color_key"]
        else:
            label, color_key = "No data yet", "muted"
    except Exception:
        label, color_key = "No data yet", "muted"

    st.markdown(status_badge_html(label, color_key), unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if is_configured():
        st.markdown(status_badge_html("\u25CF AI Online", "green"), unsafe_allow_html=True)
    else:
        st.markdown(status_badge_html("\u25CF AI Not Configured", "red"), unsafe_allow_html=True)

PAGE_RENDERERS[st.session_state["nav"]]()
