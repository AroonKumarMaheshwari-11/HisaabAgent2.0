"""
Business Advisor: the final reasoning layer. Combines Finance, Inventory,
and Cash Flow agent outputs into a synthesized recommendation, a prioritized
action plan, or a direct answer to a free-text question.

Free-text questions are answered agentically: Gemini decides which tools to
call (data tools and RAG retrieval, see ai/tools.py), while every number
still comes from deterministic Python.
"""

import re

from ai import finance_agent, inventory_agent, cashflow_agent
from ai.gemini_client import generate_text, generate_with_tools, GeminiError
from ai.prompts import build_advisor_prompt, build_action_plan_prompt, build_advisor_chat_prompt
from ai.tools import ADVISOR_TOOLS
from services.analytics_service import build_full_business_context


def get_specialist_insights(period_key: str = "30d") -> dict:
    """Runs all three specialist agents once and returns their text output."""
    context = build_full_business_context(period_key)
    return {
        "finance": finance_agent.analyze(context["finance"]),
        "inventory": inventory_agent.analyze(context["inventory"]),
        "cash_flow": cashflow_agent.analyze(context["cash_flow"]),
        "context": context,
    }


def synthesize_advisor_summary(period_key: str = "30d") -> dict:
    insights = get_specialist_insights(period_key)
    try:
        summary = generate_text(build_advisor_prompt(
            insights["finance"], insights["inventory"], insights["cash_flow"],
            insights["context"],
        ))
    except GeminiError as e:
        summary = f"The Business Advisor is temporarily unavailable: {e}"
    return {**insights, "summary": summary}


def _parse_action_plan(raw_text: str) -> list:
    """Parses the PRIORITY/ACTION/REASON block format into structured items."""
    items = []
    blocks = re.split(r"\n\s*\n", raw_text.strip())
    for block in blocks:
        priority_match = re.search(r"PRIORITY:\s*(.+)", block, re.IGNORECASE)
        action_match = re.search(r"ACTION:\s*(.+)", block, re.IGNORECASE)
        reason_match = re.search(r"REASON:\s*(.+)", block, re.IGNORECASE)
        if action_match:
            items.append({
                "priority": (priority_match.group(1).strip() if priority_match else "Medium"),
                "action": action_match.group(1).strip(),
                "reason": (reason_match.group(1).strip() if reason_match else ""),
            })
    return items


def generate_action_plan(period_key: str = "30d") -> list:
    insights = get_specialist_insights(period_key)
    try:
        raw = generate_text(build_action_plan_prompt(
            insights["finance"], insights["inventory"], insights["cash_flow"],
            insights["context"],
        ))
    except GeminiError:
        return [{
            "priority": "Low",
            "action": "Record more business activity",
            "reason": "The AI service is temporarily unavailable.",
        }]
    parsed = _parse_action_plan(raw)
    if not parsed:
        return [{
            "priority": "Low",
            "action": "Record more business activity",
            "reason": "There isn't enough data yet to generate specific recommendations.",
        }]
    return parsed


AGENT_SYSTEM_PROMPT = (
    "You are HisaabAgent, a business advisor for a Pakistani micro-business. "
    "You have tools. Data tools return the business's real numbers; "
    "search_business_records finds specific customers, products or past "
    "transactions; search_knowledge_base returns retail best-practice "
    "passages. Call the tools you need; do not guess. For 'what should I do' "
    "questions, combine the business's numbers with advice from "
    "search_knowledge_base and name the topic you used. NEVER calculate or "
    "estimate numbers yourself: use only figures returned by tools and quote "
    "them exactly. If the tools return nothing relevant, say 'not enough "
    "data'. Reply in the same language as the user (English or Roman Urdu). "
    "Keep the answer short, practical and specific. Amounts are in PKR."
)


def answer_question(user_question: str, period_key: str = "30d") -> str:
    """Agentic answer: Gemini picks which tools to call. Falls back to the
    fixed-context prompt if tool calling fails."""
    try:
        text, tools_used = generate_with_tools(
            f"Default period: {period_key}.\nQuestion: {user_question}",
            tools=ADVISOR_TOOLS,
            system_instruction=AGENT_SYSTEM_PROMPT,
        )
        if text and tools_used:
            labels = ", ".join(t.replace("_", " ") for t in tools_used)
            return f"{text}\n\n*Data used: {labels}*"
        if text:
            return text
    except GeminiError:
        pass  # fall through to the fixed-context path below

    context = build_full_business_context(period_key)
    try:
        return generate_text(build_advisor_chat_prompt(user_question, context))
    except GeminiError as e:
        return f"I couldn't process that just now: {e}"