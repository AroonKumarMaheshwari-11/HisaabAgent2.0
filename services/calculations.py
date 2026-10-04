"""
Pure financial calculation functions.

Every function here is deterministic and side-effect free: given the same
inputs, always the same output. Gemini never performs any of this math —
these are the only functions in the codebase allowed to compute money.
"""

from typing import Optional


def calculate_revenue(quantity: int, selling_price: int) -> int:
    """Revenue = quantity x selling price. Guards against negative inputs."""
    if quantity is None or selling_price is None:
        return 0
    if quantity < 0 or selling_price < 0:
        return 0
    return int(quantity) * int(selling_price)


def calculate_cogs(quantity: int, cost_price: Optional[int]) -> int:
    """Cost of goods sold. Returns 0 if cost price is unknown (not None-crash)."""
    if quantity is None or cost_price is None:
        return 0
    if quantity < 0 or cost_price < 0:
        return 0
    return int(quantity) * int(cost_price)


def calculate_gross_profit(revenue: int, cogs: int) -> int:
    return (revenue or 0) - (cogs or 0)


def calculate_estimated_profit(revenue: int, cogs: int, operating_expenses: int) -> int:
    return (revenue or 0) - (cogs or 0) - (operating_expenses or 0)


def calculate_profit_margin(profit: int, revenue: int) -> Optional[float]:
    """Returns None (not 0, not a crash) when revenue is 0 - margin is undefined."""
    if not revenue:
        return None
    return round((profit / revenue) * 100, 1)


def calculate_percentage_change(current: float, previous: float) -> Optional[float]:
    """
    Returns None when there's no valid previous-period baseline to compare
    against - callers must render an empty state, not a fabricated 0%.
    """
    if previous in (None, 0):
        return None
    return round(((current - previous) / previous) * 100, 1)


def calculate_inventory_value(products: list) -> int:
    """Total value of on-hand stock, valued at cost price."""
    total = 0
    for p in products:
        qty = p.get("quantity") or 0
        cost = p.get("cost_price") or 0
        if qty > 0 and cost > 0:
            total += qty * cost
    return total


def calculate_net_cash_flow(cash_in: int, cash_out: int) -> int:
    return (cash_in or 0) - (cash_out or 0)


def safe_divide(numerator: float, denominator: float) -> Optional[float]:
    if not denominator:
        return None
    return numerator / denominator
