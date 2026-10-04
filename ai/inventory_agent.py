"""
Inventory Agent: narrow responsibility - stock levels and sales velocity.
"""

from ai.gemini_client import generate_text, GeminiError
from ai.prompts import build_inventory_analysis_prompt


def analyze(context: dict) -> str:
    if context.get("total_products", 0) == 0:
        return ("No products recorded yet. Add products in the Inventory "
                "page to see stock insights here.")
    try:
        return generate_text(build_inventory_analysis_prompt(context))
    except GeminiError as e:
        return f"Inventory insights are temporarily unavailable: {e}"
