"""
Business Advisor: the final reasoning layer. Combines Finance, Inventory,
and Cash Flow agent outputs into a synthesized recommendation, a prioritized
action plan, or a direct answer to a free-text question.
"""

import re

from ai import finance_agent, inventory_agent, cashflow_agent
from ai.gemini_client import generate_text, GeminiError
from ai.prompts import build_advisor_prompt, build_action_plan_prompt, build_advisor_chat_prompt
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


def answer_question(user_question: str, period_key: str = "30d") -> str:
    context = build_full_business_context(period_key)
    try:
        return generate_text(build_advisor_chat_prompt(user_question, context))
    except GeminiError as e:
        return f"I couldn't process that just now: {e}"
