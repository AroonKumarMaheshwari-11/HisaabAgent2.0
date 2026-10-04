"""
Database connection management and initialization.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime

from config import DB_PATH
from database.schema import SCHEMA_STATEMENTS


def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_cursor(commit: bool = False):
    """
    Context manager yielding a cursor. Commits on success if commit=True,
    always closes the connection. Any exception rolls back and propagates.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create all tables if they don't exist, and seed a default business profile."""
    with get_cursor(commit=True) as cur:
        for statement in SCHEMA_STATEMENTS:
            cur.execute(statement)

        cur.execute("SELECT COUNT(*) as c FROM business_profile")
        row = cur.fetchone()
        if row["c"] == 0:
            cur.execute(
                """
                INSERT INTO business_profile (id, business_name, business_type,
                    currency, low_stock_threshold, created_at)
                VALUES (1, ?, ?, 'PKR', 10, ?)
                """,
                ("My Business", "General Retail", datetime.now().isoformat()),
            )


def reset_db() -> None:
    """Drop all data (used by 'reset demo data'). Keeps schema, wipes rows."""
    tables = ["transactions", "receivables", "payables", "products"]
    with get_cursor(commit=True) as cur:
        for t in tables:
            cur.execute(f"DELETE FROM {t}")
            cur.execute(f"DELETE FROM sqlite_sequence WHERE name = ?", (t,))
