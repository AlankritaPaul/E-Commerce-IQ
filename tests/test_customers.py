"""
Unit and Integration Tests for Customer Behavior Analytics and RFM Segmentation.

Verifies:
- CustomerAnalyticsEngine aggregate metrics (LTV, repeat rate, order frequency)
- Order frequency distribution brackets and revenue attribution
- Customer-level profiling with strict PII masking
- Detailed customer purchase history, reviews, and return timelines
- Geographic customer distribution by city and country
- CustomerSegmentationEngine RFM scoring (1-5 quintiles) and cohort summaries
- Churn risk cohort identification with revenue-at-risk estimation
"""

from datetime import date
from pathlib import Path
import sys
import unittest

_root = Path(__file__).resolve().parent.parent
for _p in (str(_root / "src"), str(_root)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ecommerce_iq.analytics.customers import CustomerAnalyticsEngine
from ecommerce_iq.business_logic.segmentation import CustomerSegmentationEngine
from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.models.schemas import CustomerAggregateSummary, CustomerProfile, RFMCustomerScore, ChurnRiskCustomer


class TestCustomerAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseManager()
        cls.analytics_engine = CustomerAnalyticsEngine(cls.db)
        cls.segmentation_engine = CustomerSegmentationEngine(cls.db)

    def test_aggregate_customer_metrics(self):
        """Verify platform-wide customer metrics and behavioral scorecards."""
        summary = self.analytics_engine.get_aggregate_customer_metrics()
        self.assertIsInstance(summary, CustomerAggregateSummary)
        self.assertEqual(summary.total_registered_customers, 850)
        self.assertGreater(summary.active_purchasers, 800)
        self.assertGreater(summary.repeat_customers, 700)
        self.assertGreater(summary.one_time_buyers, 0)
        self.assertGreater(summary.repeat_purchase_rate_pct, 80.0)
        self.assertGreater(summary.average_customer_ltv, 500.0)
        self.assertGreater(summary.average_order_frequency, 3.0)
        self.assertGreater(summary.customer_return_rate_pct, 10.0)
        self.assertGreater(summary.review_participation_rate_pct, 50.0)
        self.assertIn("VIP High Value", summary.segment_breakdown)
        self.assertIn("Regular", summary.segment_breakdown)

    def test_order_frequency_distribution(self):
        """Verify customer distribution across order frequency brackets."""
        distribution = self.analytics_engine.get_order_frequency_distribution()
        self.assertGreater(len(distribution), 3)

        bracket_names = [d["bracket"] for d in distribution]
        self.assertTrue(any("1 Order" in b for b in bracket_names))
        self.assertTrue(any("2-3 Orders" in b for b in bracket_names))

        total_pct = sum(d["customer_pct"] for d in distribution)
        self.assertAlmostEqual(total_pct, 100.0, delta=1.5)

        for item in distribution:
            self.assertGreater(item["customer_count"], 0)
            self.assertGreater(item["total_revenue"], 0.0)
            self.assertGreater(item["avg_spend_per_customer"], 0.0)

    def test_customer_profiles_and_pii_masking(self):
        """Verify customer profiles aggregate order metrics and strictly mask PII."""
        profiles = self.analytics_engine.get_customer_profiles(limit=10)
        self.assertEqual(len(profiles), 10)

        for p in profiles:
            self.assertIsInstance(p, CustomerProfile)
            # Verify PII masking format: "First L."
            parts = p.display_name.split()
            self.assertGreaterEqual(len(parts), 2)
            self.assertTrue(parts[-1].endswith("."))
            self.assertEqual(len(parts[-1]), 2)  # Single letter + dot e.g. "S."
            self.assertNotIn("@", p.display_name)
            self.assertGreater(p.total_spend, 0.0)
            self.assertGreater(p.order_count, 0)
            self.assertGreater(p.average_order_value, 0.0)
            self.assertGreaterEqual(p.days_since_last_order, 0)

        # Verify sorted descending by total_spend
        for i in range(len(profiles) - 1):
            self.assertGreaterEqual(profiles[i].total_spend, profiles[i + 1].total_spend)

    def test_customer_profiles_filtering(self):
        """Verify filtering customer profiles by segment and min_orders."""
        vip_profiles = self.analytics_engine.get_customer_profiles(
            limit=5,
            segment="VIP High Value",
            min_orders=5
        )
        self.assertGreater(len(vip_profiles), 0)
        for p in vip_profiles:
            self.assertEqual(p.segment, "VIP High Value")
            self.assertGreaterEqual(p.order_count, 5)

    def test_customer_detail_retrieval(self):
        """Verify retrieval of complete single-customer order history and feedback."""
        detail = self.analytics_engine.get_customer_detail(customer_id=114)
        self.assertIsNotNone(detail)
        self.assertEqual(detail["customer_id"], 114)
        self.assertTrue(detail["display_name"].endswith("."))
        self.assertGreater(detail["total_orders"], 0)
        self.assertGreater(detail["total_spend"], 0.0)
        self.assertIn("orders", detail)
        self.assertIn("returns", detail)
        self.assertIn("reviews", detail)
        self.assertIsInstance(detail["orders"], list)

    def test_nonexistent_customer_detail(self):
        """Verify querying non-existent customer returns None."""
        detail = self.analytics_engine.get_customer_detail(customer_id=999999)
        self.assertIsNone(detail)

    def test_geographic_distribution(self):
        """Verify customer counts and revenue aggregated by geography."""
        geo = self.analytics_engine.get_geographic_distribution(limit=10)
        self.assertGreater(len(geo), 0)
        top_city = geo[0]
        self.assertIn("city", top_city)
        self.assertIn("country", top_city)
        self.assertGreater(top_city["customer_count"], 0)
        self.assertGreater(top_city["total_revenue"], 0.0)

    def test_rfm_scores_and_cohort_segmentation(self):
        """Verify RFM quintiles, segment assignments, and segment summaries."""
        rfm_data = self.segmentation_engine.compute_rfm_scores()
        self.assertGreater(rfm_data["total_customers_scored"], 800)
        self.assertIn("Champions", rfm_data["segment_summary"])
        self.assertIn("Loyal Customers", rfm_data["segment_summary"])

        champions_summary = rfm_data["segment_summary"]["Champions"]
        self.assertGreater(champions_summary["customer_count"], 0)
        self.assertGreater(champions_summary["total_revenue"], 0.0)
        self.assertIn("strategy", champions_summary)

        # Check customer RFM scores
        for c in rfm_data["customers"][:20]:
            self.assertIsInstance(c, RFMCustomerScore)
            self.assertTrue(1 <= c.r_score <= 5)
            self.assertTrue(1 <= c.f_score <= 5)
            self.assertTrue(1 <= c.m_score <= 5)
            self.assertEqual(len(c.rfm_score_str), 3)
            # PII masking
            self.assertTrue(c.display_name.split()[-1].endswith("."))

    def test_churn_risk_cohort(self):
        """Verify identification of high-value dormant customers at risk of churn."""
        churn_cohort = self.segmentation_engine.get_churn_risk_cohort(
            days_threshold=90,
            min_orders=2,
            limit=25
        )
        self.assertGreater(len(churn_cohort), 0)
        for cand in churn_cohort:
            self.assertIsInstance(cand, ChurnRiskCustomer)
            self.assertGreaterEqual(cand.days_since_last_order, 90)
            self.assertGreaterEqual(cand.orders_placed, 2)
            self.assertIn(cand.risk_level, ("Critical", "High", "Moderate"))
            self.assertGreater(cand.estimated_revenue_at_risk, 0.0)
            # PII masking
            self.assertTrue(cand.display_name.split()[-1].endswith("."))


if __name__ == "__main__":
    unittest.main()
