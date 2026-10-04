"""
Demo data: "Ahmed Garments", a small clothing shop.

Explicitly seeded across TWO distinct periods (a "previous week" and a
"this week") so the Sales Performance health sub-score always has a real
period-over-period comparison during a live demo, rather than falling
back to "insufficient data" - see the review of the health-score plan.
"""

from datetime import datetime, timedelta

from database.db import reset_db
from database import queries


def _date_days_ago(n: int) -> str:
    return (datetime.now() - timedelta(days=n)).strftime("%Y-%m-%d")


def load_demo_data() -> None:
    reset_db()

    queries.update_business_profile(
        business_name="Ahmed Garments",
        business_type="Clothing Retail",
        low_stock_threshold=10,
    )

    # --- Products -----------------------------------------------------
    shirt_id = queries.add_product("Shirts", "Apparel", quantity=8,
                                    cost_price=800, selling_price=1500,
                                    low_stock_threshold=10)
    jeans_id = queries.add_product("Jeans", "Apparel", quantity=40,
                                    cost_price=1200, selling_price=2200,
                                    low_stock_threshold=10)
    tshirt_id = queries.add_product("T-Shirts", "Apparel", quantity=35,
                                     cost_price=400, selling_price=900,
                                     low_stock_threshold=10)
    shoes_id = queries.add_product("Shoes", "Footwear", quantity=60,
                                    cost_price=1800, selling_price=3200,
                                    low_stock_threshold=10)

    # --- Previous period (35-45 days ago): falls inside the 31-60-day-ago
    # window that get_period_comparison('30d') uses as its comparison
    # baseline (see utils.helpers.previous_period_bounds). Moderate sales.
    prev_sales = [
        (44, shirt_id, 6, 1500, 800),
        (42, jeans_id, 3, 2200, 1200),
        (40, tshirt_id, 8, 900, 400),
        (38, shoes_id, 2, 3200, 1800),
        (36, shirt_id, 5, 1500, 800),
        (35, tshirt_id, 6, 900, 400),
    ]
    for days_ago, pid, qty, price, cost in prev_sales:
        queries.insert_transaction(
            date=_date_days_ago(days_ago), type_="sale", product_id=pid,
            quantity=qty, unit_price=price, cost_price=cost,
            total_amount=qty * price, source="manual",
            notes="Demo data - previous period",
        )

    queries.insert_transaction(
        date=_date_days_ago(38), type_="expense", total_amount=4500,
        expense_category="Electricity", source="manual",
        notes="Demo data",
    )
    queries.insert_transaction(
        date=_date_days_ago(36), type_="expense", total_amount=2000,
        expense_category="Transport", source="manual", notes="Demo data",
    )

    # --- Current period (last 1-14 days, inside the 0-30-day-ago window):
    # stronger sales, low shirt stock.
    current_sales = [
        (6, shirt_id, 10, 1500, 800),
        (5, jeans_id, 4, 2200, 1200),
        (5, tshirt_id, 12, 900, 400),
        (4, shirt_id, 8, 1500, 800),
        (3, shoes_id, 1, 3200, 1800),
        (2, tshirt_id, 10, 900, 400),
        (1, shirt_id, 4, 1500, 800),
        (0, jeans_id, 2, 2200, 1200),
    ]
    for days_ago, pid, qty, price, cost in current_sales:
        queries.insert_transaction(
            date=_date_days_ago(days_ago), type_="sale", product_id=pid,
            quantity=qty, unit_price=price, cost_price=cost,
            total_amount=qty * price, source="manual",
            notes="Demo data - current period",
        )

    # Bring shirt stock down to a realistic low-stock number after sales.
    queries.update_product_stock(shirt_id, 6)

    queries.insert_transaction(
        date=_date_days_ago(5), type_="expense", total_amount=5200,
        expense_category="Electricity", source="manual", notes="Demo data",
    )
    queries.insert_transaction(
        date=_date_days_ago(3), type_="expense", total_amount=2500,
        expense_category="Transport", source="manual", notes="Demo data",
    )
    queries.insert_transaction(
        date=_date_days_ago(2), type_="expense", total_amount=1500,
        expense_category="Packaging", source="manual", notes="Demo data",
    )

    # A stock purchase (restocking jeans)
    queries.insert_transaction(
        date=_date_days_ago(4), type_="purchase", product_id=jeans_id,
        quantity=15, cost_price=1200, total_amount=15 * 1200,
        source="manual", notes="Demo data - restock",
    )
    queries.update_product_stock(jeans_id, 40 + 15 - 4 - 2)

    # --- Receivables (Udhaar) ------------------------------------------
    queries.add_receivable("Ali", 5000, due_date=_date_days_ago(-7),
                            notes="Demo data - promised next week")
    queries.add_receivable("Ahmed", 3500, due_date=_date_days_ago(-3),
                            notes="Demo data")

    # --- Payables --------------------------------------------------------
    queries.add_payable("ABC Traders", 15000, due_date=_date_days_ago(-5),
                         notes="Demo data - fabric supplier")


def has_demo_data() -> bool:
    products = queries.get_all_products()
    profile = queries.get_business_profile()
    return len(products) > 0 and profile.get("business_name") == "Ahmed Garments"
