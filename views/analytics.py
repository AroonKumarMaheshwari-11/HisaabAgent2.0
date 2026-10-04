"""Analytics page: trends, top products, expense breakdown."""

import streamlit as st

from database import queries
from services.analytics_service import (
    get_financial_summary, get_daily_series, get_top_products, get_expense_breakdown,
)
from ui.components import kpi_card, section_header, empty_state
from ui.charts import revenue_expense_trend, top_products_bar, expense_breakdown_pie
from utils.helpers import period_bounds

PERIOD_OPTIONS = {"Today": "today", "Last 7 Days": "7d", "Last 30 Days": "30d",
                   "This Month": "month"}


def render():
    section_header("\U0001F4CA Analytics")

    if queries.count_transactions() == 0:
        empty_state("No data yet. Record your first transaction to see analytics here.")
        return

    period_label = st.radio("Period", list(PERIOD_OPTIONS.keys()), horizontal=True,
                             label_visibility="collapsed")
    period_key = PERIOD_OPTIONS[period_label]
    start, end = period_bounds(period_key)

    summary = get_financial_summary(start, end)

    cols = st.columns(4)
    with cols[0]:
        kpi_card("Revenue", summary["revenue"])
    with cols[1]:
        kpi_card("Expenses", summary["expenses"])
    with cols[2]:
        kpi_card("Estimated Profit", summary["estimated_profit"])
    with cols[3]:
        margin = summary["profit_margin"]
        kpi_card("Profit Margin", f"{margin}%" if margin is not None else "\u2014",
                  is_currency=False)

    st.markdown("")
    series = get_daily_series(start, end)
    if len(series["days"]) >= 2:
        st.plotly_chart(revenue_expense_trend(series["days"], series["revenue"],
                                               series["expenses"]),
                         width="stretch")
    else:
        st.info("Not enough daily data yet to plot a trend line for this period.")

    col_a, col_b = st.columns(2)
    with col_a:
        top_products = get_top_products(start, end, limit=5)
        if top_products:
            st.plotly_chart(top_products_bar(top_products), width="stretch")
        else:
            st.info("No sales in this period yet.")

    with col_b:
        breakdown = get_expense_breakdown(start, end)
        if breakdown:
            st.plotly_chart(expense_breakdown_pie(breakdown), width="stretch")
        else:
            st.info("No expenses recorded in this period yet.")
