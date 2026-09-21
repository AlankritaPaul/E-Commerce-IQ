"""
Unit and Integration Tests for Business Performance Decline Diagnosis.

Verifies:
- BusinessPerformanceDiagnostic multi-factor empirical investigation
- Month-over-month decline diagnosis (August 2025 anomaly vs July 2025 baseline)
- Quantitative MetricEvidence generation and significance rankings
- Product-level decline attribution (identifying AuraSound Headphones and Bestsellers)
- Customer review sentiment signals and defect complaints integration
- Automated anomaly detection scanner across operational history
- Growth period diagnosis handling (e.g. Q4 holiday surge)
"""

from datetime import date
from pathlib import Path
import sys
import unittest

_root = Path(__file__).resolve().parent.parent
for _p in (str(_root / "src"), str(_root)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ecommerce_iq.business_logic.diagnosis import BusinessPerformanceDiagnostic
from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.models.schemas import (
    DiagnosticReport,
    MetricEvidence,
    ProductDeclineFactor,
)


class TestBusinessDiagnosis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseManager()
        cls.diagnostic = BusinessPerformanceDiagnostic(cls.db)

    def test_august_2025_decline_diagnosis(self):
        """Verify empirical diagnosis of the August 2025 revenue collapse."""
        report = self.diagnostic.diagnose_month_over_month(2025, 8)
        self.assertIsInstance(report, DiagnosticReport)
        self.assertEqual(report.severity, "Critical")
        self.assertLess(report.net_revenue_change, -20000.0)
        self.assertLess(report.net_revenue_change_pct, -50.0)
        self.assertIn("contracted", report.primary_finding.lower())
        self.assertIn("order volume", report.primary_finding.lower())

    def test_metric_evidences_integrity(self):
        """Verify all macro evidences have complete metrics, deltas, and impact rankings."""
        report = self.diagnostic.diagnose_month_over_month(2025, 8)
        self.assertEqual(len(report.metric_evidences), 8)

        metric_names = [m.metric_name for m in report.metric_evidences]
        self.assertIn("Net Revenue", metric_names)
        self.assertIn("Total Completed Orders", metric_names)
        self.assertIn("Total Units Sold", metric_names)
        self.assertIn("Average Order Value (AOV)", metric_names)
        self.assertIn("Gross Profit", metric_names)
        self.assertIn("Return Rate", metric_names)

        # Check Net Revenue evidence details
        rev_ev = next(m for m in report.metric_evidences if m.metric_name == "Net Revenue")
        self.assertEqual(rev_ev.significance, "Major Driver")
        self.assertEqual(rev_ev.impact_direction, "Negative")
        self.assertLess(rev_ev.percentage_change, -50.0)

    def test_product_level_decline_attribution(self):
        """Verify top declining products are identified with negative revenue variance."""
        report = self.diagnostic.diagnose_month_over_month(2025, 8)
        self.assertGreater(len(report.top_declining_products), 0)

        # Check top drag items
        skus = [p.sku for p in report.top_declining_products]
        self.assertIn("PROD-ELEC-001", skus)
        self.assertIn("PROD-ELEC-003", skus)

        for prod in report.top_declining_products:
            self.assertIsInstance(prod, ProductDeclineFactor)
            self.assertLess(prod.revenue_loss, 0.0)
            self.assertLess(prod.percentage_change, 0.0)
            self.assertIn(prod.primary_driver_type, ("Volume Drop", "Quality/Return Defect", "Pricing/AOV Shift"))

    def test_customer_review_signals_integration(self):
        """Verify qualitative review feedback signals corroborate quantitative decline."""
        report = self.diagnostic.diagnose_month_over_month(2025, 8)
        self.assertGreater(len(report.customer_feedback_signals), 0)

        # Confirm review signals cite negative reviews or CSAT changes
        signals_text = " ".join(report.customer_feedback_signals)
        self.assertTrue("review" in signals_text.lower() or "rating" in signals_text.lower())

    def test_contributing_factors_and_actions(self):
        """Verify contributing factors cite empirical numbers and recommend actionable steps."""
        report = self.diagnostic.diagnose_month_over_month(2025, 8)
        self.assertGreaterEqual(len(report.contributing_factors), 3)
        self.assertGreaterEqual(len(report.recommended_actions), 2)

        # Every contributing factor must contain empirical numerical evidence (% or $)
        for factor in report.contributing_factors:
            self.assertTrue("%" in factor or "$" in factor)

    def test_custom_period_diagnosis(self):
        """Verify diagnosis works with arbitrary custom date ranges."""
        report = self.diagnostic.diagnose_revenue_decline(
            current_start=date(2025, 8, 1),
            current_end=date(2025, 8, 31),
            baseline_start=date(2025, 7, 1),
            baseline_end=date(2025, 7, 31)
        )
        self.assertEqual(report.severity, "Critical")
        self.assertLess(report.net_revenue_change_pct, -50.0)

    def test_growth_period_diagnosis(self):
        """Verify diagnosis on a positive revenue period correctly identifies expansion."""
        # Compare December 2025 (holiday surge) vs November 2025
        report = self.diagnostic.diagnose_month_over_month(2025, 12)
        self.assertIsInstance(report, DiagnosticReport)
        self.assertEqual(report.severity, "Informational")
        self.assertGreater(report.net_revenue_change, 0.0)
        self.assertIn("increased", report.primary_finding.lower())

    def test_anomaly_detection_scanner(self):
        """Verify automated anomaly scanner detects the August 2025 revenue collapse."""
        anomalies = self.diagnostic.detect_anomalies(lookback_months=14)
        self.assertGreater(len(anomalies), 0)

        # Confirm 2025-08 is flagged
        aug_anomaly = next((a for a in anomalies if a["period"] == "2025-08"), None)
        self.assertIsNotNone(aug_anomaly)
        self.assertEqual(aug_anomaly["anomaly_type"], "Revenue Contraction")
        self.assertEqual(aug_anomaly["severity"], "Critical")
        self.assertLess(aug_anomaly["percentage_change"], -50.0)


if __name__ == "__main__":
    unittest.main()
