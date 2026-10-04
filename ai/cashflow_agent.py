"""
Cash Flow Agent: narrow responsibility - receivables, payables, cash pressure.
"""

from ai.gemini_client import generate_text, GeminiError
from ai.prompts import build_cashflow_analysis_prompt


def analyze(context: dict) -> str:
    if (context.get("cash_in", 0) == 0 and context.get("cash_out", 0) == 0
            and context.get("total_receivables", 0) == 0
            and context.get("total_payables", 0) == 0):
        return ("No cash flow activity recorded yet. Record sales, "
                "expenses, or udhaar to see cash flow insights here.")
    try:
        return generate_text(build_cashflow_analysis_prompt(context))
    except GeminiError as e:
        return f"Cash flow insights are temporarily unavailable: {e}"
