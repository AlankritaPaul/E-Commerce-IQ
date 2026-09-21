"""
Unit and Integration Tests for Professional BI Interface Components & Visualizations.

Verifies:
- Metric card HTML formatting and delta styling
- Interactive Plotly chart generation (Revenue Trends, Category Donut, Returns Bar, CSAT Distribution, Variance)
- Graceful handling of empty or missing chart data
- AI Insight and Briefing card rendering
- View rendering functions for Overview, Sales, Products, Customers, Reviews, Returns, Diagnosis, and Copilot
"""

from pathlib import Path
import sys
import unittest

_root = Path(__file__).resolve().parent.parent
for _p in (str(_root / "src"), str(_root)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import plotly.graph_objects as go
from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.ai.interpretation import AnalyticsInterpreter
from ecommerce_iq.models.schemas import AnalyticalInterpretation, KPISummary
from ui.components.cards import format_metric_card_html, render_kpi_grid, render_ai_insight_card
from ui.components.charts import (
    render_revenue_trend_chart,
    render_category_donut_chart,
    render_returns_bar_chart,
    render_rating_distribution_chart,
    render_variance_bar_chart,
)


class TestUICards(unittest.TestCase):
    """Test metric and briefing card component generation."""

    def test_format_metric_card_html_positive_delta(self):
        """Verify HTML formatting with positive delta styling."""
        html = format_metric_card_html(
            title="Net Revenue",
            value="$647,823.33",
            delta="+12.5%",
            subtitle="vs Previous Period"
        )
        self.assertIn("Net Revenue", html)
        self.assertIn("$647,823.33", html)
        self.assertIn("delta-positive", html)
        self.assertIn("▲ +12.5%", html)
        self.assertIn("vs Previous Period", html)

    def test_format_metric_card_html_negative_delta(self):
        """Verify HTML formatting with negative delta styling."""
        html = format_metric_card_html(
            title="Completed Orders",
            value="139",
            delta="-54.7%",
            subtitle="August Anomaly"
        )
        self.assertIn("Completed Orders", html)
        self.assertIn("139", html)
        self.assertIn("delta-negative", html)
        self.assertIn("▼ -54.7%", html)

    def test_kpi_grid_execution(self):
        """Verify render_kpi_grid executes cleanly with KPISummary."""
        kpis = KPISummary(
            total_revenue=10000.0,
            net_revenue=9500.0,
            total_orders=100,
            average_order_value=95.0,
            total_refunds=500.0,
            return_rate_percentage=5.0,
            active_customers=80,
            gross_margin_percentage=60.0
        )
        # Should execute without throwing exceptions in non-Streamlit/test context
        render_kpi_grid(kpis)

    def test_ai_insight_card_execution(self):
        """Verify render_ai_insight_card executes cleanly with AnalyticalInterpretation."""
        interp = AnalyticalInterpretation(
            title="Test Briefing",
            summary="All systems operational.",
            key_findings=["Revenue up 10%"],
            evidence_based_insights=["Strong organic growth"],
            actionable_recommendations=["Increase ad spend"],
            is_grounded=True
        )
        render_ai_insight_card(interp)


class TestUICharts(unittest.TestCase):
    """Test interactive Plotly visualization generation."""

    def test_revenue_trend_chart_generation(self):
        """Verify revenue trend chart generates dual-axis plotly figure."""
        sample_data = [
            {"month": "2025-01", "total_revenue": 50000.0, "total_orders": 300},
            {"month": "2025-02", "total_revenue": 55000.0, "total_orders": 320},
        ]
        fig = render_revenue_trend_chart(sample_data)
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 2)  # Bar + Scatter line
        self.assertEqual(fig.data[0].type, "bar")
        self.assertEqual(fig.data[1].type, "scatter")

    def test_category_donut_chart_generation(self):
        """Verify category share donut chart generates valid pie figure."""
        sample_data = [
            {"category_name": "Electronics", "gross_revenue": 120000.0},
            {"category_name": "Apparel", "gross_revenue": 45000.0},
        ]
        fig = render_category_donut_chart(sample_data)
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 1)
        self.assertEqual(fig.data[0].type, "pie")
        self.assertEqual(fig.data[0].hole, 0.55)

    def test_returns_bar_chart_generation(self):
        """Verify return reasons chart generates horizontal bar figure."""
        sample_data = [
            {"reason": "Defective", "incident_count": 80, "total_refund_amount": 15000.0},
            {"reason": "Changed Mind", "incident_count": 120, "total_refund_amount": 8000.0},
        ]
        fig = render_returns_bar_chart(sample_data)
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 1)
        self.assertEqual(fig.data[0].orientation, "h")

    def test_rating_distribution_chart_generation(self):
        """Verify CSAT rating distribution chart generates 5-bracket bar figure."""
        sample_data = [
            {"rating": 5, "review_count": 1200},
            {"rating": 4, "review_count": 400},
            {"rating": 3, "review_count": 50},
            {"rating": 2, "review_count": 100},
            {"rating": 1, "review_count": 300},
        ]
        fig = render_rating_distribution_chart(sample_data)
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 1)
        self.assertEqual(len(fig.data[0].x), 5)

    def test_variance_bar_chart_generation(self):
        """Verify diverging variance bar chart generation."""
        sample_data = [
            {"metric_name": "Revenue", "percentage_change": -61.03},
            {"metric_name": "Orders", "percentage_change": -54.72},
            {"metric_name": "AOV", "percentage_change": 12.50},
        ]
        fig = render_variance_bar_chart(sample_data)
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 1)
        self.assertEqual(fig.data[0].orientation, "h")

    def test_charts_handle_empty_data_gracefully(self):
        """Verify all chart renderers handle empty lists without crashing."""
        self.assertIsInstance(render_revenue_trend_chart([]), go.Figure)
        self.assertIsInstance(render_category_donut_chart([]), go.Figure)
        self.assertIsInstance(render_returns_bar_chart([]), go.Figure)
        self.assertIsInstance(render_rating_distribution_chart([]), go.Figure)
        self.assertIsInstance(render_variance_bar_chart([]), go.Figure)


class TestUIPages(unittest.TestCase):
    """Test dashboard view page execution with underlying database and engines."""

    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseManager()
        cls.interpreter = AnalyticsInterpreter()

    def test_sales_view_execution(self):
        """Verify sales_view renders without exceptions."""
        from ui.pages.sales_view import render_sales_page
        render_sales_page(self.db, self.interpreter)

    def test_products_view_execution(self):
        """Verify products_view renders without exceptions."""
        from ui.pages.products_view import render_products_page
        render_products_page(self.db, self.interpreter)

    def test_customers_view_execution(self):
        """Verify customers_view renders without exceptions."""
        from ui.pages.customers_view import render_customers_page
        render_customers_page(self.db, self.interpreter)

    def test_reviews_view_execution(self):
        """Verify reviews_view renders without exceptions."""
        from ui.pages.reviews_view import render_reviews_page
        render_reviews_page(self.db, self.interpreter)

    def test_returns_view_execution(self):
        """Verify returns_view renders without exceptions."""
        from ui.pages.returns_view import render_returns_page
        render_returns_page(self.db, self.interpreter)

    def test_diagnosis_view_execution(self):
        """Verify diagnosis_view renders without exceptions."""
        from ui.pages.diagnosis_view import render_diagnosis_page
        render_diagnosis_page(self.db, self.interpreter)

    def test_foundation_view_execution(self):
        """Verify foundation_view renders without exceptions."""
        from ui.pages.foundation_view import render_foundation_page
        render_foundation_page(self.db)

    def test_dataset_view_execution(self):
        """Verify dataset_view renders without exceptions."""
        from ui.pages.dataset_view import render_dataset_page
        render_dataset_page(self.db)

    def test_interpretation_view_execution(self):
        """Verify interpretation_view renders without exceptions."""
        from ui.pages.interpretation_view import render_interpretation_page
        render_interpretation_page(self.db, self.interpreter)


if __name__ == "__main__":
    unittest.main()
