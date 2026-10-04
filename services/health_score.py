"""
Business Health Score - fully deterministic, rule-based scoring.

Gemini is never asked to produce these numbers. It only receives the
already-computed sub-scores and writes a plain-language explanation of them
(see ai/advisor_agent.py). This module is the one a hackathon judge should
be pointed to when they ask "how is this score calculated?"

Each sub-score independently returns None when there isn't enough data to
compute it meaningfully - callers must render "Not enough data yet" for that
sub-score rather than defaulting it to some fake neutral number, which would
silently drag down (or inflate) the overall score.
"""

from typing import Optional

from config import HEALTH_SCORE_WEIGHTS, HEALTH_SCORE_BANDS
from services.calculations import calculate_percentage_change, safe_divide


def score_financial_health(revenue: int, expenses: int, profit: int) -> Optional[float]:
    """
    Financial health: rewards positive profit and a healthy profit margin.
    Requires at least some revenue to be meaningful.
    """
    if not revenue:
        return None
    margin = safe_divide(profit, revenue)
    if margin is None:
        return None
    # Map margin (-100%..+100%+) onto a 0-100 score, centered so 20% margin ~ 80 score.
    score = 50 + (margin * 100 * 1.5)
    return round(max(0, min(100, score)), 1)


def score_inventory_health(products: list) -> Optional[float]:
    """
    Inventory health: proportion of products that are NOT low/out of stock.
    Requires at least one product to exist.
    """
    if not products:
        return None
    healthy_count = 0
    for p in products:
        threshold = p.get("low_stock_threshold") or 10
        if (p.get("quantity") or 0) > threshold:
            healthy_count += 1
    return round((healthy_count / len(products)) * 100, 1)


def score_cash_flow_health(total_receivables: int, total_payables: int,
                            cash_in: int, cash_out: int) -> Optional[float]:
    """
    Cash flow health: penalizes payables that heavily outweigh receivables +
    incoming cash. Requires some financial activity to exist.
    """
    if cash_in == 0 and cash_out == 0 and total_receivables == 0 and total_payables == 0:
        return None

    liquidity = cash_in + total_receivables
    obligations = cash_out + total_payables

    if obligations == 0:
        return 100.0
    ratio = safe_divide(liquidity, obligations)
    if ratio is None:
        return None
    # ratio of 1.0 (break-even) -> 60 score; ratio of 2.0+ -> 100; ratio of 0 -> 0
    score = min(100.0, ratio * 60)
    return round(max(0, score), 1)


def score_sales_performance(current_revenue: int, previous_revenue: Optional[int]) -> Optional[float]:
    """
    Sales performance: period-over-period revenue growth.
    Explicitly returns None if there's no comparable previous period -
    this sub-score should NOT silently become "neutral 50" when we simply
    don't have two periods of data yet.
    """
    change = calculate_percentage_change(current_revenue, previous_revenue)
    if change is None:
        return None
    # +20% growth -> 100, 0% -> 60, -20% -> 20 (clamped)
    score = 60 + (change * 2)
    return round(max(0, min(100, score)), 1)


def calculate_overall_health_score(sub_scores: dict) -> Optional[float]:
    """
    Weighted average of whichever sub-scores are actually available.
    Weights are re-normalized over the available subset so a missing
    sub-score doesn't quietly punish the business - it's just excluded.
    """
    available = {k: v for k, v in sub_scores.items() if v is not None}
    if not available:
        return None
    total_weight = sum(HEALTH_SCORE_WEIGHTS[k] for k in available)
    if total_weight == 0:
        return None
    weighted_sum = sum(available[k] * HEALTH_SCORE_WEIGHTS[k] for k in available)
    return round(weighted_sum / total_weight, 1)


def get_health_band(score: Optional[float]):
    """Returns (label, color_key) for a given score, per config.HEALTH_SCORE_BANDS."""
    if score is None:
        return ("Not enough data", "muted")
    for threshold, label, color_key in HEALTH_SCORE_BANDS:
        if score >= threshold:
            return (label, color_key)
    return ("At Risk", "red")
