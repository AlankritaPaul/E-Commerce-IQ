"""
Unit and Integration Tests for Returns, Refunds, and Financial Leakage Analytics.

Verifies:
- ReturnsAnalyticsEngine overall return summary scorecard and metrics
- Platform-wide return rate percentage
- Stated customer return reasons breakdown and taxonomy
- Product-level return rates, refund amounts, and risk categorization (High Risk vs Normal)
- Category-level return rates and benchmark rankings
- Monthly temporal return trends
- Cross-triangulation connecting sales volume, return rates, RMA reasons, and customer review complaints
"""

from datetime import date
from pathlib import Path
import sys
import unittest

_root = Path(__file__).resolve().parent.parent
for _p in (str(_root / "src"), str(_root)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ecommerce_iq.analytics.returns import ReturnsAnalyticsEngine
from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.models.schemas import (
    CategoryReturnMetric,
    ConnectedReturnInsight,
    ProductReturnMetric,
    ReturnReasonMetric,
    ReturnsOverallSummary,
)


class TestReturnsAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseManager()
        cls.engine = ReturnsAnalyticsEngine(cls.db)

    def test_overall_return_summary(self):
        """Verify platform-wide returns scorecard and financial leakage calculations."""
        summary = self.engine.get_overall_return_summary()
        self.assertIsInstance(summary, ReturnsOverallSummary)
        self.assertEqual(summary.total_return_events, 286)
        self.assertEqual(summary.total_units_returned, 332)
        self.assertEqual(summary.total_refund_amount, 41137.50)
        self.assertAlmostEqual(summary.platform_return_rate_pct, 4.76, delta=0.1)
        self.assertAlmostEqual(summary.refund_ratio_pct, 6.66, delta=0.1)
        self.assertGreaterEqual(summary.high_risk_products_count, 2)

        # Verify reasons breakdown inside summary
        self.assertGreaterEqual(len(summary.top_return_reasons), 5)
        top_reason = summary.top_return_reasons[0]
        self.assertEqual(top_reason.reason, "Customer Changed Mind")
        self.assertEqual(top_reason.incident_count, 118)

    def test_overall_return_rate(self):
        """Verify calculation of platform-wide return rate percentage."""
        rate = self.engine.get_overall_return_rate()
        self.assertAlmostEqual(rate, 4.76, delta=0.1)

    def test_return_reasons_breakdown_overall(self):
        """Verify return reasons breakdown incident sums and percentage allocations."""
        reasons = self.engine.get_return_reasons_breakdown()
        self.assertEqual(len(reasons), 6)

        total_incidents = sum(r.incident_count for r in reasons)
        self.assertEqual(total_incidents, 286)

        total_refunds = sum(r.total_refund_amount for r in reasons)
        self.assertEqual(total_refunds, 41137.50)

        total_pct = sum(r.percentage_of_all_returns for r in reasons)
        self.assertAlmostEqual(total_pct, 100.0, delta=0.5)

    def test_return_reasons_filtered_by_product(self):
        """Verify return reasons filtered for defect-prone SKU PROD-ELEC-001."""
        reasons = self.engine.get_return_reasons_breakdown(product_id=1)
        self.assertGreater(len(reasons), 0)
        # Primary reason for PROD-ELEC-001 must be Defective/Damaged
        self.assertEqual(reasons[0].reason, "Defective/Damaged")
        self.assertGreater(reasons[0].incident_count, 40)

        # Primary reason for PROD-APP-001 must be Incorrect Size/Fit
        app_reasons = self.engine.get_return_reasons_breakdown(product_id=7)
        self.assertGreater(len(app_reasons), 0)
        self.assertEqual(app_reasons[0].reason, "Incorrect Size/Fit")
        self.assertGreater(app_reasons[0].incident_count, 15)

    def test_return_rate_by_product(self):
        """Verify product-level return rates, refund ratios, and risk categorization."""
        products = self.engine.get_return_rate_by_product()
        self.assertGreaterEqual(len(products), 25)

        # Check PROD-ELEC-001
        elec_item = next((p for p in products if p.sku == "PROD-ELEC-001"), None)
        self.assertIsNotNone(elec_item)
        self.assertEqual(elec_item.risk_level, "High Risk")
        self.assertGreater(elec_item.return_rate_pct, 20.0)
        self.assertEqual(elec_item.primary_return_reason, "Defective/Damaged")
        self.assertAlmostEqual(
            elec_item.net_revenue,
            round(elec_item.gross_revenue - elec_item.refund_amount, 2),
            delta=0.01
        )

        # Check PROD-APP-001
        app_item = next((p for p in products if p.sku == "PROD-APP-001"), None)
        self.assertIsNotNone(app_item)
        self.assertEqual(app_item.risk_level, "High Risk")
        self.assertGreater(app_item.return_rate_pct, 15.0)
        self.assertEqual(app_item.primary_return_reason, "Incorrect Size/Fit")

    def test_highest_return_products(self):
        """Verify highest return products ranking extracts anomaly products."""
        top_returns = self.engine.get_highest_return_products(limit=5)
        self.assertEqual(len(top_returns), 5)
        self.assertEqual(top_returns[0].sku, "PROD-ELEC-001")
        self.assertEqual(top_returns[1].sku, "PROD-APP-001")
        self.assertGreaterEqual(top_returns[0].return_rate_pct, top_returns[1].return_rate_pct)

    def test_return_rate_by_category(self):
        """Verify category benchmarks rank Electronics and Apparel highest."""
        categories = self.engine.get_return_rate_by_category()
        self.assertEqual(len(categories), 6)

        # Electronics & Audio has highest return rate
        self.assertEqual(categories[0].category_name, "Electronics & Audio")
        self.assertGreater(categories[0].return_rate_pct, 7.0)
        self.assertEqual(categories[0].primary_return_reason, "Defective/Damaged")

        # Apparel & Activewear has second highest return rate
        self.assertEqual(categories[1].category_name, "Apparel & Activewear")
        self.assertGreater(categories[1].return_rate_pct, 5.5)
        self.assertEqual(categories[1].primary_return_reason, "Incorrect Size/Fit")

    def test_temporal_return_trends(self):
        """Verify monthly tracking of return events, returned quantities, and refund totals."""
        trends = self.engine.get_temporal_return_trends(granularity="monthly")
        self.assertGreaterEqual(len(trends), 14)

        for month in trends:
            self.assertIn("period", month)
            self.assertGreater(month["return_events"], 0)
            self.assertGreater(month["units_returned"], 0)
            self.assertGreater(month["total_refunds"], 0.0)
            self.assertGreater(month["return_rate_pct"], 0.0)

    def test_connected_return_review_insights(self):
        """Verify triangulation linking sales, return rates, and customer review NLP complaints."""
        insights = self.engine.get_connected_return_review_insights(return_rate_threshold=7.0)
        self.assertGreater(len(insights), 0)

        # Verify PROD-ELEC-001 hardware defect correlation
        elec_insight = next((i for i in insights if i.sku == "PROD-ELEC-001"), None)
        self.assertIsNotNone(elec_insight)
        self.assertIsInstance(elec_insight, ConnectedReturnInsight)
        self.assertGreater(elec_insight.return_rate_pct, 20.0)
        self.assertEqual(elec_insight.primary_return_reason, "Defective/Damaged")
        self.assertLess(elec_insight.average_rating, 2.5)
        self.assertGreater(elec_insight.negative_review_pct, 75.0)
        self.assertIn("Defect", elec_insight.correlation_verdict)

        # Verify PROD-APP-001 sizing defect correlation
        app_insight = next((i for i in insights if i.sku == "PROD-APP-001"), None)
        self.assertIsNotNone(app_insight)
        self.assertIsInstance(app_insight, ConnectedReturnInsight)
        self.assertGreater(app_insight.return_rate_pct, 15.0)
        self.assertEqual(app_insight.primary_return_reason, "Incorrect Size/Fit")
        self.assertIn("Sizing", app_insight.correlation_verdict)


if __name__ == "__main__":
    unittest.main()
