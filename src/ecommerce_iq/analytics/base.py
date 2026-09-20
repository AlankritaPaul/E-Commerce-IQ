"""
Base Analytics Engine Interface.

Provides shared database connection handling, date parameter validation,
safe numerical routines, and query execution helpers for all specialized
analytical calculation engines.
"""

from datetime import date
from typing import Any, Dict, List, Optional, Tuple
from ecommerce_iq.database.connection import DatabaseManager


class BaseAnalyticsEngine:
    """
    Foundational class for all analytical engines.
    Encapsulates database access, query execution, and parameter formatting.
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None) -> None:
        self.db = db_manager or DatabaseManager()

    def _format_date_filter(
        self,
        date_column: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> str:
        """
        Generate SQL WHERE date filtering clauses.
        """
        clauses = []
        if start_date:
            clauses.append(f"{date_column} >= '{start_date.isoformat()}'")
        if end_date:
            clauses.append(f"{date_column} <= '{end_date.isoformat()} 23:59:59'")

        if clauses:
            return " AND " + " AND ".join(clauses)
        return ""

    def execute_query(self, query: str, params: Optional[Any] = None) -> List[Dict[str, Any]]:
        """Delegate SQL query execution to the configured DatabaseManager."""
        return self.db.execute_query(query, params)

    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """Safely compute division avoiding ZeroDivisionError."""
        if not denominator or denominator == 0.0:
            return default
        return numerator / denominator

    @staticmethod
    def calculate_growth_rate(current: float, previous: float) -> Tuple[float, str]:
        """
        Calculate percentage growth and trend direction.
        Returns:
            Tuple of (percentage_change: float, trend_direction: str)
        """
        if previous == 0.0:
            pct = 100.0 if current > 0.0 else 0.0
        else:
            pct = round(((current - previous) / abs(previous)) * 100.0, 2)

        if pct > 0.0:
            trend = "positive"
        elif pct < 0.0:
            trend = "negative"
        else:
            trend = "neutral"

        return pct, trend
