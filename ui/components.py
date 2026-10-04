"""
Reusable UI components, built as functions that render directly via
st.markdown. Keeping these in one place avoids duplicating HTML/CSS
snippets across every page module.
"""

import streamlit as st

from utils.helpers import format_currency, format_percentage
from config import COLORS


def kpi_card(label: str, value, is_currency: bool = True, delta=None,
             delta_label: str = "vs previous period"):
    """
    Renders one KPI card. `delta` should be a percentage number or None.
    When None, no comparison line is shown at all (Section 8: never fake
    a percentage change when there isn't enough data).
    """
    display_value = format_currency(value) if is_currency else str(value)

    delta_html = ""
    if delta is not None:
        arrow = "\u2191" if delta > 0 else ("\u2193" if delta < 0 else "\u2192")
        css_class = ("hisaab-kpi-delta-positive" if delta > 0
                     else "hisaab-kpi-delta-negative" if delta < 0
                     else "hisaab-kpi-delta-neutral")
        delta_html = (f'<div class="{css_class}">{arrow} {format_percentage(abs(delta))} '
                      f'<span style="color:{COLORS["text_muted"]};font-weight:400;">{delta_label}</span></div>')

    st.markdown(f"""
    <div class="hisaab-card">
        <div class="hisaab-kpi-label">{label}</div>
        <div class="hisaab-kpi-value">{display_value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def status_badge(label: str, color_key: str):
    st.markdown(
        f'<span class="hisaab-badge hisaab-badge-{color_key}">{label}</span>',
        unsafe_allow_html=True,
    )


def status_badge_html(label: str, color_key: str) -> str:
    """Non-rendering version, for embedding inside a larger markdown block."""
    return f'<span class="hisaab-badge hisaab-badge-{color_key}">{label}</span>'


def insight_card(text: str):
    st.markdown(f'<div class="hisaab-insight-card">{text}</div>', unsafe_allow_html=True)


def section_header(text: str):
    st.markdown(f'<div class="hisaab-section-header">{text}</div>', unsafe_allow_html=True)


def empty_state(message: str, action_label: str = None, action_key: str = None):
    st.markdown(f"""
    <div class="hisaab-empty-state">
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)
    if action_label and action_key:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            return st.button(action_label, key=action_key, width="stretch")
    return False


def loading_message(text: str = "\U0001F9E0 HisaabAgent is analyzing your business..."):
    return st.spinner(text)


def disclaimer():
    from config import DISCLAIMER_TEXT
    st.markdown(f'<div class="hisaab-disclaimer">{DISCLAIMER_TEXT}</div>',
                unsafe_allow_html=True)


def health_score_ring(score, label: str, color_key: str):
    """Renders the Business Health Score as a radial ring using inline SVG."""
    color_map = {
        "green": COLORS["accent_primary"],
        "amber": COLORS["accent_amber"],
        "red": COLORS["accent_red"],
        "muted": COLORS["text_muted"],
    }
    ring_color = color_map.get(color_key, COLORS["accent_gold"])
    display_score = f"{int(round(score))}" if score is not None else "\u2014"

    pct = (score or 0) / 100
    circumference = 2 * 3.14159 * 54
    offset = circumference * (1 - pct)

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:1.5rem;">
        <svg width="130" height="130" viewBox="0 0 130 130">
            <circle cx="65" cy="65" r="54" fill="none" stroke="{COLORS['border']}" stroke-width="10"/>
            <circle cx="65" cy="65" r="54" fill="none" stroke="{ring_color}" stroke-width="10"
                stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                stroke-linecap="round" transform="rotate(-90 65 65)"/>
            <text x="65" y="60" text-anchor="middle" font-size="30" font-weight="700"
                fill="{COLORS['text_primary']}" font-family="Inter, sans-serif">{display_score}</text>
            <text x="65" y="80" text-anchor="middle" font-size="12" fill="{COLORS['text_muted']}"
                font-family="Inter, sans-serif">/ 100</text>
        </svg>
        <div>
            <div style="font-size:0.85rem; color:{COLORS['text_muted']}; margin-bottom:0.3rem;">BUSINESS HEALTH</div>
            <div>{status_badge_html(label, color_key)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def action_card(priority: str, action: str, reason: str):
    priority_colors = {
        "high": "red", "medium": "amber", "attention": "amber", "low": "blue",
    }
    color_key = priority_colors.get(priority.strip().lower(), "blue")
    st.markdown(f"""
    <div class="hisaab-card" style="border-left: 3px solid {COLORS.get('accent_' + ('red' if color_key=='red' else 'amber' if color_key=='amber' else 'blue'))};">
        <div style="margin-bottom:0.4rem;">{status_badge_html(priority.upper(), color_key)}</div>
        <div style="font-weight:600; font-size:1.02rem; margin-bottom:0.25rem;">{action}</div>
        <div style="color:{COLORS['text_muted']}; font-size:0.88rem;">{reason}</div>
    </div>
    """, unsafe_allow_html=True)


def suggestion_chips(suggestions: list, key_prefix: str) -> str:
    """Renders clickable suggestion chips; returns the clicked suggestion text or None."""
    clicked = None
    cols = st.columns(len(suggestions))
    for i, s in enumerate(suggestions):
        with cols[i]:
            if st.button(s, key=f"{key_prefix}_{i}", width="stretch"):
                clicked = s
    return clicked


def stock_status_dot(color_key: str) -> str:
    dots = {"green": "\U0001F7E2", "amber": "\U0001F7E1", "red": "\U0001F534"}
    return dots.get(color_key, "\u26AA")
