"""
Temporal Period-over-Period Comparison Engine.

Calculates exact variances, percentage growth/decline, and directional trends
directly from the database across:
- Month-over-Month (MoM)
- Week-over-Week (WoW)
- Year-over-Year (YoY)
- Custom Date Range Comparisons
"""

import calendar
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from ecommerce_iq.analytics.base import BaseAnalyticsEngine
from ecommerce_iq.models.schemas import PeriodComparisonResult


class PeriodComparisonEngine(BaseAnalyticsEngine):
    """
    Executes comparative SQL queries to evaluate performance variances across periods.
    """

    def _get_metrics_for_period(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, float]:
        """
        Query core analytical metrics for an explicit date interval.
        """
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d 23:59:59")

        # 1. Orders and Net Revenue
        order_query = f"""
            SELECT 
                COUNT(DISTINCT order_id) AS order_count,
                COALESCE(SUM(total_amount), 0.0) AS net_revenue
            FROM orders
            WHERE status = 'completed'
              AND order_date >= '{start_str}'
              AND order_date <= '{end_str}';
        """
        order_row = self.execute_query(order_query)[0]
        order_count = float(order_row["order_count"] or 0.0)
        net_revenue = float(order_row["net_revenue"] or 0.0)
        aov = self.safe_divide(net_revenue, order_count)

        # 2. Units Sold and Gross Profit from Sales Ledger
        sales_query = f"""
            SELECT 
                COALESCE(SUM(quantity), 0) AS units_sold,
                COALESCE(SUM(gross_profit), 0.0) AS gross_profit
            FROM sales
            WHERE sale_date >= '{start_date.strftime("%Y-%m-%d")}'
              AND sale_date <= '{end_date.strftime("%Y-%m-%d")}';
        """
        sales_row = self.execute_query(sales_query)[0]
        units_sold = float(sales_row["units_sold"] or 0.0)
        gross_profit = float(sales_row["gross_profit"] or 0.0)

        # 3. Total Refunds
        returns_query = f"""
            SELECT COALESCE(SUM(refund_amount), 0.0) AS total_refunds
            FROM returns
            WHERE return_date >= '{start_str}'
              AND return_date <= '{end_str}';
        """
        returns_row = self.execute_query(returns_query)[0]
        total_refunds = float(returns_row["total_refunds"] or 0.0)

        return {
            "net_revenue": round(net_revenue, 2),
            "order_count": order_count,
            "average_order_value": round(aov, 2),
            "units_sold": units_sold,
            "gross_profit": round(gross_profit, 2),
            "total_refunds": round(total_refunds, 2),
        }

    def compare_custom_periods(
        self,
        current_start: date,
        current_end: date,
        previous_start: date,
        previous_end: date
    ) -> List[PeriodComparisonResult]:
        """
        Compare performance between two arbitrary date ranges.

        Returns:
            List of PeriodComparisonResult records for all core business metrics.
        """
        curr = self._get_metrics_for_period(current_start, current_end)
        prev = self._get_metrics_for_period(previous_start, previous_end)

        metric_display_names = {
            "net_revenue": "Net Revenue ($)",
            "order_count": "Total Completed Orders",
            "average_order_value": "Average Order Value ($)",
            "units_sold": "Total Units Sold",
            "gross_profit": "Gross Profit ($)",
            "total_refunds": "Total Refunds Issued ($)",
        }

        results: List[PeriodComparisonResult] = []

        for key, display_name in metric_display_names.items():
            current_val = curr[key]
            previous_val = prev[key]
            abs_change = round(current_val - previous_val, 2)
            pct_change, trend = self.calculate_growth_rate(current_val, previous_val)

            # For refunds, an increase is negative for business performance
            if key == "total_refunds":
                if abs_change > 0:
                    trend = "negative"
                elif abs_change < 0:
                    trend = "positive"

            results.append(
                PeriodComparisonResult(
                    metric_name=display_name,
                    current_value=current_val,
                    previous_value=previous_val,
                    absolute_change=abs_change,
                    percentage_change=pct_change,
                    trend_direction=trend,
                )
            )

        return results

    def compare_month_over_month(
        self,
        target_year: int,
        target_month: int
    ) -> List[PeriodComparisonResult]:
        """
        Compare performance of target month against the immediate preceding calendar month.
        Example: target_year=2025, target_month=8 compares August 2025 vs July 2025.
        """
        # Current month date bounds
        curr_days = calendar.monthrange(target_year, target_month)[1]
        curr_start = date(target_year, target_month, 1)
        curr_end = date(target_year, target_month, curr_days)

        # Prior month date bounds
        if target_month == 1:
            prev_year = target_year - 1
            prev_month = 12
        else:
            prev_year = target_year
            prev_month = target_month - 1

        prev_days = calendar.monthrange(prev_year, prev_month)[1]
        prev_start = date(prev_year, prev_month, 1)
        prev_end = date(prev_year, prev_month, prev_days)

        return self.compare_custom_periods(
            current_start=curr_start,
            current_end=curr_end,
            previous_start=prev_start,
            previous_end=prev_end
        )

    def compare_week_over_week(
        self,
        target_year: int,
        target_week: int
    ) -> List[PeriodComparisonResult]:
        """
        Compare performance of target ISO week against the prior week.
        """
        # Target week bounds
        curr_start = date.fromisocalendar(target_year, target_week, 1)
        curr_end = date.fromisocalendar(target_year, target_week, 7)

        # Previous week bounds
        prev_start = curr_start - timedelta(days=7)
        prev_end = curr_end - timedelta(days=7)

        return self.compare_custom_periods(
            current_start=curr_start,
            current_end=curr_end,
            previous_start=prev_start,
            previous_end=prev_end
        )
