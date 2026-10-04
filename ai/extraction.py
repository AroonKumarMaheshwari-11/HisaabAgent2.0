"""
Natural language -> structured business data extraction.

This is the write-path entry point (Section 12). Flow:
  raw text -> Gemini (schema-constrained) -> Python validation ->
  services.transaction_service.build_preview() -> shown to user for
  confirmation -> only on explicit confirm does anything reach the DB.
"""

from ai.gemini_client import generate_json, GeminiError
from ai.prompts import build_extraction_prompt
from ai.schemas import EXTRACTION_SCHEMA
from utils.validators import (
    validate_sale_line, validate_purchase_line, validate_expense_line,
    validate_receivable_line, validate_payable_line, clean_int,
)


class ExtractionError(Exception):
    """User-facing extraction failure."""
    pass


def extract_activity(user_text: str) -> dict:
    """
    Returns a dict of the same shape as EXTRACTION_SCHEMA, but with every
    numeric field cleaned/coerced and every line that fails validation
    moved into `clarifications_needed` instead of silently passed through.
    """
    if not user_text or not user_text.strip():
        raise ExtractionError("Please describe what happened in your business first.")

    try:
        raw = generate_json(build_extraction_prompt(user_text), EXTRACTION_SCHEMA)
    except GeminiError as e:
        raise ExtractionError(str(e)) from e

    clarifications = list(raw.get("clarifications_needed") or [])

    cleaned = {"sales": [], "purchases": [], "expenses": [], "receivables": [],
               "payables": []}

    for line in raw.get("sales") or []:
        line = {
            "product_name": (line.get("product_name") or "").strip(),
            "quantity": clean_int(line.get("quantity")),
            "unit_price": clean_int(line.get("unit_price")),
            "cost_price": clean_int(line.get("cost_price")),
        }
        problems = validate_sale_line(line)
        if problems:
            clarifications.append(
                f"For the sale of '{line['product_name'] or 'an item'}': "
                f"{', '.join(problems)}."
            )
            continue
        cleaned["sales"].append(line)

    for line in raw.get("purchases") or []:
        line = {
            "product_name": (line.get("product_name") or "").strip(),
            "quantity": clean_int(line.get("quantity")),
            "cost_price": clean_int(line.get("cost_price")),
            "selling_price": clean_int(line.get("selling_price")),
        }
        problems = validate_purchase_line(line)
        if problems:
            clarifications.append(
                f"For the purchase of '{line['product_name'] or 'an item'}': "
                f"{', '.join(problems)}."
            )
            continue
        cleaned["purchases"].append(line)

    for line in raw.get("expenses") or []:
        line = {
            "category": (line.get("category") or "").strip(),
            "amount": clean_int(line.get("amount")),
            "notes": line.get("notes"),
        }
        problems = validate_expense_line(line)
        if problems:
            clarifications.append(f"For an expense entry: {', '.join(problems)}.")
            continue
        cleaned["expenses"].append(line)

    for line in raw.get("receivables") or []:
        line = {
            "customer_name": (line.get("customer_name") or "").strip(),
            "amount": clean_int(line.get("amount")),
            "due_date": line.get("due_date"),
            "notes": line.get("notes"),
        }
        problems = validate_receivable_line(line)
        if problems:
            clarifications.append(
                f"For the amount owed by '{line['customer_name'] or 'a customer'}': "
                f"{', '.join(problems)}."
            )
            continue
        cleaned["receivables"].append(line)

    for line in raw.get("payables") or []:
        line = {
            "supplier_name": (line.get("supplier_name") or "").strip(),
            "amount": clean_int(line.get("amount")),
            "due_date": line.get("due_date"),
            "notes": line.get("notes"),
        }
        problems = validate_payable_line(line)
        if problems:
            clarifications.append(
                f"For the amount owed to '{line['supplier_name'] or 'a supplier'}': "
                f"{', '.join(problems)}."
            )
            continue
        cleaned["payables"].append(line)

    cleaned["clarifications_needed"] = clarifications
    return cleaned
