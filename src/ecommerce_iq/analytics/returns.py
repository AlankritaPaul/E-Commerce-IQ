"""
Returns, Refunds, and Financial Leakage Analytics Engine.

Analyzes product-level return rates, refund financial leakage, return reasons,
and temporal trends, while triangulating findings with sales volume and
customer review sentiment data for root cause diagnosis.
"""

from datetime import date
from typing import Any, Dict, List, Optional
from ecommerce_iq.analytics.base import BaseAnalyticsEngine
from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.models.schemas import (
    CategoryReturnMetric,
    ConnectedReturnInsight,
    ProductReturnMetric,
    ReturnReasonMetric,
    ReturnsOverallSummary,
)


class ReturnsAnalyticsEngine(BaseAnalyticsEngine):
    """
    Computes return ratios, refund totals, category benchmarks,
    and triangulated root cause diagnostics.
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None) -> None:
        super().__init__(db_manager)

    def get_overall_return_rate(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> float:
        """
        Calculate the platform-wide return rate percentage:
        (total_units_returned / total_units_sold) * 100.
        """
        date_filter_returns = self._format_date_filter("r.return_date", start_date, end_date)
        date_filter_orders = self._format_date_filter("o.order_date", start_date, end_date)

        sold_query = f"""
            SELECT COALESCE(SUM(oi.quantity), 0) AS total_sold
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.status = 'completed' {date_filter_orders};
        """
        sold_units = int(self.execute_query(sold_query)[0]["total_sold"] or 0)

        ret_query = f"""
            SELECT COALESCE(SUM(r.quantity_returned), 0) AS total_returned
            FROM returns r
            WHERE 1=1 {date_filter_returns};
        """
        returned_units = int(self.execute_query(ret_query)[0]["total_returned"] or 0)

        return round(self.safe_divide(float(returned_units), float(sold_units)) * 100.0, 2)

    def get_return_reasons_breakdown(
        self,
        product_id: Optional[int] = None,
        category_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[ReturnReasonMetric]:
        """
        Categorize returned items by customer return reasons with refund amounts.
        """
        where_clauses = ["1=1"]
        if product_id:
            where_clauses.append(f"r.product_id = {product_id}")
        if category_id:
            where_clauses.append(f"p.category_id = {category_id}")
        if start_date:
            where_clauses.append(f"r.return_date >= '{start_date.isoformat()}'")
        if end_date:
            where_clauses.append(f"r.return_date <= '{end_date.isoformat()} 23:59:59'")

        filter_clause = " AND ".join(where_clauses)

        query = f"""
            SELECT 
                r.return_reason AS reason,
                COUNT(r.return_id) AS incident_count,
                ROUND(COALESCE(SUM(r.refund_amount), 0.0), 2) AS total_refund_amount
            FROM returns r
            JOIN products p ON r.product_id = p.product_id
            WHERE {filter_clause}
            GROUP BY r.return_reason
            ORDER BY incident_count DESC;
        """
        rows = self.execute_query(query)
        total_incidents = sum(int(r["incident_count"]) for r in rows)

        metrics: List[ReturnReasonMetric] = []
        for r in rows:
            cnt = int(r["incident_count"])
            pct = round(self.safe_divide(float(cnt), float(total_incidents)) * 100.0, 1)
            metrics.append(
                ReturnReasonMetric(
                    reason=r["reason"],
                    incident_count=cnt,
                    total_refund_amount=float(r["total_refund_amount"]),
                    percentage_of_all_returns=pct,
                )
            )

        return metrics

    def get_overall_return_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> ReturnsOverallSummary:
        """
        Platform-wide executive scorecard for returns, refunds, and financial leakage.
        """
        date_filter_returns = self._format_date_filter("r.return_date", start_date, end_date)
        date_filter_orders = self._format_date_filter("o.order_date", start_date, end_date)

        # 1. Total return events, units returned, and refunds issued
        ret_query = f"""
            SELECT 
                COUNT(r.return_id) AS return_events,
                COALESCE(SUM(r.quantity_returned), 0) AS units_returned,
                ROUND(COALESCE(SUM(r.refund_amount), 0.0), 2) AS total_refunds
            FROM returns r
            WHERE 1=1 {date_filter_returns};
        """
        ret_row = self.execute_query(ret_query)[0]
        return_events = int(ret_row["return_events"] or 0)
        units_returned = int(ret_row["units_returned"] or 0)
        total_refunds = float(ret_row["total_refunds"] or 0.0)

        # 2. Total gross sales & sold units
        sales_query = f"""
            SELECT 
                COALESCE(SUM(oi.quantity), 0) AS units_sold,
                ROUND(COALESCE(SUM(oi.item_total), 0.0), 2) AS gross_sales
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.status = 'completed' {date_filter_orders};
        """
        sales_row = self.execute_query(sales_query)[0]
        units_sold = int(sales_row["units_sold"] or 0)
        gross_sales = float(sales_row["gross_sales"] or 0.0)

        platform_return_rate = round(
            self.safe_divide(float(units_returned), float(units_sold)) * 100.0, 2
        )
        refund_ratio = round(
            self.safe_divide(total_refunds, gross_sales) * 100.0, 2
        )

        # 3. Return reasons breakdown
        reasons = self.get_return_reasons_breakdown(start_date=start_date, end_date=end_date)

        # 4. Count high risk products (return rate >= 12%)
        products = self.get_return_rate_by_product()
        high_risk_count = sum(1 for p in products if p.risk_level == "High Risk")

        return ReturnsOverallSummary(
            total_return_events=return_events,
            total_units_returned=units_returned,
            total_refund_amount=total_refunds,
            platform_return_rate_pct=platform_return_rate,
            refund_ratio_pct=refund_ratio,
            high_risk_products_count=high_risk_count,
            top_return_reasons=reasons,
        )

    def get_return_rate_by_product(
        self,
        limit: Optional[int] = None,
        sort_by: str = "return_rate_pct",
        ascending: bool = False,
        min_units_sold: int = 1
    ) -> List[ProductReturnMetric]:
        """
        Evaluate SKU-level return rates, refund totals, revenue leakage, and risk tier.
        """
        query = f"""
            WITH prod_sales AS (
                SELECT 
                    oi.product_id,
                    SUM(oi.quantity) AS units_sold,
                    SUM(oi.item_total) AS gross_revenue
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                WHERE o.status = 'completed'
                GROUP BY oi.product_id
            ),
            prod_returns AS (
                SELECT 
                    r.product_id,
                    COUNT(r.return_id) AS return_count,
                    SUM(r.quantity_returned) AS units_returned,
                    SUM(r.refund_amount) AS total_refunds
                FROM returns r
                GROUP BY r.product_id
            ),
            prod_reasons AS (
                SELECT 
                    product_id,
                    return_reason,
                    ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY COUNT(*) DESC) as rn
                FROM returns
                GROUP BY product_id, return_reason
            )
            SELECT 
                p.product_id,
                p.sku,
                p.title,
                c.name AS category_name,
                COALESCE(ps.units_sold, 0) AS units_sold,
                COALESCE(pr.units_returned, 0) AS units_returned,
                ROUND(
                    CASE WHEN COALESCE(ps.units_sold, 0) > 0 
                         THEN (COALESCE(pr.units_returned, 0) * 100.0) / ps.units_sold 
                         ELSE 0.0 
                    END, 2
                ) AS return_rate_pct,
                ROUND(COALESCE(ps.gross_revenue, 0.0), 2) AS gross_revenue,
                ROUND(COALESCE(pr.total_refunds, 0.0), 2) AS refund_amount,
                ROUND(COALESCE(ps.gross_revenue, 0.0) - COALESCE(pr.total_refunds, 0.0), 2) AS net_revenue,
                ROUND(
                    CASE WHEN COALESCE(ps.gross_revenue, 0.0) > 0 
                         THEN (COALESCE(pr.total_refunds, 0.0) * 100.0) / ps.gross_revenue 
                         ELSE 0.0 
                    END, 2
                ) AS refund_ratio_pct,
                COALESCE(reas.return_reason, 'None') AS primary_return_reason
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN prod_sales ps ON p.product_id = ps.product_id
            LEFT JOIN prod_returns pr ON p.product_id = pr.product_id
            LEFT JOIN prod_reasons reas ON p.product_id = reas.product_id AND reas.rn = 1
            WHERE COALESCE(ps.units_sold, 0) >= {min_units_sold}
            ORDER BY {sort_by} {"ASC" if ascending else "DESC"};
        """
        rows = self.execute_query(query)
        metrics: List[ProductReturnMetric] = []

        for r in rows:
            ret_rate = float(r["return_rate_pct"])
            ref_ratio = float(r["refund_ratio_pct"])

            if ret_rate >= 12.0 or ref_ratio >= 15.0:
                risk_level = "High Risk"
            elif ret_rate >= 7.0:
                risk_level = "Moderate Risk"
            else:
                risk_level = "Normal"

            metrics.append(
                ProductReturnMetric(
                    product_id=r["product_id"],
                    sku=r["sku"],
                    title=r["title"],
                    category_name=r["category_name"],
                    units_sold=int(r["units_sold"]),
                    units_returned=int(r["units_returned"]),
                    return_rate_pct=ret_rate,
                    gross_revenue=float(r["gross_revenue"]),
                    refund_amount=float(r["refund_amount"]),
                    net_revenue=float(r["net_revenue"]),
                    refund_ratio_pct=ref_ratio,
                    primary_return_reason=r["primary_return_reason"],
                    risk_level=risk_level,
                )
            )

        if limit:
            return metrics[:limit]
        return metrics

    def get_highest_return_products(self, limit: int = 10) -> List[ProductReturnMetric]:
        """
        Extract products with the highest return rates across the catalog (min 10 units sold).
        """
        return self.get_return_rate_by_product(
            limit=limit,
            sort_by="return_rate_pct",
            ascending=False,
            min_units_sold=10
        )

    def get_return_rate_by_category(self) -> List[CategoryReturnMetric]:
        """
        Benchmark returns and refunds across product categories.
        """
        query = """
            WITH cat_sales AS (
                SELECT 
                    p.category_id,
                    SUM(oi.quantity) AS units_sold,
                    SUM(oi.item_total) AS gross_revenue
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                JOIN products p ON oi.product_id = p.product_id
                WHERE o.status = 'completed'
                GROUP BY p.category_id
            ),
            cat_returns AS (
                SELECT 
                    p.category_id,
                    COUNT(r.return_id) AS return_count,
                    SUM(r.quantity_returned) AS units_returned,
                    SUM(r.refund_amount) AS total_refunds
                FROM returns r
                JOIN products p ON r.product_id = p.product_id
                GROUP BY p.category_id
            ),
            cat_reasons AS (
                SELECT 
                    p.category_id,
                    r.return_reason,
                    ROW_NUMBER() OVER (PARTITION BY p.category_id ORDER BY COUNT(*) DESC) as rn
                FROM returns r
                JOIN products p ON r.product_id = p.product_id
                GROUP BY p.category_id, r.return_reason
            )
            SELECT 
                c.category_id,
                c.name AS category_name,
                COALESCE(cs.units_sold, 0) AS units_sold,
                COALESCE(cr.units_returned, 0) AS units_returned,
                ROUND(
                    CASE WHEN COALESCE(cs.units_sold, 0) > 0 
                         THEN (COALESCE(cr.units_returned, 0) * 100.0) / cs.units_sold 
                         ELSE 0.0 
                    END, 2
                ) AS return_rate_pct,
                ROUND(COALESCE(cr.total_refunds, 0.0), 2) AS total_refunds,
                ROUND(COALESCE(cs.gross_revenue, 0.0), 2) AS gross_revenue,
                ROUND(
                    CASE WHEN COALESCE(cs.gross_revenue, 0.0) > 0 
                         THEN (COALESCE(cr.total_refunds, 0.0) * 100.0) / cs.gross_revenue 
                         ELSE 0.0 
                    END, 2
                ) AS refund_ratio_pct,
                COALESCE(reas.return_reason, 'None') AS primary_return_reason
            FROM categories c
            LEFT JOIN cat_sales cs ON c.category_id = cs.category_id
            LEFT JOIN cat_returns cr ON c.category_id = cr.category_id
            LEFT JOIN cat_reasons reas ON c.category_id = reas.category_id AND reas.rn = 1
            ORDER BY return_rate_pct DESC;
        """
        rows = self.execute_query(query)
        cat_metrics: List[CategoryReturnMetric] = []

        for r in rows:
            cat_metrics.append(
                CategoryReturnMetric(
                    category_id=r["category_id"],
                    category_name=r["category_name"],
                    units_sold=int(r["units_sold"]),
                    units_returned=int(r["units_returned"]),
                    return_rate_pct=float(r["return_rate_pct"]),
                    total_refunds=float(r["total_refunds"]),
                    gross_revenue=float(r["gross_revenue"]),
                    refund_ratio_pct=float(r["refund_ratio_pct"]),
                    primary_return_reason=r["primary_return_reason"],
                )
            )

        return cat_metrics

    def get_temporal_return_trends(
        self,
        granularity: str = "monthly"
    ) -> List[Dict[str, Any]]:
        """
        Track return incidents, returned quantities, refund amounts, and return rates over time.
        """
        period_format = "%Y-%m" if granularity == "monthly" else "%Y-%W"

        query = f"""
            WITH monthly_returns AS (
                SELECT 
                    strftime('{period_format}', return_date) AS period,
                    COUNT(return_id) AS return_events,
                    SUM(quantity_returned) AS units_returned,
                    SUM(refund_amount) AS total_refunds
                FROM returns
                GROUP BY period
            ),
            monthly_sales AS (
                SELECT 
                    strftime('{period_format}', o.order_date) AS period,
                    SUM(oi.quantity) AS units_sold,
                    SUM(oi.item_total) AS gross_sales
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                WHERE o.status = 'completed'
                GROUP BY period
            )
            SELECT 
                ms.period,
                COALESCE(mr.return_events, 0) AS return_events,
                COALESCE(mr.units_returned, 0) AS units_returned,
                ROUND(COALESCE(mr.total_refunds, 0.0), 2) AS total_refunds,
                COALESCE(ms.units_sold, 0) AS units_sold,
                ROUND(COALESCE(ms.gross_sales, 0.0), 2) AS gross_sales,
                ROUND(
                    CASE WHEN COALESCE(ms.units_sold, 0) > 0 
                         THEN (COALESCE(mr.units_returned, 0) * 100.0) / ms.units_sold 
                         ELSE 0.0 
                    END, 2
                ) AS return_rate_pct,
                ROUND(
                    CASE WHEN COALESCE(ms.gross_sales, 0.0) > 0 
                         THEN (COALESCE(mr.total_refunds, 0.0) * 100.0) / ms.gross_sales 
                         ELSE 0.0 
                    END, 2
                ) AS refund_ratio_pct
            FROM monthly_sales ms
            LEFT JOIN monthly_returns mr ON ms.period = mr.period
            ORDER BY ms.period ASC;
        """
        return self.execute_query(query)

    def get_connected_return_review_insights(
        self,
        return_rate_threshold: float = 7.0,
        limit: int = 10
    ) -> List[ConnectedReturnInsight]:
        """
        Triangulate returns data with sales economics and customer review complaints
        to deliver an explainable root cause verdict for high-return products.
        """
        query = f"""
            WITH prod_sales AS (
                SELECT 
                    oi.product_id,
                    SUM(oi.quantity) AS units_sold,
                    SUM(oi.item_total) AS gross_revenue
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                WHERE o.status = 'completed'
                GROUP BY oi.product_id
            ),
            prod_returns AS (
                SELECT 
                    r.product_id,
                    COUNT(r.return_id) AS return_count,
                    SUM(r.quantity_returned) AS units_returned,
                    SUM(r.refund_amount) AS total_refunds
                FROM returns r
                GROUP BY r.product_id
            ),
            prod_reasons AS (
                SELECT 
                    product_id,
                    return_reason,
                    ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY COUNT(*) DESC) as rn
                FROM returns
                GROUP BY product_id, return_reason
            ),
            prod_reviews AS (
                SELECT 
                    r.product_id,
                    ROUND(AVG(r.rating), 2) AS avg_rating,
                    COUNT(*) AS total_reviews,
                    ROUND(
                        SUM(CASE WHEN ri.sentiment_label = 'negative' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1
                    ) AS neg_review_pct
                FROM reviews r
                LEFT JOIN review_insights ri ON r.review_id = ri.review_id
                GROUP BY r.product_id
            ),
            prod_top_complaint AS (
                SELECT 
                    r.product_id,
                    COALESCE(ri.detected_issue, ri.primary_topic) AS top_complaint,
                    ROW_NUMBER() OVER (PARTITION BY r.product_id ORDER BY COUNT(*) DESC) as rn
                FROM reviews r
                JOIN review_insights ri ON r.review_id = ri.review_id
                WHERE ri.sentiment_label = 'negative'
                GROUP BY r.product_id, top_complaint
            )
            SELECT 
                p.product_id,
                p.sku,
                p.title,
                c.name AS category_name,
                COALESCE(ps.units_sold, 0) AS units_sold,
                COALESCE(pr.units_returned, 0) AS units_returned,
                ROUND(
                    CASE WHEN COALESCE(ps.units_sold, 0) > 0 
                         THEN (COALESCE(pr.units_returned, 0) * 100.0) / ps.units_sold 
                         ELSE 0.0 
                    END, 2
                ) AS return_rate_pct,
                ROUND(COALESCE(pr.total_refunds, 0.0), 2) AS refund_amount,
                COALESCE(reas.return_reason, 'None') AS primary_return_reason,
                COALESCE(prev.avg_rating, 0.0) AS avg_rating,
                COALESCE(prev.total_reviews, 0) AS total_reviews,
                COALESCE(prev.neg_review_pct, 0.0) AS neg_review_pct,
                COALESCE(tc.top_complaint, 'None detected') AS top_review_complaint
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            JOIN prod_sales ps ON p.product_id = ps.product_id
            LEFT JOIN prod_returns pr ON p.product_id = pr.product_id
            LEFT JOIN prod_reasons reas ON p.product_id = reas.product_id AND reas.rn = 1
            LEFT JOIN prod_reviews prev ON p.product_id = prev.product_id
            LEFT JOIN prod_top_complaint tc ON p.product_id = tc.product_id AND tc.rn = 1
            WHERE (COALESCE(pr.units_returned, 0) * 100.0 / ps.units_sold) >= {return_rate_threshold}
            ORDER BY return_rate_pct DESC
            LIMIT {limit};
        """
        rows = self.execute_query(query)
        insights: List[ConnectedReturnInsight] = []

        for r in rows:
            ret_rate = float(r["return_rate_pct"])
            neg_pct = float(r["neg_review_pct"])
            reason = r["primary_return_reason"]
            complaint = r["top_review_complaint"]
            sku = r["sku"]
            title = r["title"]

            # Synthesize automated root-cause verdict
            if reason == "Defective/Damaged" and "battery" in complaint.lower():
                verdict = (
                    f"Hardware / Manufacturing Defect: High return rate of {ret_rate}% "
                    f"is driven primarily by '{reason}' returns (${r['refund_amount']:,.2f} refunded). "
                    f"Corroborated by {neg_pct}% negative customer reviews citing '{complaint}'."
                )
            elif reason == "Incorrect Size/Fit" or "tight" in complaint.lower() or "size" in complaint.lower():
                verdict = (
                    f"Sizing & Fit Inaccuracy: Return rate of {ret_rate}% is driven by "
                    f"'{reason}' returns. Customer reviews ({neg_pct}% negative) specifically complain "
                    f"that the product '{complaint}'. Recommended action: Update sizing chart on product page."
                )
            elif ret_rate >= 10.0:
                verdict = (
                    f"Severe Quality Risk: Unusually high return rate of {ret_rate}% "
                    f"with primary reason '{reason}'. Reviews indicate customer dissatisfaction "
                    f"with '{complaint}' (Average rating: {r['avg_rating']}/5.0)."
                )
            else:
                verdict = (
                    f"Elevated Return Frequency: {ret_rate}% return rate with primary reason "
                    f"'{reason}' and {neg_pct}% negative review feedback citing '{complaint}'."
                )

            insights.append(
                ConnectedReturnInsight(
                    product_id=r["product_id"],
                    sku=sku,
                    title=title,
                    category_name=r["category_name"],
                    units_sold=int(r["units_sold"]),
                    units_returned=int(r["units_returned"]),
                    return_rate_pct=ret_rate,
                    refund_amount=float(r["refund_amount"]),
                    primary_return_reason=reason,
                    average_rating=float(r["avg_rating"]),
                    total_reviews=int(r["total_reviews"]),
                    negative_review_pct=neg_pct,
                    top_review_complaint=complaint,
                    correlation_verdict=verdict,
                )
            )

        return insights
