"""
Validation for structured data coming out of Gemini extraction.

Gemini's response_schema constrains the JSON *shape*, but not semantic
validity (e.g. it could still return quantity: -5, or a string where a
number belongs). Every one of these checks runs before any value reaches
services/transaction_service.py.
"""

from typing import Any, Optional


def is_positive_number(value: Any) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def is_non_negative_number(value: Any) -> bool:
    try:
        return float(value) >= 0
    except (TypeError, ValueError):
        return False


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and len(value.strip()) > 0


def clean_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    """Coerce to a non-negative int, or return default if impossible."""
    try:
        n = int(round(float(value)))
        return n if n >= 0 else default
    except (TypeError, ValueError):
        return default


def validate_sale_line(line: dict) -> list:
    """Returns a list of problem strings; empty list means valid."""
    problems = []
    if not is_non_empty_string(line.get("product_name")):
        problems.append("missing product name")
    if not is_positive_number(line.get("quantity")):
        problems.append("missing or invalid quantity")
    if not is_positive_number(line.get("unit_price")):
        problems.append("missing or invalid selling price")
    return problems


def validate_purchase_line(line: dict) -> list:
    problems = []
    if not is_non_empty_string(line.get("product_name")):
        problems.append("missing product name")
    if not is_positive_number(line.get("quantity")):
        problems.append("missing or invalid quantity")
    if not is_positive_number(line.get("cost_price")):
        problems.append("missing or invalid cost price")
    return problems


def validate_expense_line(line: dict) -> list:
    problems = []
    if not is_positive_number(line.get("amount")):
        problems.append("missing or invalid amount")
    if not is_non_empty_string(line.get("category")):
        problems.append("missing expense category")
    return problems


def validate_receivable_line(line: dict) -> list:
    problems = []
    if not is_non_empty_string(line.get("customer_name")):
        problems.append("missing customer name")
    if not is_positive_number(line.get("amount")):
        problems.append("missing or invalid amount")
    return problems


def validate_payable_line(line: dict) -> list:
    problems = []
    if not is_non_empty_string(line.get("supplier_name")):
        problems.append("missing supplier name")
    if not is_positive_number(line.get("amount")):
        problems.append("missing or invalid amount")
    return problems
