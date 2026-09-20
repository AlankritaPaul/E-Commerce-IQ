"""
Formatting Utilities.

Helper functions for formatting currency, percentages, numbers, and dates
for consistent executive dashboard presentation.
"""

from datetime import date, datetime
from typing import Union


def format_currency(value: Union[float, int], currency_symbol: str = "$") -> str:
    """
    Format numeric value as currency string with commas and two decimals.
    Example: 12500.5 -> "$12,500.50"
    """
    return f"{currency_symbol}{value:,.2f}"


def format_percentage(value: Union[float, int], include_sign: bool = False) -> str:
    """
    Format numeric value as a percentage.
    Example: 12.345 -> "+12.3%" (if include_sign=True)
    """
    sign = "+" if include_sign and value > 0 else ""
    return f"{sign}{value:.1f}%"


def format_delta_display(change_pct: float) -> str:
    """
    Return human-readable delta indicator string.
    Example: 5.2 -> "+5.2% vs previous period"
    """
    sign = "+" if change_pct > 0 else ""
    return f"{sign}{change_pct:.1f}% vs previous period"
