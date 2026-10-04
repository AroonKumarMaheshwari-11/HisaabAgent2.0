"""
Lightweight RAG (retrieval-augmented generation) for HisaabAgent2.0.

Two retrieval sources, both ranked with BM25 (pure Python, no extra
packages, works offline):
  1. knowledge/*.md  - a small retail playbook (chunked by '## ' headings)
  2. the business's own records (transactions, udhaar, payables)

The agent calls these as tools; retrieved text is the ONLY thing it may
base advice on, and numbers still come from deterministic Python.
"""

import math
import os
import re
from collections import Counter

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_KB_DIR = os.path.join(_ROOT, "knowledge")
_TOKEN = re.compile(r"[a-z0-9\u0600-\u06ff]+")
_STOP = {
    "the", "a", "an", "is", "are", "of", "to", "in", "on", "and", "or", "for",
    "it", "this", "that", "with", "as", "at", "be", "by", "my", "me", "i",
    "ka", "ki", "ke", "ko", "se", "me", "mein", "hai", "hain", "ho", "kya",
    "aur", "ya", "par", "pe", "ne", "bhi", "to", "kar", "karo", "kaise",
}


def _tokens(text: str) -> list:
    return [t for t in _TOKEN.findall(text.lower()) if len(t) > 1 and t not in _STOP]


class _BM25:
    def __init__(self, docs: list, k1: float = 1.5, b: float = 0.75):
        self.docs = docs
        self.k1, self.b = k1, b
        self.tokens = [_tokens(d["text"] + " " + d.get("title", "")) for d in docs]
        self.tf = [Counter(t) for t in self.tokens]
        self.df = Counter()
        for t in self.tokens:
            self.df.update(set(t))
        total = sum(len(t) for t in self.tokens)
        self.avgdl = (total / len(self.tokens)) if self.tokens else 1.0

    def search(self, query: str, k: int = 3) -> list:
        q = _tokens(query)
        n = len(self.docs)
        scored = []
        for i, tf in enumerate(self.tf):
            dl = len(self.tokens[i]) or 1
            score = 0.0
            for term in q:
                f = tf.get(term, 0)
                if not f:
                    continue
                idf = math.log(1 + (n - self.df[term] + 0.5) / (self.df[term] + 0.5))
                score += idf * f * (self.k1 + 1) / (
                    f + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
            if score > 0:
                scored.append((score, i))
        scored.sort(reverse=True)
        return [{**self.docs[i], "score": round(s, 2)} for s, i in scored[:k]]


# ---------------------------------------------------------------------------
# 1. Knowledge base (markdown files)
# ---------------------------------------------------------------------------
_kb_index = None


def _load_knowledge() -> list:
    docs = []
    if not os.path.isdir(_KB_DIR):
        return docs
    for name in sorted(os.listdir(_KB_DIR)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(_KB_DIR, name), encoding="utf-8") as f:
            content = f.read()
        for chunk in re.split(r"\n(?=## )", content):
            chunk = chunk.strip()
            if not chunk:
                continue
            first = chunk.splitlines()[0]
            title = first.lstrip("# ").strip() if first.startswith("#") else name
            docs.append({"source": name, "title": title, "text": chunk})
    return docs


def search_knowledge(query: str, k: int = 3) -> list:
    global _kb_index
    if _kb_index is None:
        _kb_index = _BM25(_load_knowledge())
    return _kb_index.search(query, k)


# ---------------------------------------------------------------------------
# 2. The business's own records
# ---------------------------------------------------------------------------
def _record_docs() -> list:
    from database import queries
    docs = []
    try:
        products = {p["id"]: p.get("name", "") for p in queries.get_all_products()}
    except Exception:
        products = {}

    try:
        txns = queries.get_transactions(start_date="2000-01-01", end_date="2999-12-31")
    except Exception:
        from utils.helpers import period_bounds
        txns = queries.get_transactions(*period_bounds("30d"))

    for t in txns:
        product = products.get(t.get("product_id"), "")
        parts = [
            f"{t.get('type', '')} on {str(t.get('date', ''))[:10]}",
            f"product {product}" if product else "",
            f"quantity {t.get('quantity')}" if t.get("quantity") else "",
            f"total {t.get('total_amount')}",
            f"category {t.get('expense_category')}" if t.get("expense_category") else "",
            f"customer {t.get('customer_name')}" if t.get("customer_name") else "",
            f"supplier {t.get('supplier_name')}" if t.get("supplier_name") else "",
            str(t.get("notes") or t.get("description") or ""),
        ]
        docs.append({"kind": "transaction", "title": t.get("type", ""),
                     "text": ", ".join(p for p in parts if p)})

    try:
        for r in queries.get_receivables():
            docs.append({"kind": "udhaar", "title": "receivable", "text": (
                f"udhaar receivable customer {r.get('customer_name')} "
                f"remaining {r.get('remaining_amount')} due {r.get('due_date')} "
                f"status {r.get('status')}")})
        for p in queries.get_payables():
            docs.append({"kind": "payable", "title": "payable", "text": (
                f"payable supplier {p.get('supplier_name')} "
                f"remaining {p.get('remaining_amount')} due {p.get('due_date')} "
                f"status {p.get('status')}")})
    except Exception:
        pass
    return docs


def search_records(query: str, k: int = 5) -> list:
    docs = _record_docs()
    if not docs:
        return []
    return _BM25(docs).search(query, k)