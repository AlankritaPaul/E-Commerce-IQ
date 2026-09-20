"""
Input Validation and Parameter Sanitization Utilities.

Provides helper routines to validate date ranges, numeric thresholds,
and sanitize SQL identifiers.
"""

from datetime import date
from typing import Optional, Tuple


def validate_date_range(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate that start_date does not exceed end_date.

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if start_date and end_date and start_date > end_date:
        return False, f"Start date ({start_date}) cannot be after end date ({end_date})."
    return True, None


def clamp_limit(limit: int, default: int = 10, max_limit: int = 100) -> int:
    """
    Ensure an integer query limit falls within [1, max_limit].
    """
    if limit <= 0:
        return default
    return min(limit, max_limit)


def sanitize_identifier(identifier: str) -> str:
    """
    Sanitize column or table names to prevent identifier injection.
    Allows only alphanumeric characters and underscores.
    """
    import re
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "", identifier)
    if not cleaned:
        raise ValueError("Identifier must contain at least one alphanumeric character.")
    return cleaned
