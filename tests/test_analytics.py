"""
Unit and Integration Tests for Sales & Revenue Analytics Engine.

Verifies:
- BaseAnalyticsEngine helper routines and date filter construction
- KPICalculator: Total revenue, order count, AOV, time-series (day/week/month), and status breakdown
- ProductAnalyticsEngine: Revenue by product, top products (Cash Cows), underperforming products (Dead Stock), category breakdown
- PeriodComparisonEngine: MoM, WoW, and custom period growth/decline variances
"""

from datetime import date
from pathlib import Path
import unittest
import sys

_root = Path(__file__).resolve().parent.parent
for _p in (str(_root / "src"), str(_root)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ecommerce_iq.analytics.base import BaseAnalyticsEngine
from ecommerce_iq.analytics.kpis import KPICalculator
from ecommerce_iq.analytics.comparisons import PeriodComparisonEngine
from ecommerce_iq.analytics.products import ProductAnalyticsEngine
from ecommerce_iq.analytics.returns import ReturnsAnalyticsEngine
from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.models.schemas import KPISummary, PeriodComparisonResult


class TestAnalyticsEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseManager()
        cls.kpi = KPICalculator(cls.db)
        cls.product_engine = ProductAnalyticsEngine(cls.db)
        cls.comparison_engine = PeriodComparisonEngine(cls.db)

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
        self.assertIn("orders.order_date <= '2025-01-31 23:59:59'", clause)
        self.assertTrue(clause.startswith(" AND "))

        # Only start date
        start_only = base_engine._format_date_filter("orders.order_date", start_date=date(2025, 1, 1))
        self.assertIn("orders.order_date >= '2025-01-01'", start_only)
        self.assertNotIn("<=", start_only)

        # No dates provided
        empty_clause = base_engine._format_date_filter("orders.order_date")
        self.assertEqual(empty_clause, "")

    def test_safe_math_helpers(self):
        """Verify safe division and growth rate calculations."""
        self.assertEqual(BaseAnalyticsEngine.safe_divide(100, 0), 0.0)
        self.assertEqual(BaseAnalyticsEngine.safe_divide(100, 4), 25.0)

        # Positive growth
        pct, trend = BaseAnalyticsEngine.calculate_growth_rate(120, 100)
        self.assertEqual(pct, 20.0)
        self.assertEqual(trend, "positive")

        # Negative growth
        pct, trend = BaseAnalyticsEngine.calculate_growth_rate(80, 100)
        self.assertEqual(pct, -20.0)
        self.assertEqual(trend, "negative")

        # Zero baseline
        pct, trend = BaseAnalyticsEngine.calculate_growth_rate(50, 0)
        self.assertEqual(pct, 100.0)
        self.assertEqual(trend, "positive")

    def test_kpi_summary_calculation(self):
        """Verify KPISummary produces realistic metrics from database."""
        summary = self.kpi.calculate_summary()
        self.assertIsInstance(summary, KPISummary)
        self.assertGreater(summary.total_revenue, 100000.0)
        self.assertGreater(summary.net_revenue, 100000.0)
        self.assertGreater(summary.total_orders, 1000)
        self.assertGreater(summary.average_order_value, 50.0)
        self.assertGreater(summary.active_customers, 100)
        self.assertGreater(summary.return_rate_percentage, 0.0)
        self.assertGreater(summary.gross_margin_percentage or 0.0, 20.0)

    def test_calculate_revenue_with_date_filter(self):
        """Verify revenue calculation with date interval filters."""
        # Full year revenue
        total_rev = self.kpi.calculate_revenue()
        self.assertGreater(total_rev, 500000.0)

        # Single month (January 2025)
        jan_rev = self.kpi.calculate_revenue(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
        self.assertGreater(jan_rev, 10000.0)
        self.assertLess(jan_rev, total_rev)

    def test_order_count_and_status_breakdown(self):
        """Verify order count queries and status breakdowns."""
        completed_orders = self.kpi.calculate_order_count(status="completed")
        self.assertGreater(completed_orders, 1000)

        breakdown = self.kpi.get_order_status_breakdown()
        self.assertIn("completed", breakdown)
        self.assertGreater(breakdown["completed"], 0)

    def test_revenue_time_series(self):
        """Verify time-series aggregation by day, week, and month."""
        # By Month
        monthly = self.kpi.get_revenue_by_month()
        self.assertGreater(len(monthly), 10)
        self.assertIn("period", monthly[0])
        self.assertIn("net_revenue", monthly[0])
        self.assertIn("order_count", monthly[0])

        # By Week
        weekly = self.kpi.get_revenue_by_week(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31)
        )
        self.assertGreater(len(weekly), 8)

        # By Day
        daily = self.kpi.get_revenue_by_day(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 14)
        )
        self.assertGreater(len(daily), 5)

    def test_revenue_by_product(self):
        """Verify product revenue metrics and sorting."""
        products = self.product_engine.get_revenue_by_product(limit=10)
        self.assertGreater(len(products), 0)

        first_prod = products[0]
        self.assertIn("sku", first_prod)
        self.assertIn("net_revenue", first_prod)
        self.assertIn("gross_profit", first_prod)
        self.assertIn("profit_margin_pct", first_prod)
        self.assertIn("return_rate_pct", first_prod)
        self.assertGreater(first_prod["net_revenue"], 0.0)

    def test_top_and_underperforming_products(self):
        """Verify top performers have higher revenue than underperforming products."""
        top_prods = self.product_engine.get_top_products(limit=3)
        laggards = self.product_engine.get_underperforming_products(limit=3)

        self.assertEqual(len(top_prods), 3)
        self.assertEqual(len(laggards), 3)
        self.assertGreater(top_prods[0]["net_revenue"], laggards[0]["net_revenue"])

    def test_category_breakdown(self):
        """Verify category breakdown returns all active product categories."""
        categories = self.product_engine.get_category_breakdown()
        self.assertGreater(len(categories), 3)
        cat_names = [c["category_name"] for c in categories]
        self.assertIn("Electronics & Audio", cat_names)
        self.assertIn("Apparel & Activewear", cat_names)

    def test_period_comparison_month_over_month(self):
        """Verify MoM comparison successfully detects the August 2025 decline anomaly."""
        # August 2025 vs July 2025
        mom_results = self.comparison_engine.compare_month_over_month(
            target_year=2025,
            target_month=8
        )
        self.assertGreater(len(mom_results), 0)

        # Find Net Revenue metric
        rev_metric = next((m for m in mom_results if "Net Revenue" in m.metric_name), None)
        self.assertIsNotNone(rev_metric)
        self.assertEqual(rev_metric.trend_direction, "negative")
        self.assertLess(rev_metric.percentage_change, -30.0)  # Verify sharp drop

    def test_period_comparison_week_over_week(self):
        """Verify WoW comparison executes and returns structured results."""
        wow_results = self.comparison_engine.compare_week_over_week(
            target_year=2025,
            target_week=20
        )
        self.assertGreater(len(wow_results), 0)
        self.assertIsInstance(wow_results[0], PeriodComparisonResult)


if __name__ == "__main__":
    unittest.main()
