"""Dashboard page: the "how is my business doing?" landing view."""

from datetime import datetime

import streamlit as st

from database import queries
from services.analytics_service import (
    get_period_comparison, build_health_score_data, get_inventory_value_total,
    get_receivables_summary, get_payables_summary,
)
from services.inventory_service import get_low_stock_products
from ai.advisor_agent import get_specialist_insights
from ai.gemini_client import GeminiError
from ui.components import (
    kpi_card, section_header, health_score_ring, insight_card, empty_state,
    loading_message, disclaimer,
)
from utils.helpers import format_currency


def render():
    profile = queries.get_business_profile()
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")

    st.markdown(f"### {greeting} \U0001F44B")
    st.markdown(
        f"Here's how **{profile.get('business_name', 'your business')}** is performing."
    )

    if queries.count_transactions() == 0:
        empty_state(
            "No activity recorded yet. Record your first transaction to "
            "start seeing business insights.",
        )
        st.markdown("")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("\U0001F4DD Record Activity", width="stretch"):
                st.session_state["nav_override"] = "\U0001F4DD Record Activity"
                st.rerun()
        return

    comparison = get_period_comparison("30d")
    current = comparison["current"]
    receivables = get_receivables_summary()
    payables = get_payables_summary()
    inventory_value = get_inventory_value_total()

    section_header("Key Metrics (Last 30 Days)")
    row1 = st.columns(3)
    with row1[0]:
        kpi_card("Revenue", current["revenue"], delta=comparison["revenue_change"])
    with row1[1]:
        kpi_card("Expenses", current["expenses"], delta=comparison["expenses_change"])
    with row1[2]:
        kpi_card("Estimated Profit", current["estimated_profit"], delta=comparison["profit_change"])

    row2 = st.columns(3)
    with row2[0]:
        kpi_card("Receivables (Udhaar)", receivables["total_outstanding"])
    with row2[1]:
        kpi_card("Payables", payables["total_outstanding"])
    with row2[2]:
        kpi_card("Inventory Value", inventory_value)

    st.markdown("")
    col_score, col_gap, col_insights = st.columns([1.1, 0.05, 1.85])

    with col_score:
        section_header("Business Health")
        health = build_health_score_data("30d")
        health_score_ring(health["overall"], health["label"], health["color_key"])

        st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
        sub_labels = {
            "financial": "Financial Health",
            "inventory": "Inventory Health",
            "cash_flow": "Cash Flow",
            "sales_performance": "Sales Performance",
        }
        for key, label in sub_labels.items():
            val = health["sub_scores"].get(key)
            val_display = f"{int(round(val))}/100" if val is not None else "No data yet"
            st.markdown(
                f"<div style='display:flex; justify-content:space-between; "
                f"padding:0.25rem 0; font-size:0.88rem;'>"
                f"<span style='color:{('#9FB8AC')};'>{label}</span>"
                f"<span style='font-weight:600;'>{val_display}</span></div>",
                unsafe_allow_html=True,
            )

    with col_insights:
        section_header("\U0001F9E0 AI Business Insights")
        try:
            with loading_message("\U0001F9E0 HisaabAgent is analyzing your business..."):
                insights = get_specialist_insights("30d")
            for block_name, text in [("Finance", insights["finance"]),
                                      ("Inventory", insights["inventory"]),
                                      ("Cash Flow", insights["cash_flow"])]:
                for line in [l.strip("-\u2022 ").strip() for l in text.split("\n") if l.strip()]:
                    insight_card(line)
        except GeminiError as e:
            insight_card(f"AI insights unavailable right now: {e}")
        except Exception:
            insight_card(
                "Something went wrong while generating insights. Please try again."
            )

    low_stock = get_low_stock_products()
    if low_stock:
        st.markdown("")
        section_header("\u26A0\uFE0F Needs Attention")
        for p in low_stock[:3]:
            insight_card(
                f"\U0001F4E6 <strong>{p['name']}</strong> is running low "
                f"({p['quantity']} units left)."
            )

    st.markdown("")
    disclaimer()
