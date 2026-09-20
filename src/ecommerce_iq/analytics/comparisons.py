"""
Temporal Period-over-Period Comparison Engine.

Provides automated variance calculations across:
- Month-over-Month (MoM)
- Week-over-Week (WoW)
- Year-over-Year (YoY)
- Custom Date Range Comparisons
"""

from typing import Any, List
from src.ecommerce_iq.models.schemas import PeriodComparisonResult


class PeriodComparisonEngine:
    """
    Computes variances, percentage deltas, and trend directions between periods.
    Implementation will be activated in Phase 3.
    """

    def __init__(self, db_manager: Any) -> None:
        self.db = db_manager

    def compare_month_over_month(
        self,
        target_year: int,
        target_month: int
    ) -> List[PeriodComparisonResult]:
        """
        Compare performance of target month against immediate prior month.
        """
        raise NotImplementedError("MoM comparison will be implemented in Phase 3.")

    def compare_week_over_week(
        self,
        target_year: int,
        target_week: int
    ) -> List[PeriodComparisonResult]:
        """
        Compare performance of target ISO week against prior week.
        """
        raise NotImplementedError("WoW comparison will be implemented in Phase 3.")
