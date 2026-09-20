import sys
from pathlib import Path
import unittest

_root = Path(__file__).resolve().parent.parent
for _p in (str(_root / "src"), str(_root)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ecommerce_iq.models.entities import (
    Category,
    Customer,
    Order,
    OrderItem,
    Payment,
    Product,
    Return,
    ReturnAndRefund,
    Review,
    ReviewInsight,
    Sale,
)
from ecommerce_iq.models.schemas import (
    AIQueryResponse,
    DiagnosticReport,
    KPISummary,
    PeriodComparisonResult,
    ProductPerformanceMetric,
    RecommendationItem,
    ReturnReasonMetric,
    ReviewSentimentSummary,
)


class TestModelsAndEntities(unittest.TestCase):
    def test_entity_table_names(self):
        """Verify ORM entities define the expected database table names."""
        self.assertEqual(Customer.__tablename__, "customers")
        self.assertEqual(Category.__tablename__, "categories")
        self.assertEqual(Product.__tablename__, "products")
        self.assertEqual(Order.__tablename__, "orders")
        self.assertEqual(OrderItem.__tablename__, "order_items")
        self.assertEqual(Payment.__tablename__, "payments")
        self.assertEqual(Return.__tablename__, "returns")
        self.assertEqual(ReturnAndRefund.__tablename__, "returns")
        self.assertEqual(Review.__tablename__, "reviews")
        self.assertEqual(ReviewInsight.__tablename__, "review_insights")
        self.assertEqual(Sale.__tablename__, "sales")

    def test_kpi_summary_schema(self):
        """Verify that KPISummary dataclass initializes correctly."""
        kpi = KPISummary(
            total_revenue=10000.0,
            net_revenue=9200.0,
            total_orders=150,
            average_order_value=66.67,
            total_refunds=800.0,
            return_rate_percentage=5.3,
            active_customers=120,
            gross_margin_percentage=42.5
        )
        self.assertEqual(kpi.total_revenue, 10000.0)
        self.assertEqual(kpi.total_orders, 150)
        self.assertEqual(kpi.return_rate_percentage, 5.3)
        self.assertEqual(kpi.gross_margin_percentage, 42.5)

    def test_diagnostic_and_recommendation_schemas(self):
        """Verify DiagnosticReport and RecommendationItem schemas."""
        diag = DiagnosticReport(
            title="Revenue Drop Diagnosis",
            period_analyzed="August 2025 vs July 2025",
            primary_finding="18% drop in Electronics category revenue",
            contributing_factors=["Spike in returns for SKU-104", "Negative reviews mentioning zipper defects"],
            recommended_actions=["Halt fulfillment of SKU-104 batch B", "Issue proactive refunds"]
        )
        self.assertEqual(len(diag.contributing_factors), 2)

        rec = RecommendationItem(
            priority="High",
            category="Quality",
            title="Supplier Escalation",
            action="Contact vendor regarding zipper quality",
            expected_impact="Reduce return rate by 8%"
        )
        self.assertEqual(rec.priority, "High")


if __name__ == "__main__":
    unittest.main()
