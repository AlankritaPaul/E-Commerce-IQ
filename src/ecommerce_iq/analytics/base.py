"""
Base Analytics Engine Interface.

Provides shared database connection handling, date parameter validation,
and helper routines for all specialized analytical calculation engines.
"""

from datetime import date
from typing import Any, Optional
from ecommerce_iq.database.connection import DatabaseManager


class BaseAnalyticsEngine:
    """
    Foundational class for all analytical engines.
    Encapsulates database access and query execution helpers.
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
        Helper to generate SQL WHERE date filtering clauses.
        """
        clauses = []
        if start_date:
            clauses.append(f"{date_column} >= '{start_date.isoformat()}'")
        if end_date:
            clauses.append(f"{date_column} <= '{end_date.isoformat()}'")

        if clauses:
            return " AND " + " AND ".join(clauses)
        return ""
