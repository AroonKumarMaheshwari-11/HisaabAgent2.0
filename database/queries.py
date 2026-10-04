"""
All raw SQL lives here, as parameterized, single-purpose functions.
Nothing above this layer (services/, ai/) writes SQL directly.
"""

from datetime import datetime
from typing import Optional

from database.db import get_cursor


# ---------------------------------------------------------------------------
# business_profile
# ---------------------------------------------------------------------------

def get_business_profile() -> dict:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM business_profile WHERE id = 1")
        row = cur.fetchone()
        return dict(row) if row else {}


def update_business_profile(business_name: str, business_type: str,
                             low_stock_threshold: int) -> None:
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            UPDATE business_profile
            SET business_name = ?, business_type = ?, low_stock_threshold = ?
            WHERE id = 1
            """,
            (business_name, business_type, low_stock_threshold),
        )


# ---------------------------------------------------------------------------
# products
# ---------------------------------------------------------------------------

def add_product(name: str, category: str, quantity: int, cost_price: int,
                 selling_price: int, low_stock_threshold: Optional[int] = None) -> int:
    now = datetime.now().isoformat()
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO products (name, category, quantity, cost_price,
                selling_price, low_stock_threshold, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, category, quantity, cost_price, selling_price,
             low_stock_threshold, now, now),
        )
        return cur.lastrowid


def get_all_products() -> list:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM products ORDER BY name ASC")
        return [dict(r) for r in cur.fetchall()]


def get_product_by_id(product_id: int) -> Optional[dict]:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_product_by_name(name: str) -> Optional[dict]:
    """Case-insensitive exact match, used by the extraction pipeline."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM products WHERE LOWER(name) = LOWER(?) LIMIT 1",
            (name,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def update_product_stock(product_id: int, new_quantity: int) -> None:
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE products SET quantity = ?, updated_at = ? WHERE id = ?",
            (new_quantity, datetime.now().isoformat(), product_id),
        )


def update_product(product_id: int, name: str, category: str, cost_price: int,
                    selling_price: int, low_stock_threshold: Optional[int]) -> None:
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            UPDATE products
            SET name = ?, category = ?, cost_price = ?, selling_price = ?,
                low_stock_threshold = ?, updated_at = ?
            WHERE id = ?
            """,
            (name, category, cost_price, selling_price, low_stock_threshold,
             datetime.now().isoformat(), product_id),
        )


# ---------------------------------------------------------------------------
# transactions
# ---------------------------------------------------------------------------

def insert_transaction(date: str, type_: str, total_amount: int,
                        product_id: Optional[int] = None,
                        quantity: Optional[int] = None,
                        unit_price: Optional[int] = None,
                        cost_price: Optional[int] = None,
                        customer_id: Optional[int] = None,
                        supplier_id: Optional[int] = None,
                        expense_category: Optional[str] = None,
                        notes: Optional[str] = None,
                        source: str = "manual") -> int:
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO transactions (date, type, product_id, quantity,
                unit_price, cost_price, total_amount, customer_id, supplier_id,
                expense_category, notes, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (date, type_, product_id, quantity, unit_price, cost_price,
             total_amount, customer_id, supplier_id, expense_category, notes,
             source, datetime.now().isoformat()),
        )
        return cur.lastrowid


def get_transactions(start_date: Optional[str] = None,
                      end_date: Optional[str] = None,
                      type_: Optional[str] = None) -> list:
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    if type_:
        query += " AND type = ?"
        params.append(type_)
    query += " ORDER BY date DESC, id DESC"
    with get_cursor() as cur:
        cur.execute(query, params)
        return [dict(r) for r in cur.fetchall()]


def count_transactions() -> int:
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) as c FROM transactions")
        return cur.fetchone()["c"]


# ---------------------------------------------------------------------------
# receivables (Udhaar - money owed TO the business)
# ---------------------------------------------------------------------------

def add_receivable(customer_name: str, amount: int, due_date: Optional[str] = None,
                    notes: Optional[str] = None) -> int:
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO receivables (customer_name, amount, amount_paid,
                remaining_amount, due_date, status, notes, created_at)
            VALUES (?, ?, 0, ?, ?, 'pending', ?, ?)
            """,
            (customer_name, amount, amount, due_date, notes,
             datetime.now().isoformat()),
        )
        return cur.lastrowid


def get_receivables(status: Optional[str] = None) -> list:
    query = "SELECT * FROM receivables"
    params = []
    if status:
        query += " WHERE status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC"
    with get_cursor() as cur:
        cur.execute(query, params)
        return [dict(r) for r in cur.fetchall()]


def record_receivable_payment(receivable_id: int, payment_amount: int) -> None:
    with get_cursor(commit=True) as cur:
        cur.execute("SELECT amount, amount_paid FROM receivables WHERE id = ?",
                     (receivable_id,))
        row = cur.fetchone()
        if not row:
            return
        new_paid = row["amount_paid"] + payment_amount
        remaining = max(row["amount"] - new_paid, 0)
        status = "paid" if remaining == 0 else ("partial" if new_paid > 0 else "pending")
        cur.execute(
            """
            UPDATE receivables
            SET amount_paid = ?, remaining_amount = ?, status = ?
            WHERE id = ?
            """,
            (new_paid, remaining, status, receivable_id),
        )


# ---------------------------------------------------------------------------
# payables (money the business owes suppliers)
# ---------------------------------------------------------------------------

def add_payable(supplier_name: str, amount: int, due_date: Optional[str] = None,
                 notes: Optional[str] = None) -> int:
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO payables (supplier_name, amount, amount_paid,
                remaining_amount, due_date, status, notes, created_at)
            VALUES (?, ?, 0, ?, ?, 'pending', ?, ?)
            """,
            (supplier_name, amount, amount, due_date, notes,
             datetime.now().isoformat()),
        )
        return cur.lastrowid


def get_payables(status: Optional[str] = None) -> list:
    query = "SELECT * FROM payables"
    params = []
    if status:
        query += " WHERE status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC"
    with get_cursor() as cur:
        cur.execute(query, params)
        return [dict(r) for r in cur.fetchall()]


def record_payable_payment(payable_id: int, payment_amount: int) -> None:
    with get_cursor(commit=True) as cur:
        cur.execute("SELECT amount, amount_paid FROM payables WHERE id = ?",
                     (payable_id,))
        row = cur.fetchone()
        if not row:
            return
        new_paid = row["amount_paid"] + payment_amount
        remaining = max(row["amount"] - new_paid, 0)
        status = "paid" if remaining == 0 else ("partial" if new_paid > 0 else "pending")
        cur.execute(
            """
            UPDATE payables
            SET amount_paid = ?, remaining_amount = ?, status = ?
            WHERE id = ?
            """,
            (new_paid, remaining, status, payable_id),
        )
