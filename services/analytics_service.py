"""
Aggregation queries and compact context-dict builders.

Two audiences use this module:
1. UI pages (Dashboard, Analytics, Cash Flow) - want fuller aggregates.
2. AI agents (ai/*.py) - want small, pre-computed context dicts per
   Section 53 of the brief: never send the whole database to Gemini.
"""

from collections import defaultdict
from typing import Optional

from database import queries
from services.calculations import (
    calculate_gross_profit, calculate_estimated_profit, calculate_profit_margin,
    calculate_percentage_change, calculate_inventory_value, calculate_net_cash_flow,
)
from services.inventory_service import get_products_with_status, get_low_stock_products
from utils.helpers import period_bounds, previous_period_bounds


def get_financial_summary(start_date: str, end_date: str) -> dict:
    txns = queries.get_transactions(start_date=start_date, end_date=end_date)
    revenue = sum(t["total_amount"] for t in txns if t["type"] == "sale")
    cogs = sum((t["quantity"] or 0) * (t["cost_price"] or 0)
               for t in txns if t["type"] == "sale" and t["cost_price"])
    expenses = sum(t["total_amount"] for t in txns if t["type"] == "expense")
    purchases = sum(t["total_amount"] for t in txns if t["type"] == "purchase")

    gross_profit = calculate_gross_profit(revenue, cogs)
    estimated_profit = calculate_estimated_profit(revenue, cogs, expenses)
    margin = calculate_profit_margin(estimated_profit, revenue)

    return {
        "revenue": revenue,
        "cogs": cogs,
        "expenses": expenses,
        "purchases": purchases,
        "gross_profit": gross_profit,
        "estimated_profit": estimated_profit,
        "profit_margin": margin,
        "transaction_count": len(txns),
    }


def get_period_comparison(period_key: str) -> dict:
    """Current period summary + % change vs the immediately preceding period."""
    start, end = period_bounds(period_key)
    prev_start, prev_end = previous_period_bounds(period_key)

    current = get_financial_summary(start, end)
    previous = get_financial_summary(prev_start, prev_end)

    has_previous_data = previous["transaction_count"] > 0

    return {
        "current": current,
        "previous": previous if has_previous_data else None,
        "revenue_change": calculate_percentage_change(
            current["revenue"], previous["revenue"] if has_previous_data else None),
        "expenses_change": calculate_percentage_change(
            current["expenses"], previous["expenses"] if has_previous_data else None),
        "profit_change": calculate_percentage_change(
            current["estimated_profit"], previous["estimated_profit"] if has_previous_data else None),
    }


def get_receivables_summary() -> dict:
    receivables = queries.get_receivables()
    pending = [r for r in receivables if r["status"] != "paid"]
    return {
        "items": receivables,
        "pending_items": pending,
        "total_outstanding": sum(r["remaining_amount"] for r in pending),
        "count_pending": len(pending),
    }


def get_payables_summary() -> dict:
    payables = queries.get_payables()
    pending = [p for p in payables if p["status"] != "paid"]
    return {
        "items": payables,
        "pending_items": pending,
        "total_outstanding": sum(p["remaining_amount"] for p in pending),
        "count_pending": len(pending),
    }


def get_cash_flow_summary(start_date: str, end_date: str) -> dict:
    txns = queries.get_transactions(start_date=start_date, end_date=end_date)
    cash_in = sum(t["total_amount"] for t in txns if t["type"] == "sale")
    cash_out = sum(t["total_amount"] for t in txns
                   if t["type"] in ("expense", "purchase"))
    net = calculate_net_cash_flow(cash_in, cash_out)
    receivables = get_receivables_summary()
    payables = get_payables_summary()
    return {
        "cash_in": cash_in,
        "cash_out": cash_out,
        "net_cash_flow": net,
        "total_receivables": receivables["total_outstanding"],
        "total_payables": payables["total_outstanding"],
    }


def get_top_products(start_date: str, end_date: str, limit: int = 5) -> list:
    txns = queries.get_transactions(start_date=start_date, end_date=end_date, type_="sale")
    by_product = defaultdict(lambda: {"quantity": 0, "revenue": 0})
    products_by_id = {p["id"]: p for p in queries.get_all_products()}
    for t in txns:
        pid = t.get("product_id")
        name = products_by_id.get(pid, {}).get("name", "Unknown") if pid else "Unknown"
        by_product[name]["quantity"] += t["quantity"] or 0
        by_product[name]["revenue"] += t["total_amount"] or 0
    ranked = sorted(by_product.items(), key=lambda kv: kv[1]["revenue"], reverse=True)
    return [{"product": k, **v} for k, v in ranked[:limit]]


def get_expense_breakdown(start_date: str, end_date: str) -> list:
    txns = queries.get_transactions(start_date=start_date, end_date=end_date, type_="expense")
    by_category = defaultdict(int)
    for t in txns:
        by_category[t.get("expense_category") or "Other"] += t["total_amount"]
    return [{"category": k, "amount": v} for k, v in
            sorted(by_category.items(), key=lambda kv: kv[1], reverse=True)]


def get_daily_series(start_date: str, end_date: str) -> dict:
    """Day-by-day revenue/expense series for line charts."""
    txns = queries.get_transactions(start_date=start_date, end_date=end_date)
    by_day = defaultdict(lambda: {"revenue": 0, "expenses": 0})
    for t in txns:
        day = t["date"][:10]
        if t["type"] == "sale":
            by_day[day]["revenue"] += t["total_amount"]
        elif t["type"] == "expense":
            by_day[day]["expenses"] += t["total_amount"]
    days = sorted(by_day.keys())
    return {
        "days": days,
        "revenue": [by_day[d]["revenue"] for d in days],
        "expenses": [by_day[d]["expenses"] for d in days],
    }


def get_inventory_value_total() -> int:
    return calculate_inventory_value(queries.get_all_products())


# ---------------------------------------------------------------------------
# Compact context builders for AI agents (Section 53) - small dicts only.
# ---------------------------------------------------------------------------

def build_finance_context(period_key: str = "30d") -> dict:
    comparison = get_period_comparison(period_key)
    return {
        "period": period_key,
        "revenue": comparison["current"]["revenue"],
        "expenses": comparison["current"]["expenses"],
        "estimated_profit": comparison["current"]["estimated_profit"],
        "profit_margin": comparison["current"]["profit_margin"],
        "revenue_change_pct": comparison["revenue_change"],
        "expenses_change_pct": comparison["expenses_change"],
        "profit_change_pct": comparison["profit_change"],
        "has_previous_period_data": comparison["previous"] is not None,
        "expense_breakdown": get_expense_breakdown(*period_bounds(period_key)),
    }


def build_inventory_context() -> dict:
    products = get_products_with_status()
    start, end = period_bounds("30d")
    top_products = get_top_products(start, end, limit=5)
    return {
        "total_products": len(products),
        "low_stock_products": [
            {"name": p["name"], "quantity": p["quantity"], "threshold":
                p.get("low_stock_threshold")}
            for p in products if p["status"] == "low"
        ],
        "top_selling_last_30d": top_products,
        "inventory_value": get_inventory_value_total(),
        "has_sufficient_sales_history": len(top_products) >= 1,
    }


def build_cashflow_context(period_key: str = "30d") -> dict:
    start, end = period_bounds(period_key)
    cash = get_cash_flow_summary(start, end)
    receivables = get_receivables_summary()
    payables = get_payables_summary()
    return {
        "period": period_key,
        "cash_in": cash["cash_in"],
        "cash_out": cash["cash_out"],
        "net_cash_flow": cash["net_cash_flow"],
        "receivables": [
            {"customer": r["customer_name"], "amount": r["remaining_amount"],
             "due_date": r.get("due_date")}
            for r in receivables["pending_items"]
        ],
        "payables": [
            {"supplier": p["supplier_name"], "amount": p["remaining_amount"],
             "due_date": p.get("due_date")}
            for p in payables["pending_items"]
        ],
        "total_receivables": receivables["total_outstanding"],
        "total_payables": payables["total_outstanding"],
    }


def build_health_score_data(period_key: str = "30d") -> dict:
    """
    Assembles every input the health_score module needs, then computes
    all four sub-scores and the overall score. Returns everything the
    Dashboard needs to render the score plus explain it.
    """
    from services.health_score import (
        score_financial_health, score_inventory_health, score_cash_flow_health,
        score_sales_performance, calculate_overall_health_score, get_health_band,
    )

    comparison = get_period_comparison(period_key)
    products = get_products_with_status()
    cash = get_cash_flow_summary(*period_bounds(period_key))
    receivables = get_receivables_summary()
    payables = get_payables_summary()

    financial = score_financial_health(
        comparison["current"]["revenue"], comparison["current"]["expenses"],
        comparison["current"]["estimated_profit"],
    )
    inventory = score_inventory_health(products)
    cash_flow = score_cash_flow_health(
        receivables["total_outstanding"], payables["total_outstanding"],
        cash["cash_in"], cash["cash_out"],
    )
    previous_revenue = comparison["previous"]["revenue"] if comparison["previous"] else None
    sales_performance = score_sales_performance(
        comparison["current"]["revenue"], previous_revenue,
    )

    sub_scores = {
        "financial": financial,
        "inventory": inventory,
        "cash_flow": cash_flow,
        "sales_performance": sales_performance,
    }
    overall = calculate_overall_health_score(sub_scores)
    label, color_key = get_health_band(overall)

    return {
        "overall": overall,
        "label": label,
        "color_key": color_key,
        "sub_scores": sub_scores,
    }


def build_full_business_context(period_key: str = "30d") -> dict:
    """Used by the Business Advisor - combines all three narrow contexts."""
    return {
        "finance": build_finance_context(period_key),
        "inventory": build_inventory_context(),
        "cash_flow": build_cashflow_context(period_key),
    }



    """Used by the Business Advisor - combines all three narrow contexts."""
    return {
        "finance": build_finance_context(period_key),
        "inventory": build_inventory_context(),
        "cash_flow": build_cashflow_context(period_key),
    }
