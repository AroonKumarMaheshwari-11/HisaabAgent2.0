"""
Inventory business rules: stock status classification, low-stock detection.
"""

from database import queries
from config import DEFAULT_LOW_STOCK_THRESHOLD


def get_stock_status(product: dict) -> str:
    """Returns 'healthy' | 'monitor' | 'low' based on quantity vs threshold."""
    threshold = product.get("low_stock_threshold") or DEFAULT_LOW_STOCK_THRESHOLD
    qty = product.get("quantity") or 0
    if qty <= 0:
        return "low"
    if qty <= threshold:
        return "low"
    if qty <= threshold * 2:
        return "monitor"
    return "healthy"


STATUS_LABELS = {
    "healthy": ("\U0001F7E2 Healthy", "green"),
    "monitor": ("\U0001F7E1 Monitor", "amber"),
    "low": ("\U0001F534 Low Stock", "red"),
}


def get_products_with_status() -> list:
    products = queries.get_all_products()
    for p in products:
        status = get_stock_status(p)
        p["status"] = status
        p["status_label"], p["status_color"] = STATUS_LABELS[status]
        p["inventory_value"] = (p.get("quantity") or 0) * (p.get("cost_price") or 0)
    return products


def get_low_stock_products() -> list:
    return [p for p in get_products_with_status() if p["status"] == "low"]


def add_new_product(name: str, category: str, quantity: int, cost_price: int,
                     selling_price: int, low_stock_threshold: int = None) -> int:
    return queries.add_product(
        name=name, category=category, quantity=quantity, cost_price=cost_price,
        selling_price=selling_price, low_stock_threshold=low_stock_threshold,
    )


def update_existing_product(product_id: int, name: str, category: str,
                             cost_price: int, selling_price: int,
                             low_stock_threshold: int = None) -> None:
    queries.update_product(product_id, name, category, cost_price, selling_price,
                            low_stock_threshold)
