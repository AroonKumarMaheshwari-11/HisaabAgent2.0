"""Small formatting helpers used across the UI layer."""

from datetime import datetime, timedelta

from config import CURRENCY_SYMBOL


def format_currency(amount) -> str:
    """1500 -> '₨1,500'. Negative values shown as '-₨1,500'."""
    if amount is None:
        return f"{CURRENCY_SYMBOL}0"
    amount = int(round(amount))
    sign = "-" if amount < 0 else ""
    return f"{sign}{CURRENCY_SYMBOL}{abs(amount):,}"


def format_percentage(value) -> str:
    if value is None:
        return "\u2014"  # em dash: no data
    sign = "+" if value > 0 else ""
    return f"{sign}{value}%"


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def days_ago_str(days: int) -> str:
    return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")


def format_date_display(iso_date: str) -> str:
    try:
        dt = datetime.strptime(iso_date[:10], "%Y-%m-%d")
        return dt.strftime("%d %b %Y")
    except (ValueError, TypeError):
        return iso_date or "\u2014"


def period_bounds(period_key: str):
    """
    Returns (start_date, end_date) ISO strings for a named period.
    'today' | '7d' | '30d' | 'month'
    """
    end = today_str()
    if period_key == "today":
        start = today_str()
    elif period_key == "7d":
        start = days_ago_str(7)
    elif period_key == "30d":
        start = days_ago_str(30)
    elif period_key == "month":
        start = datetime.now().strftime("%Y-%m-01")
    else:
        start = days_ago_str(30)
    return start, end


def previous_period_bounds(period_key: str):
    """The immediately preceding period of equal length, for comparisons."""
    now = datetime.now()
    if period_key == "today":
        start = end = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    elif period_key == "7d":
        end = days_ago_str(8)
        start = days_ago_str(14)
    elif period_key == "30d":
        end = days_ago_str(31)
        start = days_ago_str(60)
    elif period_key == "month":
        first_of_this_month = now.replace(day=1)
        last_of_prev_month = first_of_this_month - timedelta(days=1)
        start = last_of_prev_month.replace(day=1).strftime("%Y-%m-%d")
        end = last_of_prev_month.strftime("%Y-%m-%d")
    else:
        end = days_ago_str(31)
        start = days_ago_str(60)
    return start, end
