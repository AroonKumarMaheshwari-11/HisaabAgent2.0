"""
Settings page.

Deliberately minimal: only fields whose value visibly changes app
behavior are here (business name feeds the Dashboard greeting; business
type feeds AI context; low-stock threshold feeds Inventory status logic).
Currency and language-preference fields were cut - see the scope review -
because currency is fixed to PKR and language is auto-detected by Gemini,
so a stored setting for either would have no effect and would be visibly
misleading against the "settings that do nothing" test.
"""

import streamlit as st

from database import queries
from demo.demo_data import load_demo_data, has_demo_data
from database.db import reset_db
from ai.gemini_client import is_configured
from ui.components import section_header, status_badge
from config import CURRENCY_SYMBOL, CURRENCY_CODE


def render():
    section_header("\u2699\uFE0F Settings")

    profile = queries.get_business_profile()

    with st.form("settings_form"):
        business_name = st.text_input("Business Name", value=profile.get("business_name", ""))
        business_type = st.text_input("Business Type", value=profile.get("business_type", ""))
        low_stock_threshold = st.number_input(
            "Default Low-Stock Threshold", min_value=1, step=1,
            value=profile.get("low_stock_threshold", 10),
            help="Products below this quantity are flagged as low stock, "
                 "unless they have their own custom threshold.",
        )
        st.text_input("Currency", value=f"{CURRENCY_CODE} ({CURRENCY_SYMBOL})", disabled=True)

        if st.form_submit_button("Save Settings", type="primary"):
            queries.update_business_profile(
                business_name.strip() or "My Business",
                business_type.strip() or "General Retail",
                int(low_stock_threshold),
            )
            st.success("Settings saved.")
            st.rerun()

    st.markdown("---")
    section_header("AI Status")
    if is_configured():
        status_badge("AI Online", "green")
    else:
        status_badge("AI Not Configured", "red")
        st.caption("Set the GEMINI_API_KEY environment variable, or add it to "
                   "Streamlit secrets, to enable AI features.")

    st.markdown("---")
    section_header("Demo Data")
    st.write("Load a realistic sample business (\"Ahmed Garments\") to explore "
             "every feature immediately.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("\U0001F4E5 Load Demo Business", type="primary", width="stretch"):
            load_demo_data()
            st.success("Demo data loaded! Head to the Dashboard to see it.")
            st.rerun()
    with col2:
        if st.button("\U0001F5D1\uFE0F Reset All Data", width="stretch"):
            st.session_state["confirm_reset"] = True

    if st.session_state.get("confirm_reset"):
        st.warning("This will permanently delete all products, transactions, "
                   "receivables, and payables. This cannot be undone.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, reset everything", type="primary"):
                reset_db()
                st.session_state["confirm_reset"] = False
                st.success("All data has been reset.")
                st.rerun()
        with c2:
            if st.button("Cancel"):
                st.session_state["confirm_reset"] = False
                st.rerun()
