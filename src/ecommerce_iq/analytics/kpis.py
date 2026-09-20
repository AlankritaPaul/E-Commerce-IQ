"""
Core KPI Calculation Engine.

Computes exact financial and operational metrics:
- Gross Merchandise Value (GMV)
- Net Revenue
- Average Order Value (AOV)
- Total Completed Orders
- Customer Lifetime Value (LTV)
"""

from datetime import date
from typing import Any, Optional
from src.ecommerce_iq.models.schemas import KPISummary


class KPICalculator:
    """
    Calculates primary business metrics from underlying transaction data.
    Implementation will be activated in Phase 3.
    """

    def __init__(self, db_manager: Any) -> None:
        self.db = db_manager

    def calculate_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> KPISummary:
        """
        Compute high-level executive KPI metrics for the specified date range.
        """
        raise NotImplementedError("KPI calculation will be implemented in Phase 3.")

    def calculate_revenue(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> float:
        """Calculate total gross revenue."""
        raise NotImplementedError("Revenue calculation will be implemented in Phase 3.")

    def calculate_aov(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> float:
        """Calculate Average Order Value (AOV)."""
        raise NotImplementedError("AOV calculation will be implemented in Phase 3.")
