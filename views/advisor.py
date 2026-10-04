"""AI Business Advisor page: synthesized summary + free-text Q&A."""

import streamlit as st

from database import queries
from ai.advisor_agent import synthesize_advisor_summary, answer_question
from ai.gemini_client import GeminiError
from ui.components import section_header, insight_card, loading_message, disclaimer, empty_state

SAMPLE_QUESTIONS = [
    "Mera business kaisa perform kar raha hai?",
    "Which product should I restock?",
    "Who owes me money?",
    "Where am I spending too much?",
]


def render():
    section_header("\U0001F916 AI Business Advisor")
    st.markdown("Ask anything about your business - HisaabAgent answers using your actual data.")

    if queries.count_transactions() == 0:
        empty_state("No business data yet. Record some activity first so the "
                     "Advisor has something to analyze.")
        return

    if st.button("\U0001F50E Analyze My Business", type="primary"):
        try:
            with loading_message("\U0001F9E0 HisaabAgent is analyzing Finance, "
                                  "Inventory, and Cash Flow..."):
                result = synthesize_advisor_summary("30d")
            st.session_state["advisor_summary"] = result
        except Exception:
            st.error("Something went wrong while analyzing your business. Please try again.")

    result = st.session_state.get("advisor_summary")
    if result:
        st.markdown("#### Summary")
        insight_card(result["summary"].replace("\n", "<br>"))

        with st.expander("See individual agent findings"):
            st.markdown("**Finance Agent**")
            st.write(result["finance"])
            st.markdown("**Inventory Agent**")
            st.write(result["inventory"])
            st.markdown("**Cash Flow Agent**")
            st.write(result["cash_flow"])

    st.markdown("---")
    st.markdown("#### Ask a question")

    cols = st.columns(len(SAMPLE_QUESTIONS))
    clicked_q = None
    for i, q in enumerate(SAMPLE_QUESTIONS):
        with cols[i]:
            if st.button(q, key=f"sample_q_{i}", width="stretch"):
                clicked_q = q

    question = st.text_input(
        "Your question",
        value=clicked_q or "",
        placeholder="Mere paas 50,000 rupees hain. Business mein kis cheez ko priority doon?",
        label_visibility="collapsed",
    )

    if st.button("Ask HisaabAgent", type="primary") and question.strip():
        try:
            with loading_message("\U0001F9E0 Thinking..."):
                answer = answer_question(question.strip(), "30d")
            insight_card(answer.replace("\n", "<br>"))
        except GeminiError as e:
            st.error(str(e))
        except Exception:
            st.error("Something went wrong while answering. Please try again.")

    st.markdown("")
    disclaimer()
