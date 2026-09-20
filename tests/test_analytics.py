import sys
from datetime import date
from pathlib import Path
import unittest

_root = Path(__file__).resolve().parent.parent
for _p in (str(_root / "src"), str(_root)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ecommerce_iq.analytics.base import BaseAnalyticsEngine
from ecommerce_iq.analytics.kpis import KPICalculator
from ecommerce_iq.analytics.comparisons import PeriodComparisonEngine
from ecommerce_iq.analytics.products import ProductAnalyticsEngine
from ecommerce_iq.analytics.returns import ReturnsAnalyticsEngine


class TestAnalytics(unittest.TestCase):
    def test_base_analytics_date_filter_formatting(self):
        """Verify date filter clause formatting helper."""
        base_engine = BaseAnalyticsEngine()

        # Both start and end dates
        clause = base_engine._format_date_filter(
            "orders.order_date",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
        self.assertIn("orders.order_date >= '2025-01-01'", clause)
        self.assertIn("orders.order_date <= '2025-01-31'", clause)
        self.assertTrue(clause.startswith(" AND "))

        # Only start date
        start_only = base_engine._format_date_filter("orders.order_date", start_date=date(2025, 1, 1))
        self.assertIn("orders.order_date >= '2025-01-01'", start_only)
        self.assertNotIn("<=", start_only)

        # No dates provided
        empty_clause = base_engine._format_date_filter("orders.order_date")
        self.assertEqual(empty_clause, "")

    def test_analytics_classes_instantiation(self):
        """Verify that analytics classes can be initialized with mock db manager."""
        mock_db = object()

        kpi_calc = KPICalculator(mock_db)
        self.assertIs(kpi_calc.db, mock_db)

        comp_engine = PeriodComparisonEngine(mock_db)
        self.assertIs(comp_engine.db, mock_db)

        prod_engine = ProductAnalyticsEngine(mock_db)
        self.assertIs(prod_engine.db, mock_db)

        ret_engine = ReturnsAnalyticsEngine(mock_db)
        self.assertIs(ret_engine.db, mock_db)


if __name__ == "__main__":
    unittest.main()
