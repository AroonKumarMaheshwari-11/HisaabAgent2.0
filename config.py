"""
Central configuration for HisaabAgent2.0.

Every constant that could plausibly need changing later (model name,
thresholds, scoring weights, colors) lives here so it's never scattered
across the codebase.
"""

import os

# ---------------------------------------------------------------------------
# Gemini configuration
# ---------------------------------------------------------------------------
# Single place to change the model. Do not hard-code model names anywhere else.
GEMINI_MODEL = "gemini-2.5-flash"

# Resolution order: environment variable first (local dev), then Streamlit
# secrets (deployed). We don't import streamlit here to keep this module
# import-light; ai/gemini_client.py handles the actual secrets lookup.
GEMINI_API_KEY_ENV_VAR = "GEMINI_API_KEY"

GEMINI_TEMPERATURE_EXTRACTION = 0.1   # low: we want consistent structured output
GEMINI_TEMPERATURE_ANALYSIS = 0.4     # a bit more room for natural phrasing

GEMINI_MAX_RETRIES = 2

# ---------------------------------------------------------------------------
# Business / currency
# ---------------------------------------------------------------------------
CURRENCY_SYMBOL = "\u20a8"  # Rs sign
CURRENCY_CODE = "PKR"

DEFAULT_LOW_STOCK_THRESHOLD = 10

# ---------------------------------------------------------------------------
# Business Health Score weights (must sum to 1.0)
# ---------------------------------------------------------------------------
HEALTH_SCORE_WEIGHTS = {
    "financial": 0.35,
    "inventory": 0.20,
    "cash_flow": 0.25,
    "sales_performance": 0.20,
}

HEALTH_SCORE_BANDS = [
    (80, "Healthy", "green"),
    (55, "Needs Attention", "amber"),
    (0, "At Risk", "red"),
]

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hisaabagent.db")

# ---------------------------------------------------------------------------
# App metadata
# ---------------------------------------------------------------------------
APP_NAME = "HisaabAgent2.0"
APP_TAGLINE = "Your AI-powered business co-pilot for everyday decisions."

DISCLAIMER_TEXT = (
    "AI-generated insights are for informational purposes and should be "
    "verified before making important financial decisions."
)

# ---------------------------------------------------------------------------
# Color tokens - LIGHT THEME (single source of truth for ui/styles.py
# and ui/charts.py)
# ---------------------------------------------------------------------------
COLORS = {
    "bg_deep": "#0D1424",
    "bg_deep_end": "#090D16",
    "bg_panel": "#0A0F1D",
    "bg_card": "#131B2E",
    "border": "#243049",

    "text_primary": "#F8FAFC",
    "text_muted": "#94A3B8",

    "accent_primary": "#10B981",
    "accent_hover": "#34D399",
    "on_accent": "#04261C",
    "accent_gold": "#FBBF24",
    "accent_red": "#F87171",
    "accent_amber": "#F59E0B",
    "accent_blue": "#38BDF8",
}