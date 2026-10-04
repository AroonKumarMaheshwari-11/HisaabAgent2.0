"""
All table definitions for HisaabAgent's SQLite database.

Design notes (stated explicitly so they're not accidentally "fixed" later):
- All monetary values are stored as INTEGER whole PKR. Micro-business users
  don't enter fractional rupees, and integers sidestep float rounding bugs
  in every downstream sum.
- There is a single `expenses` table dropped: expense rows live in
  `transactions` with type='expense' and a populated `expense_category`.
  Keeping one ledger avoids two write-paths that can drift out of sync.
- Dates are stored as ISO 8601 strings ('YYYY-MM-DD' or full timestamp for
  created_at) so lexicographic sort == chronological sort.
"""

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS business_profile (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        business_name TEXT NOT NULL DEFAULT 'My Business',
        business_type TEXT NOT NULL DEFAULT 'General Retail',
        currency TEXT NOT NULL DEFAULT 'PKR',
        low_stock_threshold INTEGER NOT NULL DEFAULT 10,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        quantity INTEGER NOT NULL DEFAULT 0,
        cost_price INTEGER NOT NULL DEFAULT 0,
        selling_price INTEGER NOT NULL DEFAULT 0,
        low_stock_threshold INTEGER,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS receivables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        amount INTEGER NOT NULL,
        amount_paid INTEGER NOT NULL DEFAULT 0,
        remaining_amount INTEGER NOT NULL,
        due_date TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        notes TEXT,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS payables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL,
        amount INTEGER NOT NULL,
        amount_paid INTEGER NOT NULL DEFAULT 0,
        remaining_amount INTEGER NOT NULL,
        due_date TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        notes TEXT,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        type TEXT NOT NULL CHECK (type IN ('sale','purchase','expense')),
        product_id INTEGER,
        quantity INTEGER,
        unit_price INTEGER,
        cost_price INTEGER,
        total_amount INTEGER NOT NULL,
        customer_id INTEGER,
        supplier_id INTEGER,
        expense_category TEXT,
        notes TEXT,
        source TEXT NOT NULL DEFAULT 'manual',
        created_at TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (id),
        FOREIGN KEY (customer_id) REFERENCES receivables (id),
        FOREIGN KEY (supplier_id) REFERENCES payables (id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions (date)",
    "CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions (type)",
    "CREATE INDEX IF NOT EXISTS idx_receivables_status ON receivables (status)",
    "CREATE INDEX IF NOT EXISTS idx_payables_status ON payables (status)",
]
