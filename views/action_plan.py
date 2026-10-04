"""Today's Action Plan page: prioritized, reasoned recommendations."""

import streamlit as st

from database import queries
from ai.advisor_agent import generate_action_plan
from ui.components import section_header, action_card, loading_message, disclaimer, empty_state


def render():
    section_header("🎯 Today's Action Plan")
    st.markdown("A prioritized list of what to focus on, based on your actual business data.")

    if queries.count_transactions() == 0:
        empty_state("No business data yet. Record some activity first so "
                    "HisaabAgent can generate an action plan.")
    else:
        if st.button("🔄 Generate Today's Plan", type="primary") or \
                "action_plan" not in st.session_state:
            try:
                with loading_message("🧠 Building your action plan..."):
                    plan = generate_action_plan("30d")
                st.session_state["action_plan"] = plan
            except Exception:
                st.error("Something went wrong while building your action plan. Please try again.")
                st.session_state.setdefault("action_plan", [])

        plan = st.session_state.get("action_plan", [])
        if not plan:
            st.info("No action items to show yet.")
        else:
            priority_order = {"high": 0, "medium": 1, "attention": 1, "low": 2}
            plan_sorted = sorted(plan, key=lambda x: priority_order.get(
                x["priority"].strip().lower(), 3))
            for item in plan_sorted:
                action_card(item["priority"], item["action"], item["reason"])

    st.markdown("")
    disclaimer()

    # AI Transformation Roadmap Section
    st.markdown("---")
    section_header("🚀 AI Transformation Roadmap")
    st.markdown("Dekhein aapka business manual se AI-powered automated business mein kaise transform hota hai:")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1. Aaj Ka Manual Kaam")
        st.info("• Kaghaz par udhaar likhna\n• Stock khud ginte rehna\n• Bill haath se banana")
        
    with col2:
        st.subheader("2. HisaabAgent Automation")
        st.warning("• Auto Stock & Reorder Alerts\n• Udhaar Overdue Reminders\n• Smart Profit & Sales Analytics")
        
    with col3:
        st.subheader("3. Future Growth")
        st.success("• Zero Manual Errors\n• Time Saved Everyday\n• Smart Business Insights")