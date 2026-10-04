"""
Record Activity page: natural language entry -> Gemini extraction ->
confirmation -> commit. This is the hackathon demo centerpiece (Section 58).
"""

import streamlit as st

from ai.extraction import extract_activity, ExtractionError
from services.transaction_service import build_preview, commit_preview
from ui.components import section_header, suggestion_chips, loading_message, disclaimer
from utils.helpers import format_currency, today_str

SUGGESTIONS = [
    "I sold 10 shirts for \u20a81,500 each",
    "Ali owes me \u20a85,000",
    "I paid my supplier \u20a812,000",
    "Bought 30 shirts for \u20a8900 each",
]


def _render_preview(preview: dict):
    st.markdown("#### Here's what I understood:")

    any_items = False

    for sale in preview["sales"]:
        any_items = True
        stock_note = ""
        if sale["product_exists"]:
            if sale["insufficient_stock"]:
                stock_note = (f" \u26A0\uFE0F Current stock is only "
                               f"{sale['current_stock']} - this will bring it below zero.")
            else:
                stock_note = f" (stock: {sale['current_stock']} \u2192 {sale['stock_after']})"
        else:
            stock_note = " (new product will be created)"
        st.markdown(f"""
        <div class="hisaab-card">
            <strong>\U0001F6CD\uFE0F Sale</strong><br>
            {sale['quantity']} \u00d7 {sale['product_name']}<br>
            {format_currency(sale['unit_price'])} each &nbsp;\u2192&nbsp;
            <strong>Total: {format_currency(sale['total_amount'])}</strong>
            <div style="color:#9FB8AC; font-size:0.82rem; margin-top:0.3rem;">{stock_note}</div>
        </div>
        """, unsafe_allow_html=True)

    for p in preview["purchases"]:
        any_items = True
        st.markdown(f"""
        <div class="hisaab-card">
            <strong>\U0001F4E6 Purchase</strong><br>
            {p['quantity']} \u00d7 {p['product_name']}<br>
            {format_currency(p['cost_price'])} each &nbsp;\u2192&nbsp;
            <strong>Total: {format_currency(p['total_amount'])}</strong>
        </div>
        """, unsafe_allow_html=True)

    for e in preview["expenses"]:
        any_items = True
        st.markdown(f"""
        <div class="hisaab-card">
            <strong>\U0001F4B8 Expense</strong> - {e['category']}<br>
            <strong>{format_currency(e['amount'])}</strong>
        </div>
        """, unsafe_allow_html=True)

    for r in preview["receivables"]:
        any_items = True
        st.markdown(f"""
        <div class="hisaab-card">
            <strong>\U0001F4B0 Receivable from {r['customer_name']}</strong><br>
            <strong>{format_currency(r['amount'])}</strong>
            {f" &middot; due {r['due_date']}" if r.get('due_date') else ""}
        </div>
        """, unsafe_allow_html=True)

    for p in preview["payables"]:
        any_items = True
        st.markdown(f"""
        <div class="hisaab-card">
            <strong>\U0001F3EA Payable to {p['supplier_name']}</strong><br>
            <strong>{format_currency(p['amount'])}</strong>
            {f" &middot; due {p['due_date']}" if p.get('due_date') else ""}
        </div>
        """, unsafe_allow_html=True)

    if preview["clarifications"]:
        st.markdown("##### \u2753 A few things I need clarified:")
        for c in preview["clarifications"]:
            st.warning(c)

    return any_items


def render():
    section_header("Tell HisaabAgent what happened.")
    st.markdown("You can write naturally in English or Roman Urdu.")

    clicked = suggestion_chips(SUGGESTIONS, key_prefix="chip")

    default_text = clicked if clicked else st.session_state.get("record_activity_text", "")

    user_text = st.text_area(
        "Business activity",
        value=default_text,
        placeholder="Aaj 20 shirts 1500 ki bechi, 5000 supplier ko diye aur Ali se 3000 lene hain.",
        height=110,
        label_visibility="collapsed",
        key="record_activity_input",
    )

    analyze_clicked = st.button("\U0001F50D Analyze Activity", type="primary")

    if analyze_clicked:
        if not user_text or not user_text.strip():
            st.warning("Please describe what happened first.")
        else:
            try:
                with loading_message("\U0001F9E0 HisaabAgent is reading your message..."):
                    extracted = extract_activity(user_text)
                    preview = build_preview(extracted)
                st.session_state["pending_preview"] = preview
            except ExtractionError as e:
                st.error(str(e))
            except Exception:
                st.error(
                    "Something went wrong while analyzing your business. Please try again."
                )

    preview = st.session_state.get("pending_preview")
    if preview:
        st.markdown("---")
        has_items = _render_preview(preview)

        if has_items:
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("\u2705 Confirm & Save", type="primary", width="stretch"):
                    try:
                        summary = commit_preview(preview, date=today_str())
                        st.session_state["pending_preview"] = None
                        st.session_state["record_activity_input"] = ""
                        total_saved = sum(summary.values())
                        st.success(
                            f"Saved successfully! Recorded {total_saved} item(s). "
                            f"Your Dashboard has been updated."
                        )
                    except Exception:
                        st.error(
                            "Something went wrong while saving. Please try again."
                        )
            with col2:
                if st.button("\u270F\uFE0F Edit", width="stretch"):
                    st.session_state["pending_preview"] = None
                    st.info("Edit your description above and click Analyze Activity again.")
        else:
            st.info("I couldn't confidently extract any activity. Please try rephrasing, "
                     "or answer the clarification above.")

    st.markdown("")
    disclaimer()
