"""
Transaction service: turns validated, extracted activity into database writes.

This is the ONLY module that commits AI-extracted data to the database, and
it never does so directly from raw Gemini output - callers must pass data
that has already gone through utils/validators.py and been shown to the
user for confirmation (see ai/extraction.py + app "Record Activity" page).

All arithmetic here calls services/calculations.py - nothing is computed
inline so there's exactly one place to audit for money math.
"""

from typing import Optional

from database import queries
from services.calculations import calculate_revenue, calculate_cogs
from utils.helpers import today_str


def build_preview(parsed: dict) -> dict:
    """
    Takes raw (but schema-shaped) extraction output and returns a preview
    dict with Python-computed totals, ready to render as a confirmation
    card. Never trusts any 'total_amount' Gemini may have included -
    recomputes everything from quantity/price.

    Also resolves whether referenced products already exist, so the
    preview can tell the user "new product will be created" vs "updating
    existing stock".
    """
    preview = {
        "sales": [],
        "purchases": [],
        "expenses": [],
        "receivables": [],
        "payables": [],
        "clarifications": list(parsed.get("clarifications_needed") or []),
    }

    for line in parsed.get("sales", []) or []:
        qty = line.get("quantity")
        price = line.get("unit_price")
        existing = queries.get_product_by_name(line.get("product_name", ""))
        revenue = calculate_revenue(qty, price)
        cost_price = line.get("cost_price")
        if cost_price is None and existing:
            cost_price = existing.get("cost_price")
        preview["sales"].append({
            "product_name": line.get("product_name"),
            "quantity": qty,
            "unit_price": price,
            "cost_price": cost_price,
            "total_amount": revenue,
            "product_exists": existing is not None,
            "current_stock": existing["quantity"] if existing else None,
            "stock_after": (existing["quantity"] - qty) if existing and qty else None,
            "insufficient_stock": bool(existing and qty and existing["quantity"] < qty),
        })

    for line in parsed.get("purchases", []) or []:
        qty = line.get("quantity")
        cost = line.get("cost_price")
        existing = queries.get_product_by_name(line.get("product_name", ""))
        preview["purchases"].append({
            "product_name": line.get("product_name"),
            "quantity": qty,
            "cost_price": cost,
            "selling_price": line.get("selling_price"),
            "total_amount": calculate_cogs(qty, cost),
            "product_exists": existing is not None,
            "current_stock": existing["quantity"] if existing else None,
        })

    for line in parsed.get("expenses", []) or []:
        preview["expenses"].append({
            "category": line.get("category"),
            "amount": line.get("amount"),
            "notes": line.get("notes"),
        })

    for line in parsed.get("receivables", []) or []:
        preview["receivables"].append({
            "customer_name": line.get("customer_name"),
            "amount": line.get("amount"),
            "due_date": line.get("due_date"),
            "notes": line.get("notes"),
        })

    for line in parsed.get("payables", []) or []:
        preview["payables"].append({
            "supplier_name": line.get("supplier_name"),
            "amount": line.get("amount"),
            "due_date": line.get("due_date"),
            "notes": line.get("notes"),
        })

    return preview


def _get_or_create_product(name: str, default_cost: Optional[int] = None,
                            default_selling: Optional[int] = None) -> dict:
    existing = queries.get_product_by_name(name)
    if existing:
        return existing
    new_id = queries.add_product(
        name=name,
        category=None,
        quantity=0,
        cost_price=default_cost or 0,
        selling_price=default_selling or 0,
    )
    return queries.get_product_by_id(new_id)


def commit_preview(preview: dict, date: Optional[str] = None) -> dict:
    """
    Writes a confirmed preview to the database. Returns a summary of what
    was created, for a success message / toast.
    """
    date = date or today_str()
    summary = {"sales": 0, "purchases": 0, "expenses": 0, "receivables": 0, "payables": 0}

    for line in preview.get("sales", []):
        qty = line.get("quantity")
        price = line.get("unit_price")
        if not qty or not price:
            continue
        product = _get_or_create_product(line["product_name"], default_selling=price)
        new_stock = max((product["quantity"] or 0) - qty, 0)
        queries.update_product_stock(product["id"], new_stock)
        revenue = calculate_revenue(qty, price)
        queries.insert_transaction(
            date=date, type_="sale", product_id=product["id"], quantity=qty,
            unit_price=price, cost_price=line.get("cost_price"),
            total_amount=revenue, source="ai_extracted",
            notes=f"Sold {qty} x {line['product_name']}",
        )
        summary["sales"] += 1

    for line in preview.get("purchases", []):
        qty = line.get("quantity")
        cost = line.get("cost_price")
        if not qty or not cost:
            continue
        product = _get_or_create_product(
            line["product_name"], default_cost=cost,
            default_selling=line.get("selling_price"),
        )
        new_stock = (product["quantity"] or 0) + qty
        queries.update_product_stock(product["id"], new_stock)
        # Keep cost price current if this purchase specifies one.
        queries.update_product(
            product["id"], product["name"], product.get("category"),
            cost_price=cost,
            selling_price=line.get("selling_price") or product.get("selling_price") or 0,
            low_stock_threshold=product.get("low_stock_threshold"),
        )
        total = calculate_cogs(qty, cost)
        queries.insert_transaction(
            date=date, type_="purchase", product_id=product["id"], quantity=qty,
            unit_price=line.get("selling_price"), cost_price=cost,
            total_amount=total, source="ai_extracted",
            notes=f"Purchased {qty} x {line['product_name']}",
        )
        summary["purchases"] += 1

    for line in preview.get("expenses", []):
        amount = line.get("amount")
        if not amount:
            continue
        queries.insert_transaction(
            date=date, type_="expense", total_amount=int(amount),
            expense_category=line.get("category") or "Other",
            notes=line.get("notes"), source="ai_extracted",
        )
        summary["expenses"] += 1

    for line in preview.get("receivables", []):
        amount = line.get("amount")
        if not amount:
            continue
        queries.add_receivable(
            customer_name=line["customer_name"], amount=int(amount),
            due_date=line.get("due_date"), notes=line.get("notes"),
        )
        summary["receivables"] += 1

    for line in preview.get("payables", []):
        amount = line.get("amount")
        if not amount:
            continue
        queries.add_payable(
            supplier_name=line["supplier_name"], amount=int(amount),
            due_date=line.get("due_date"), notes=line.get("notes"),
        )
        summary["payables"] += 1

    return summary


def record_manual_sale(product_id: int, quantity: int, unit_price: int,
                        cost_price: Optional[int], date: Optional[str] = None) -> None:
    """Used by the Inventory page's 'Record Sale' quick action (non-AI path)."""
    date = date or today_str()
    product = queries.get_product_by_id(product_id)
    if not product:
        return
    new_stock = max((product["quantity"] or 0) - quantity, 0)
    queries.update_product_stock(product_id, new_stock)
    revenue = calculate_revenue(quantity, unit_price)
    queries.insert_transaction(
        date=date, type_="sale", product_id=product_id, quantity=quantity,
        unit_price=unit_price, cost_price=cost_price or product.get("cost_price"),
        total_amount=revenue, source="manual",
    )


def record_manual_purchase(product_id: int, quantity: int, cost_price: int,
                            date: Optional[str] = None) -> None:
    """Used by the Inventory page's 'Record Purchase' quick action."""
    date = date or today_str()
    product = queries.get_product_by_id(product_id)
    if not product:
        return
    new_stock = (product["quantity"] or 0) + quantity
    queries.update_product_stock(product_id, new_stock)
    total = calculate_cogs(quantity, cost_price)
    queries.insert_transaction(
        date=date, type_="purchase", product_id=product_id, quantity=quantity,
        unit_price=product.get("selling_price"), cost_price=cost_price,
        total_amount=total, source="manual",
    )


def record_manual_expense(category: str, amount: int, notes: Optional[str] = None,
                           date: Optional[str] = None) -> None:
    date = date or today_str()
    queries.insert_transaction(
        date=date, type_="expense", total_amount=int(amount),
        expense_category=category, notes=notes, source="manual",
    )
