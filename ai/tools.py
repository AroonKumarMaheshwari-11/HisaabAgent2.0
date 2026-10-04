"""
Tools the Business Advisor agent can call.

Data tools are thin wrappers over services/analytics_service.py, so every
number comes from deterministic Python. Retrieval tools (RAG) return
passages from the knowledge base and from the business's own records.
Gemini only decides WHICH tool to call; it never calculates.
Docstrings matter: Gemini reads them to decide when to use each tool.
"""

from ai import rag
from services import analytics_service as svc
from utils.helpers import period_bounds

_VALID_PERIODS = ("today", "7d", "30d", "month")


def _bounds(period: str):
    try:
        return period_bounds(period)
    except Exception:
        return period_bounds("30d")


def get_financial_summary(period: str = "30d") -> dict:
    """Revenue, expenses, estimated profit and profit margin, plus % change
    versus the previous period. Use for questions about sales, profit or
    overall performance. period is one of: today, 7d, 30d, month."""
    return svc.build_finance_context(period if period in _VALID_PERIODS else "30d")


def get_top_products(period: str = "30d", limit: int = 5) -> list:
    """Best-selling products ranked by revenue, with quantity sold.
    Use for 'what sells most' or 'which product is best' questions."""
    start, end = _bounds(period)
    return svc.get_top_products(start, end, limit=max(1, min(limit, 10)))


def get_low_stock_products() -> dict:
    """Products that are running low on stock, plus total inventory value.
    Use for restocking, stock or inventory questions."""
    ctx = svc.build_inventory_context()
    return {
        "low_stock_products": ctx["low_stock_products"],
        "total_products": ctx["total_products"],
        "inventory_value": ctx["inventory_value"],
    }


def get_receivables() -> dict:
    """Udhaar: money customers still owe the business, per customer,
    with due dates. Use for questions about who owes money."""
    ctx = svc.build_cashflow_context("30d")
    return {"receivables": ctx["receivables"],
            "total_receivables": ctx["total_receivables"]}


def get_payables() -> dict:
    """Money the business still owes suppliers, per supplier, with due
    dates. Use for questions about what to pay and to whom."""
    ctx = svc.build_cashflow_context("30d")
    return {"payables": ctx["payables"],
            "total_payables": ctx["total_payables"]}


def get_cash_flow(period: str = "30d") -> dict:
    """Cash in, cash out and net cash flow for a period. period is one of:
    today, 7d, 30d, month."""
    return svc.build_cashflow_context(period if period in _VALID_PERIODS else "30d")


def get_expense_breakdown(period: str = "30d") -> list:
    """Expenses grouped by category for a period, largest first.
    Use for 'where is my money going' questions."""
    start, end = _bounds(period)
    return svc.get_expense_breakdown(start, end)


def get_health_score(period: str = "30d") -> dict:
    """Business Health Score (0-100) with financial, inventory, cash flow
    and sales performance sub-scores."""
    return svc.build_health_score_data(period if period in _VALID_PERIODS else "30d")


_SYNONYMS = {
    "receivable": "udhaar wapas", "receivables": "udhaar wapas",
    "credit": "udhaar", "recover": "wapas", "recovery": "wapas",
    "collect": "wapas", "owe": "udhaar", "debt": "udhaar",
    "stock": "restocking", "inventory": "restocking", "reorder": "restocking",
    "price": "pricing margin", "pricing": "margin", "profit": "margin",
    "cash": "cash flow", "expense": "expenses kharch", "expenses": "kharch",
    "supplier": "supplier payables", "eid": "seasonal ramzan",
    "ramzan": "seasonal eid", "season": "seasonal",
}


def search_knowledge_base(query: str) -> list:
    """Search the retail playbook for HOW-TO advice: recovering udhaar,
    restocking, pricing and margins, cash flow, supplier payments, cutting
    expenses, Eid/Ramzan stock. Use for 'what should I do / kaise karun'
    questions. Returns passages with titles; base advice only on them."""
    words = query.lower().split()
    expanded = query + " " + " ".join(_SYNONYMS.get(w.strip("?.,"), "") for w in words)
    hits = rag.search_knowledge(expanded, k=3)
    if hits:
        return [{"topic": h["title"], "passage": h["text"]} for h in hits]
    topics = [d["title"] for d in rag._load_knowledge()]
    return [{"topic": "none", "passage": "No match. Available topics: " + "; ".join(topics)}]



def search_business_records(query: str) -> list:
    """Search this business's own records (past sales, expenses, udhaar,
    payables) by customer, supplier, product or category name. Use for
    questions about a specific customer, product or past transaction,
    e.g. 'Ali ka udhaar' or 'shirts ki sales'."""
    hits = rag.search_records(query, k=5)
    return [{"type": h["kind"], "record": h["text"]} for h in hits] or [
        {"type": "none", "record": "No matching records found."}]


ADVISOR_TOOLS = [
    get_financial_summary, get_top_products, get_low_stock_products,
    get_receivables, get_payables, get_cash_flow,
    get_expense_breakdown, get_health_score,
    search_knowledge_base, search_business_records,
]