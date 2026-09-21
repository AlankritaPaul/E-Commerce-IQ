"""
Unit and Integration Tests for AI Interpretation Layer and Anti-Hallucination Grounding.

Verifies:
- NumericalGroundingVerifier text number extraction and verification algorithms
- Detection and interception of hallucinated/unverified numerical claims
- AnalyticsInterpreter domain explanations:
  * KPI scorecards
  * Period-over-Period comparisons
  * Product performance and catalog economics
  * Customer behavioral dynamics and churn cohorts
  * Customer response and review sentiment
  * Returns velocity and refund leakage
  * Root-cause performance diagnosis reports
- Polymorphic universal interpretation dispatcher
- 100% evidence grounding across all generated narratives
"""

from datetime import date
from pathlib import Path
import sys
import unittest

_root = Path(__file__).resolve().parent.parent
for _p in (str(_root / "src"), str(_root)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ecommerce_iq.ai.interpretation import AnalyticsInterpreter, NumericalGroundingVerifier
from ecommerce_iq.business_logic.diagnosis import BusinessPerformanceDiagnostic
from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.models.schemas import (
    AnalyticalInterpretation,
    ChurnRiskCustomer,
    CustomerAggregateSummary,
    DiagnosticReport,
    EvidenceCitation,
    KPISummary,
    PeriodComparisonResult,
    ProductPerformanceMetric,
    ProductReturnMetric,
    ReturnReasonMetric,
    ReturnsOverallSummary,
    ReviewSentimentSummary,
    ThemeCluster,
)


class TestNumericalGroundingVerifier(unittest.TestCase):
    """Test number extraction and anti-hallucination verification."""

    def setUp(self):
        self.verifier = NumericalGroundingVerifier()

    def test_extract_numbers_from_text(self):
        """Verify extraction of currencies, percentages, and formatted integers."""
        sample_text = (
            "In August 2025, net revenue plunged by -$56,904.60 (-61.03%) from $93,242.08 to $36,337.48. "
            "Total orders dropped by 54.7% across 139 orders, with an average rating of 4.10 stars."
        )
        extracted = self.verifier.extract_numbers_from_text(sample_text)
        nums = [item[0] for item in extracted]

        self.assertIn(-56904.60, nums)
        self.assertIn(93242.08, nums)
        self.assertIn(36337.48, nums)
        self.assertIn(-61.03, nums)
        self.assertIn(54.7, nums)
        self.assertIn(139.0, nums)
        self.assertIn(4.10, nums)

    def test_detection_of_unverified_hallucinated_figures(self):
        """Verify that invented or unsupported numbers are caught by the verifier."""
        kpis = KPISummary(
            total_revenue=10000.0,
            net_revenue=9500.0,
            total_orders=100,
            average_order_value=95.0,
            total_refunds=500.0,
            return_rate_percentage=5.0,
            active_customers=80
        )

        # Interpretation with fabricated numbers ($999,999.00 and 88.88%)
        hallucinated_interp = AnalyticalInterpretation(
            title="Fabricated Interpretation",
            summary="We made $999,999.00 in sales with an extraordinary 88.88% growth rate.",
            key_findings=["Invented figure of $500,000.00."],
            evidence_based_insights=["Everything is fabricated."],
            actionable_recommendations=["Stop hallucinating."]
        )

        is_grounded, unverified = self.verifier.verify(hallucinated_interp, kpis)
        self.assertFalse(is_grounded)
        self.assertGreaterEqual(len(unverified), 2)
        self.assertTrue(any("999,999" in u for u in unverified))
        self.assertTrue(any("88.88" in u for u in unverified))


class TestAnalyticsInterpreter(unittest.TestCase):
    """Test AI interpretation layer across all analytical data domains."""

    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseManager()
        cls.interpreter = AnalyticsInterpreter()

    def test_interpret_kpis(self):
        """Verify interpretation of high-level KPI scorecard."""
        kpis = KPISummary(
            total_revenue=688960.83,
            net_revenue=647823.33,
            total_orders=4061,
            average_order_value=169.65,
            total_refunds=41137.50,
            return_rate_percentage=4.76,
            active_customers=832,
            gross_margin_percentage=62.5
        )

        interp = self.interpreter.interpret_kpis(kpis)
        self.assertIsInstance(interp, AnalyticalInterpretation)
        self.assertTrue(interp.is_grounded, f"Ungrounded claims: {interp.unverified_claims}")
        self.assertIn("$647,823.33", interp.summary)
        self.assertIn("4,061", interp.summary)
        self.assertIn("$169.65", interp.summary)
        self.assertIn("832", interp.summary)
        self.assertGreaterEqual(len(interp.key_findings), 4)
        self.assertGreaterEqual(len(interp.evidence_citations), 4)

    def test_interpret_period_comparison(self):
        """Verify interpretation of period variance analysis."""
        comparisons = [
            PeriodComparisonResult(
                metric_name="Net Revenue",
                current_value=36337.48,
                previous_value=93242.08,
                absolute_change=-56904.60,
                percentage_change=-61.03,
                trend_direction="negative"
            ),
            PeriodComparisonResult(
                metric_name="Completed Orders",
                current_value=139.0,
                previous_value=307.0,
                absolute_change=-168.0,
                percentage_change=-54.72,
                trend_direction="negative"
            ),
            PeriodComparisonResult(
                metric_name="Average Order Value",
                current_value=272.13,
                previous_value=317.27,
                absolute_change=-45.14,
                percentage_change=-14.23,
                trend_direction="negative"
            ),
        ]

        interp = self.interpreter.interpret_period_comparison(comparisons, period_label="August 2025 MoM")
        self.assertTrue(interp.is_grounded, f"Ungrounded claims: {interp.unverified_claims}")
        self.assertIn("contracted", interp.summary.lower())
        self.assertIn("-61.03%", interp.summary)
        self.assertIn("-$56,904.60", interp.summary)
        self.assertEqual(len(interp.evidence_citations), 3)

    def test_interpret_product_performance(self):
        """Verify interpretation of catalog SKU economics."""
        products = [
            ProductPerformanceMetric(
                product_id=1,
                sku="PROD-ELEC-001",
                title="AuraSound ANC Headphones",
                category_name="Electronics",
                units_sold=450,
                total_revenue=89955.00,
                total_returns=119,
                return_rate_pct=26.44,
                avg_rating=3.65
            ),
            ProductPerformanceMetric(
                product_id=2,
                sku="PROD-ELEC-002",
                title="Smart Watch Ultra",
                category_name="Electronics",
                units_sold=220,
                total_revenue=43978.00,
                total_returns=10,
                return_rate_pct=4.55,
                avg_rating=4.40
            ),
        ]

        interp = self.interpreter.interpret_product_performance(products)
        self.assertTrue(interp.is_grounded, f"Ungrounded claims: {interp.unverified_claims}")
        self.assertIn("AuraSound ANC Headphones", interp.summary)
        self.assertIn("$89,955.00", interp.summary)
        self.assertIn("450", interp.summary)
        self.assertGreaterEqual(len(interp.key_findings), 2)

    def test_interpret_customer_behavior(self):
        """Verify interpretation of customer retention and churn dynamics."""
        summary = CustomerAggregateSummary(
            total_registered_customers=850,
            active_purchasers=832,
            repeat_customers=805,
            one_time_buyers=27,
            repeat_purchase_rate_pct=96.75,
            average_customer_ltv=778.63,
            average_order_frequency=4.60,
            customer_return_rate_pct=25.48,
            review_participation_rate_pct=52.30
        )
        churn_cohort = [
            ChurnRiskCustomer(
                customer_id=101,
                display_name="David M.",
                city="Chicago",
                country="USA",
                segment="High Value",
                orders_placed=5,
                total_spend=1250.00,
                average_order_value=250.00,
                days_since_last_order=95,
                risk_level="High",
                estimated_revenue_at_risk=1250.00
            )
        ]

        interp = self.interpreter.interpret_customer_behavior(summary, churn_risks=churn_cohort)
        self.assertTrue(interp.is_grounded, f"Ungrounded claims: {interp.unverified_claims}")
        self.assertIn("96.75%", interp.summary)
        self.assertIn("$778.63", interp.summary)
        self.assertIn("805", interp.summary)
        self.assertIn("Churn Risk Cohort", interp.key_findings[-1])

    def test_interpret_customer_reviews(self):
        """Verify interpretation of customer sentiment and complaints."""
        summary = ReviewSentimentSummary(
            total_reviews=2067,
            average_rating=4.10,
            positive_count=1605,
            neutral_count=13,
            negative_count=449,
            positive_percentage=77.65,
            negative_percentage=21.72,
            top_complaints=["Battery dies quickly", "Packaging damaged"],
            top_praises=["Great build quality", "Fast shipping"]
        )
        issues = [
            ThemeCluster(
                theme_title="Battery failure / cuts out",
                topic="Hardware",
                review_count=85,
                percentage_of_reviews=4.11,
                severity_or_sentiment="Critical"
            )
        ]

        interp = self.interpreter.interpret_customer_reviews(summary, recurring_issues=issues)
        self.assertTrue(interp.is_grounded, f"Ungrounded claims: {interp.unverified_claims}")
        self.assertIn("4.10 / 5.0 stars", interp.summary)
        self.assertIn("77.65%", interp.summary)
        self.assertIn("1,605", interp.summary)
        self.assertTrue(any("Battery dies quickly" in f for f in interp.key_findings))

    def test_interpret_returns(self):
        """Verify interpretation of platform returns and refund costs."""
        summary = ReturnsOverallSummary(
            total_return_events=286,
            total_units_returned=332,
            total_refund_amount=41137.50,
            platform_return_rate_pct=4.76,
            refund_ratio_pct=6.66,
            high_risk_products_count=2,
            top_return_reasons=[
                ReturnReasonMetric(
                    reason="Defective / Damaged",
                    incident_count=81,
                    total_refund_amount=16135.00,
                    percentage_of_all_returns=28.32
                )
            ]
        )

        interp = self.interpreter.interpret_returns(summary)
        self.assertTrue(interp.is_grounded, f"Ungrounded claims: {interp.unverified_claims}")
        self.assertIn("$41,137.50", interp.summary)
        self.assertIn("4.76%", interp.summary)
        self.assertIn("286", interp.summary)

    def test_interpret_diagnostic_end_to_end(self):
        """Verify interpretation of live empirical diagnosis report (August 2025 drop)."""
        diag = BusinessPerformanceDiagnostic(self.db)
        report = diag.diagnose_month_over_month(2025, 8)

        interp = self.interpreter.interpret_diagnostic(report)
        self.assertTrue(interp.is_grounded, f"Ungrounded claims: {interp.unverified_claims}")
        self.assertEqual(interp.source_analytics_type, "DiagnosticReport")
        self.assertIn("Critical Severity", interp.summary)
        self.assertIn("-61.03%", interp.summary)
        self.assertIn("Primary Declining SKU", interp.key_findings[-1])
        self.assertGreaterEqual(len(interp.evidence_citations), 3)

    def test_polymorphic_dispatcher(self):
        """Verify that the universal interpret() method routes each data type accurately."""
        kpis = KPISummary(100.0, 90.0, 1, 90.0, 10.0, 1.0, 1)
        interp1 = self.interpreter.interpret(kpis)
        self.assertEqual(interp1.source_analytics_type, "KPISummary")

        returns_sum = ReturnsOverallSummary(10, 10, 500.0, 5.0, 5.0, 0)
        interp2 = self.interpreter.interpret(returns_sum)
        self.assertEqual(interp2.source_analytics_type, "ReturnsOverallSummary")

        reviews_sum = ReviewSentimentSummary(100, 4.5, 90, 5, 5, 90.0, 5.0)
        interp3 = self.interpreter.interpret(reviews_sum)
        self.assertEqual(interp3.source_analytics_type, "ReviewSentimentSummary")


if __name__ == "__main__":
    unittest.main()
