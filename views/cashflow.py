"""Cash Flow page: Udhaar/receivables, payables, cash flow visuals."""

import streamlit as st
import pandas as pd

from database import queries
from services.analytics_service import (
    get_receivables_summary, get_payables_summary, get_cash_flow_summary,
    get_daily_series,
)
from ui.components import kpi_card, section_header, empty_state
from ui.charts import receivables_vs_payables_bar, cash_flow_trend
from utils.helpers import format_currency, format_date_display, period_bounds, today_str


def render():
    section_header("\U0001F4B0 Cash Flow")

    start, end = period_bounds("30d")
    cash = get_cash_flow_summary(start, end)
    receivables = get_receivables_summary()
    payables = get_payables_summary()

    cols = st.columns(4)
    with cols[0]:
        kpi_card("Money In (30d)", cash["cash_in"])
    with cols[1]:
        kpi_card("Money Out (30d)", cash["cash_out"])
    with cols[2]:
        kpi_card("Net Cash Flow", cash["net_cash_flow"])
    with cols[3]:
        kpi_card("Outstanding Udhaar", receivables["total_outstanding"])

    st.markdown("")
    col_a, col_b = st.columns(2)
    with col_a:
        if receivables["total_outstanding"] or payables["total_outstanding"]:
            st.plotly_chart(
                receivables_vs_payables_bar(receivables["total_outstanding"],
                                             payables["total_outstanding"]),
                width="stretch",
            )
        else:
            st.info("No receivables or payables recorded yet.")
    with col_b:
        series = get_daily_series(start, end)
        if len(series["days"]) >= 2:
            st.plotly_chart(cash_flow_trend(series["days"], series["revenue"],
                                             series["expenses"]),
                             width="stretch")
        else:
            st.info("Not enough daily data yet for a cash flow trend.")

    st.markdown("---")
    tab1, tab2 = st.tabs(["\U0001F4B5 Udhaar / Money to Receive", "\U0001F3EA Supplier Payables"])

    with tab1:
        pending = receivables["pending_items"]
        if not pending:
            empty_state("No outstanding receivables.")
        else:
            rows = [{
                "Customer": r["customer_name"],
                "Amount": format_currency(r["amount"]),
                "Paid": format_currency(r["amount_paid"]),
                "Remaining": format_currency(r["remaining_amount"]),
                "Due Date": format_date_display(r["due_date"]) if r.get("due_date") else "\u2014",
                "Status": r["status"].capitalize(),
            } for r in pending]
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
            st.markdown(f"**Total Outstanding: {format_currency(receivables['total_outstanding'])}**")

        with st.expander("\u2795 Add Receivable / Record Payment"):
            sub1, sub2 = st.tabs(["Add New", "Record Payment"])
            with sub1:
                with st.form("add_receivable_form"):
                    name = st.text_input("Customer Name")
                    amount = st.number_input("Amount Owed", min_value=0, step=1)
                    due = st.date_input("Due Date (optional)", value=None)
                    if st.form_submit_button("Add Receivable", type="primary"):
                        if name.strip() and amount > 0:
                            queries.add_receivable(
                                name.strip(), int(amount),
                                due_date=str(due) if due else None,
                            )
                            st.success(f"Added receivable for {name}.")
                            st.rerun()
                        else:
                            st.error("Customer name and amount are required.")
            with sub2:
                if pending:
                    with st.form("pay_receivable_form"):
                        options = {f"{r['customer_name']} - {format_currency(r['remaining_amount'])}": r["id"]
                                   for r in pending}
                        chosen = st.selectbox("Select receivable", list(options.keys()))
                        payment = st.number_input("Payment Amount", min_value=1, step=1)
                        if st.form_submit_button("Record Payment", type="primary"):
                            queries.record_receivable_payment(options[chosen], int(payment))
                            st.success("Payment recorded.")
                            st.rerun()
                else:
                    st.info("No outstanding receivables to record payment against.")

    with tab2:
        pending_p = payables["pending_items"]
        if not pending_p:
            empty_state("No outstanding payables.")
        else:
            rows = [{
                "Supplier": p["supplier_name"],
                "Amount": format_currency(p["amount"]),
                "Paid": format_currency(p["amount_paid"]),
                "Remaining": format_currency(p["remaining_amount"]),
                "Due Date": format_date_display(p["due_date"]) if p.get("due_date") else "\u2014",
                "Status": p["status"].capitalize(),
            } for p in pending_p]
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
            st.markdown(f"**Total Outstanding: {format_currency(payables['total_outstanding'])}**")

        with st.expander("\u2795 Add Payable / Record Payment"):
            sub1, sub2 = st.tabs(["Add New", "Record Payment"])
            with sub1:
                with st.form("add_payable_form"):
                    name = st.text_input("Supplier Name")
                    amount = st.number_input("Amount Owed", min_value=0, step=1)
                    due = st.date_input("Due Date (optional)", value=None, key="payable_due")
                    if st.form_submit_button("Add Payable", type="primary"):
                        if name.strip() and amount > 0:
                            queries.add_payable(
                                name.strip(), int(amount),
                                due_date=str(due) if due else None,
                            )
                            st.success(f"Added payable to {name}.")
                            st.rerun()
                        else:
                            st.error("Supplier name and amount are required.")
            with sub2:
                if pending_p:
                    with st.form("pay_payable_form"):
                        options = {f"{p['supplier_name']} - {format_currency(p['remaining_amount'])}": p["id"]
                                   for p in pending_p}
                        chosen = st.selectbox("Select payable", list(options.keys()))
                        payment = st.number_input("Payment Amount", min_value=1, step=1,
                                                   key="payable_payment_amt")
                        if st.form_submit_button("Record Payment", type="primary"):
                            queries.record_payable_payment(options[chosen], int(payment))
                            st.success("Payment recorded.")
                            st.rerun()
                else:
                    st.info("No outstanding payables to record payment against.")
