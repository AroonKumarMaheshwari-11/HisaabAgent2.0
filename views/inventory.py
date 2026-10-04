"""Inventory page: product table, add/update, quick sale/purchase, AI insights."""

import streamlit as st
import pandas as pd

from services.inventory_service import (
    get_products_with_status, add_new_product, update_existing_product,
)
from services.transaction_service import record_manual_sale, record_manual_purchase
from services.analytics_service import build_inventory_context
from ai.inventory_agent import analyze as analyze_inventory
from ai.gemini_client import GeminiError
from ui.components import section_header, kpi_card, empty_state, loading_message, insight_card
from utils.helpers import format_currency


def render():
    section_header("\U0001F4E6 Inventory")

    products = get_products_with_status()

    if not products:
        empty_state("No inventory data yet.")
    else:
        search = st.text_input("Search products", placeholder="Search by name or category...",
                                label_visibility="collapsed")
        filtered = [p for p in products if search.lower() in p["name"].lower()
                    or search.lower() in (p.get("category") or "").lower()] if search else products

        total_value = sum(p["inventory_value"] for p in products)
        low_count = len([p for p in products if p["status"] == "low"])

        cols = st.columns(3)
        with cols[0]:
            kpi_card("Total Products", len(products), is_currency=False)
        with cols[1]:
            kpi_card("Inventory Value", total_value)
        with cols[2]:
            kpi_card("Low Stock Items", low_count, is_currency=False)

        st.markdown("")
        df_rows = []
        for p in filtered:
            df_rows.append({
                "Product": p["name"],
                "Category": p.get("category") or "\u2014",
                "Stock": p["quantity"],
                "Cost Price": format_currency(p["cost_price"]),
                "Selling Price": format_currency(p["selling_price"]),
                "Inventory Value": format_currency(p["inventory_value"]),
                "Status": p["status_label"],
            })
        st.dataframe(pd.DataFrame(df_rows), width="stretch", hide_index=True)

        low_stock = [p for p in products if p["status"] == "low"]
        if low_stock:
            st.markdown("")
            section_header("\u26A0\uFE0F Low Stock")
            for p in low_stock:
                st.warning(f"**{p['name']}** - only {p['quantity']} units left "
                           f"(threshold: {p.get('low_stock_threshold') or 10})")

        st.markdown("")
        section_header("\U0001F9E0 Inventory AI Insights")
        try:
            with loading_message("Analyzing inventory..."):
                context = build_inventory_context()
                text = analyze_inventory(context)
            for line in [l.strip("-\u2022 ").strip() for l in text.split("\n") if l.strip()]:
                insight_card(line)
        except GeminiError as e:
            insight_card(f"Inventory insights unavailable: {e}")

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["\u2795 Add Product", "\U0001F4B5 Record Sale",
                                 "\U0001F4E5 Record Purchase"])

    with tab1:
        with st.form("add_product_form"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Product Name")
                category = st.text_input("Category")
                quantity = st.number_input("Starting Quantity", min_value=0, step=1)
            with c2:
                cost_price = st.number_input("Cost Price (per unit)", min_value=0, step=1)
                selling_price = st.number_input("Selling Price (per unit)", min_value=0, step=1)
                threshold = st.number_input("Low Stock Threshold", min_value=1, step=1, value=10)
            submitted = st.form_submit_button("Add Product", type="primary")
            if submitted:
                if not name.strip():
                    st.error("Product name is required.")
                else:
                    add_new_product(name.strip(), category.strip() or None, int(quantity),
                                     int(cost_price), int(selling_price), int(threshold))
                    st.success(f"Added {name}.")
                    st.rerun()

    with tab2:
        if not products:
            st.info("Add a product first.")
        else:
            with st.form("record_sale_form"):
                product_map = {p["name"]: p for p in products}
                chosen = st.selectbox("Product", list(product_map.keys()))
                qty = st.number_input("Quantity Sold", min_value=1, step=1)
                p = product_map[chosen]
                price = st.number_input("Selling Price (per unit)", min_value=0, step=1,
                                         value=p["selling_price"])
                submitted = st.form_submit_button("Record Sale", type="primary")
                if submitted:
                    record_manual_sale(p["id"], int(qty), int(price), p.get("cost_price"))
                    st.success(f"Recorded sale of {qty} x {chosen}.")
                    st.rerun()

    with tab3:
        if not products:
            st.info("Add a product first.")
        else:
            with st.form("record_purchase_form"):
                product_map = {p["name"]: p for p in products}
                chosen = st.selectbox("Product", list(product_map.keys()), key="purchase_product")
                qty = st.number_input("Quantity Purchased", min_value=1, step=1, key="purchase_qty")
                p = product_map[chosen]
                cost = st.number_input("Cost Price (per unit)", min_value=0, step=1,
                                        value=p["cost_price"], key="purchase_cost")
                submitted = st.form_submit_button("Record Purchase", type="primary")
                if submitted:
                    record_manual_purchase(p["id"], int(qty), int(cost))
                    st.success(f"Recorded purchase of {qty} x {chosen}.")
                    st.rerun()
