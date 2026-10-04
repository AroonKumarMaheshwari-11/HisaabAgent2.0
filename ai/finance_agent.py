"""
Finance Agent: narrow responsibility - revenue/expense/profit/margin insights.
Receives a pre-computed compact context (never raw DB access) and returns
plain-language insight text. Computes nothing itself.
"""

from ai.gemini_client import generate_text, GeminiError
from ai.prompts import build_finance_analysis_prompt


def analyze(context: dict) -> str:
    if context.get("revenue", 0) == 0 and context.get("expenses", 0) == 0:
        return ("Not enough financial activity recorded yet. Record a few "
                "sales or expenses to see finance insights here.")
    try:
        return generate_text(build_finance_analysis_prompt(context))
    except GeminiError as e:
        return f"Finance insights are temporarily unavailable: {e}"
