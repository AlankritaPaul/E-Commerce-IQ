"""
Core KPI and Revenue Calculation Engine.

Computes exact financial and operational metrics directly from the SQL database:
- Total Gross & Net Revenue
- Total Completed Orders & Order Status Breakdown
- Average Order Value (AOV)
- Revenue Aggregated by Day, Week, and Month (Time-Series)
- Return Rates & Financial Refund Totals
- Gross Margin Percentages
"""

from datetime import date
from typing import Any, Dict, List, Optional
from ecommerce_iq.analytics.base import BaseAnalyticsEngine
from ecommerce_iq.models.schemas import KPISummary


class KPICalculator(BaseAnalyticsEngine):
    """
    Executes deterministic SQL queries to calculate business metrics.
    Guarantees mathematically exact outputs directly from the database.
    """

    def calculate_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> KPISummary:
        """
        Compute high-level executive KPI scorecard metrics for the specified date range.
        """
        date_filter_orders = self._format_date_filter("o.order_date", start_date, end_date)
        date_filter_returns = self._format_date_filter("r.return_date", start_date, end_date)
        date_filter_sales = self._format_date_filter("s.sale_date", start_date, end_date)

        # 1. Order-level metrics
        order_query = f"""
            SELECT 
                COUNT(DISTINCT o.order_id) AS total_orders,
                COUNT(DISTINCT o.customer_id) AS active_customers,
                COALESCE(SUM(o.subtotal), 0.0) AS gross_sales,
                COALESCE(SUM(o.discount_amount), 0.0) AS total_discounts,
                COALESCE(SUM(o.total_amount), 0.0) AS net_revenue
            FROM orders o
            WHERE o.status = 'completed' {date_filter_orders};
        """
        order_row = self.execute_query(order_query)[0]
        total_orders = order_row["total_orders"] or 0
        active_customers = order_row["active_customers"] or 0
        gross_sales = float(order_row["gross_sales"] or 0.0)
        net_revenue = float(order_row["net_revenue"] or 0.0)
        aov = round(self.safe_divide(net_revenue, total_orders), 2)

        # 2. Return and refund metrics
        return_query = f"""
            SELECT 
                COALESCE(SUM(r.refund_amount), 0.0) AS total_refunds,
                COALESCE(SUM(r.quantity_returned), 0) AS total_units_returned
            FROM returns r
            WHERE 1=1 {date_filter_returns};
        """
        return_row = self.execute_query(return_query)[0]
        total_refunds = float(return_row["total_refunds"] or 0.0)
        total_units_returned = return_row["total_units_returned"] or 0

        # 3. Total units sold & gross margin from sales ledger
        sales_query = f"""
            SELECT 
                COALESCE(SUM(s.quantity), 0) AS total_units_sold,
                COALESCE(SUM(s.net_revenue), 0.0) AS sales_net_rev,
                COALESCE(SUM(s.gross_profit), 0.0) AS total_gross_profit
            FROM sales s
            WHERE 1=1 {date_filter_sales};
        """
        sales_row = self.execute_query(sales_query)[0]
        total_units_sold = sales_row["total_units_sold"] or 0
        total_gross_profit = float(sales_row["total_gross_profit"] or 0.0)
        sales_net = float(sales_row["sales_net_rev"] or 0.0)

        # Return rate percentage: (units_returned / units_sold) * 100
        return_rate_pct = round(
            self.safe_divide(float(total_units_returned), float(total_units_sold)) * 100.0, 2
        )

        # Gross margin percentage: (gross_profit / net_revenue) * 100
        gross_margin_pct = round(
            self.safe_divide(total_gross_profit, sales_net) * 100.0, 2
        )

        return KPISummary(
            total_revenue=round(gross_sales, 2),
            net_revenue=round(net_revenue, 2),
            total_orders=total_orders,
            average_order_value=aov,
            total_refunds=round(total_refunds, 2),
            return_rate_percentage=return_rate_pct,
            active_customers=active_customers,
            gross_margin_percentage=gross_margin_pct
        )

    def calculate_revenue(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        net: bool = True
    ) -> float:
        """
        Calculate total revenue (net or gross) for completed orders.
        """
        col = "total_amount" if net else "subtotal"
        date_filter = self._format_date_filter("order_date", start_date, end_date)
        query = f"""
            SELECT COALESCE(SUM({col}), 0.0) AS revenue
            FROM orders
            WHERE status = 'completed' {date_filter};
        """
        rows = self.execute_query(query)
        return round(float(rows[0]["revenue"] or 0.0), 2)

    def calculate_order_count(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = "completed"
    ) -> int:
        """
        Count orders matching date range and optional status filter.
        """
        date_filter = self._format_date_filter("order_date", start_date, end_date)
        status_clause = f"AND status = '{status}'" if status else ""
        query = f"""
            SELECT COUNT(DISTINCT order_id) AS total_orders
            FROM orders
            WHERE 1=1 {status_clause} {date_filter};
        """
        rows = self.execute_query(query)
        return int(rows[0]["total_orders"] or 0)

    def calculate_aov(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> float:
        """
        Calculate Average Order Value (Net Revenue / Completed Orders).
        """
        date_filter = self._format_date_filter("order_date", start_date, end_date)
        query = f"""
            SELECT 
                COUNT(DISTINCT order_id) AS orders,
                SUM(total_amount) AS rev
            FROM orders
            WHERE status = 'completed' {date_filter};
        """
        row = self.execute_query(query)[0]
        orders = row["orders"] or 0
        rev = float(row["rev"] or 0.0)
        return round(self.safe_divide(rev, orders), 2)

    def get_revenue_time_series(
        self,
        granularity: str = "monthly",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Aggregate revenue, order volume, discounts, and AOV over temporal buckets.

        Args:
            granularity: One of 'daily', 'weekly', 'monthly'.
            start_date: Inclusive lower date bound.
            end_date: Inclusive upper date bound.

        Returns:
            List of dictionary records sorted chronologically.
        """
        if granularity == "daily":
            period_expr = "DATE(order_date)"
        elif granularity == "weekly":
            period_expr = "strftime('%Y-W%W', order_date)"
        else:  # monthly
            period_expr = "strftime('%Y-%m', order_date)"

        date_filter = self._format_date_filter("order_date", start_date, end_date)

        query = f"""
            SELECT 
                {period_expr} AS period,
                COUNT(DISTINCT order_id) AS order_count,
                COUNT(DISTINCT customer_id) AS active_customers,
                ROUND(COALESCE(SUM(subtotal), 0.0), 2) AS gross_revenue,
                ROUND(COALESCE(SUM(discount_amount), 0.0), 2) AS discount_amount,
                ROUND(COALESCE(SUM(total_amount), 0.0), 2) AS net_revenue,
                ROUND(AVG(total_amount), 2) AS average_order_value
            FROM orders
            WHERE status = 'completed' {date_filter}
            GROUP BY 1
            ORDER BY 1 ASC;
        """
        return self.execute_query(query)

    def get_revenue_by_day(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Convenience method for daily revenue time-series."""
        return self.get_revenue_time_series(granularity="daily", start_date=start_date, end_date=end_date)

    def get_revenue_by_week(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Convenience method for weekly revenue time-series."""
        return self.get_revenue_time_series(granularity="weekly", start_date=start_date, end_date=end_date)

    def get_revenue_by_month(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Convenience method for monthly revenue time-series."""
        return self.get_revenue_time_series(granularity="monthly", start_date=start_date, end_date=end_date)

    def get_order_status_breakdown(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, int]:
        """
        Return counts of orders grouped by status (completed, cancelled, refunded, pending).
        """
        date_filter = self._format_date_filter("order_date", start_date, end_date)
        query = f"""
            SELECT status, COUNT(*) AS count
            FROM orders
            WHERE 1=1 {date_filter}
            GROUP BY status;
        """
        rows = self.execute_query(query)
        return {r["status"]: r["count"] for r in rows}
