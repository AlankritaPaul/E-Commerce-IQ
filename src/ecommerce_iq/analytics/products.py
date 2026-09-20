"""
Product Performance and Unit Economics Analytics Engine.

Provides deep SKU-level multi-dimensional evaluation:
- Net Revenue, Units Sold, and Order Frequency
- Cost of Goods Sold (COGS), Gross Profit, and Margin %
- Return Rates (%), Total Refund Amounts ($), and Units Returned
- Customer Feedback, CSAT Star Ratings, Sentiment Breakdown, and Complaints
- Transparent, Data-Driven Performance Classification (High Performers, Quality Risks, Low Velocity Dead Stock)
- Transparent 0-100 Product Health Scoring Algorithm
"""

from datetime import date
from typing import Any, Dict, List, Optional, Tuple
from ecommerce_iq.analytics.base import BaseAnalyticsEngine


class ProductAnalyticsEngine(BaseAnalyticsEngine):
    """
    Executes product-level analytical queries against the SQL database.
    Calculates all metrics, scores, and classifications dynamically from data.
    """

    def get_revenue_by_product(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None,
        sort_by: str = "net_revenue",
        ascending: bool = False,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Calculate revenue, units sold, order frequency, COGS, gross profit, return rate,
        and customer rating per product using CTEs to eliminate join fan-out.
        """
        date_filter_orders = self._format_date_filter("o.order_date", start_date, end_date)
        cat_filter = f"AND p.category_id = {category_id}" if category_id else ""

        query = f"""
            WITH product_sales AS (
                SELECT 
                    oi.product_id,
                    COUNT(DISTINCT oi.order_id) AS order_frequency,
                    COALESCE(SUM(oi.quantity), 0) AS units_sold,
                    COALESCE(SUM(oi.item_total), 0.0) AS gross_revenue,
                    COALESCE(SUM(oi.discount_applied), 0.0) AS discount_amount,
                    COALESCE(SUM(oi.quantity * oi.unit_cost), 0.0) AS cogs
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id AND o.status = 'completed'
                WHERE 1=1 {date_filter_orders}
                GROUP BY oi.product_id
            ),
            product_returns AS (
                SELECT 
                    r.product_id,
                    COALESCE(SUM(r.quantity_returned), 0) AS units_returned,
                    COALESCE(SUM(r.refund_amount), 0.0) AS refund_amount
                FROM returns r
                GROUP BY r.product_id
            ),
            product_reviews AS (
                SELECT 
                    rev.product_id,
                    ROUND(AVG(rev.rating), 2) AS avg_rating,
                    COUNT(rev.review_id) AS total_reviews,
                    SUM(CASE WHEN rev.rating >= 4 THEN 1 ELSE 0 END) AS positive_reviews,
                    SUM(CASE WHEN rev.rating <= 2 THEN 1 ELSE 0 END) AS negative_reviews
                FROM reviews rev
                GROUP BY rev.product_id
            )
            SELECT 
                p.product_id,
                p.sku,
                p.title,
                c.name AS category_name,
                p.cost_price,
                p.retail_price,
                p.stock_quantity,
                COALESCE(s.order_frequency, 0) AS order_frequency,
                COALESCE(s.units_sold, 0) AS units_sold,
                ROUND(COALESCE(s.gross_revenue, 0.0), 2) AS gross_revenue,
                ROUND(COALESCE(s.discount_amount, 0.0), 2) AS discount_amount,
                ROUND(COALESCE(s.gross_revenue, 0.0) - COALESCE(s.discount_amount, 0.0), 2) AS net_revenue,
                ROUND(COALESCE(s.cogs, 0.0), 2) AS cogs,
                ROUND((COALESCE(s.gross_revenue, 0.0) - COALESCE(s.discount_amount, 0.0)) - COALESCE(s.cogs, 0.0), 2) AS gross_profit,
                ROUND(
                    CASE 
                        WHEN (COALESCE(s.gross_revenue, 0.0) - COALESCE(s.discount_amount, 0.0)) > 0 
                        THEN (((COALESCE(s.gross_revenue, 0.0) - COALESCE(s.discount_amount, 0.0)) - COALESCE(s.cogs, 0.0)) * 100.0) 
                             / (COALESCE(s.gross_revenue, 0.0) - COALESCE(s.discount_amount, 0.0))
                        ELSE 0.0 
                    END, 2
                ) AS profit_margin_pct,
                COALESCE(r.units_returned, 0) AS units_returned,
                ROUND(COALESCE(r.refund_amount, 0.0), 2) AS refund_amount,
                ROUND(
                    CASE 
                        WHEN COALESCE(s.units_sold, 0) > 0 
                        THEN (COALESCE(r.units_returned, 0) * 100.0) / s.units_sold 
                        ELSE 0.0 
                    END, 2
                ) AS return_rate_pct,
                COALESCE(rev.avg_rating, 0.0) AS avg_rating,
                COALESCE(rev.total_reviews, 0) AS total_reviews,
                COALESCE(rev.positive_reviews, 0) AS positive_reviews,
                COALESCE(rev.negative_reviews, 0) AS negative_reviews
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN product_sales s ON p.product_id = s.product_id
            LEFT JOIN product_returns r ON p.product_id = r.product_id
            LEFT JOIN product_reviews rev ON p.product_id = rev.product_id
            WHERE 1=1 {cat_filter}
            ORDER BY {sort_by} {"ASC" if ascending else "DESC"}
            LIMIT {limit};
        """
        return self.execute_query(query)

    def get_product_feedback_details(self, product_id: int) -> Dict[str, Any]:
        """
        Retrieve granular customer feedback, top complaints, and sentiment for a given product.
        """
        # 1. Feedback summary
        summary_query = f"""
            SELECT 
                COUNT(*) AS total_reviews,
                ROUND(AVG(rating), 2) AS avg_rating,
                SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) AS positive_count,
                SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) AS neutral_count,
                SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) AS negative_count
            FROM reviews
            WHERE product_id = {product_id};
        """
        s_row = self.execute_query(summary_query)[0]
        total_rev = s_row["total_reviews"] or 0
        avg_rat = float(s_row["avg_rating"] or 0.0)
        pos_count = s_row["positive_count"] or 0
        neg_count = s_row["negative_count"] or 0

        # 2. Top negative complaints from review insights
        complaints_query = f"""
            SELECT 
                ri.detected_issue AS issue,
                COUNT(*) AS count
            FROM review_insights ri
            JOIN reviews r ON ri.review_id = r.review_id
            WHERE r.product_id = {product_id}
              AND ri.sentiment_label = 'negative'
              AND ri.detected_issue != 'None'
            GROUP BY ri.detected_issue
            ORDER BY count DESC
            LIMIT 5;
        """
        complaints = self.execute_query(complaints_query)

        # 3. Top positive topics
        praises_query = f"""
            SELECT 
                ri.primary_topic AS topic,
                COUNT(*) AS count
            FROM review_insights ri
            JOIN reviews r ON ri.review_id = r.review_id
            WHERE r.product_id = {product_id}
              AND ri.sentiment_label = 'positive'
            GROUP BY ri.primary_topic
            ORDER BY count DESC
            LIMIT 5;
        """
        praises = self.execute_query(praises_query)

        return {
            "product_id": product_id,
            "total_reviews": total_rev,
            "average_rating": avg_rat,
            "positive_count": pos_count,
            "negative_count": neg_count,
            "positive_percentage": round(self.safe_divide(pos_count, total_rev) * 100.0, 1),
            "negative_percentage": round(self.safe_divide(neg_count, total_rev) * 100.0, 1),
            "top_complaints": complaints,
            "top_praises": praises,
        }

    def calculate_health_score(self, product: Dict[str, Any], max_revenue: float) -> float:
        """
        Transparent 0-100 Product Health Score Algorithm:
        - Revenue Component (35%): Normalized against catalog top revenue
        - CSAT Component (25%): (avg_rating / 5.0) * 100
        - Return Rate Component (25%): 100 - (return_rate_pct * 3.5), floored at 0
        - Margin Component (15%): Clamped profit_margin_pct between 0 and 100
        """
        net_rev = max(0.0, product.get("net_revenue", 0.0))
        rev_score = min(100.0, (net_rev / max_revenue * 100.0)) if max_revenue > 0 else 0.0

        avg_rat = product.get("avg_rating", 0.0)
        rating_score = (avg_rat / 5.0) * 100.0 if avg_rat > 0 else 50.0

        ret_pct = product.get("return_rate_pct", 0.0)
        return_score = max(0.0, 100.0 - (ret_pct * 3.5))

        margin_pct = product.get("profit_margin_pct", 0.0)
        margin_score = min(100.0, max(0.0, margin_pct))

        composite_score = (
            (rev_score * 0.35) +
            (rating_score * 0.25) +
            (return_score * 0.25) +
            (margin_score * 0.15)
        )
        return round(composite_score, 1)

    def classify_products(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Classify all products using transparent, data-driven operational criteria:

        1. 'high_performing' (Cash Cows / Star Performers):
           - Net Revenue >= median revenue of catalog
           - Return Rate <= 6.5% (healthy benchmark)
           - Average Rating >= 4.2 / 5.0
           - Profit Margin >= 40.0%

        2. 'quality_risk' (Defect Anomaly / High Return Rate):
           - Return Rate >= 12.0% OR Average Rating <= 3.2 / 5.0

        3. 'low_velocity' (Dead Stock / Lagging Catalog):
           - Units Sold <= 40 units across period OR Order Frequency <= 35 orders

        4. 'steady_performers':
           - Products that maintain balanced metrics without extremes.
        """
        products = self.get_revenue_by_product(start_date=start_date, end_date=end_date, limit=200)
        if not products:
            return {"high_performing": [], "quality_risk": [], "low_velocity": [], "steady_performers": []}

        # Calculate dynamic median revenue for transparent thresholding
        revenues = sorted([p["net_revenue"] for p in products])
        median_revenue = revenues[len(revenues) // 2] if revenues else 0.0
        max_revenue = max(revenues) if revenues else 1.0

        classified: Dict[str, List[Dict[str, Any]]] = {
            "high_performing": [],
            "quality_risk": [],
            "low_velocity": [],
            "steady_performers": []
        }

        for p in products:
            p_augmented = dict(p)
            health = self.calculate_health_score(p, max_revenue)
            p_augmented["health_score"] = health

            # Fetch top complaint if negative reviews exist
            feedback = self.get_product_feedback_details(p["product_id"])
            p_augmented["feedback_summary"] = feedback
            top_comp = feedback["top_complaints"][0]["issue"] if feedback["top_complaints"] else "None"
            p_augmented["primary_complaint"] = top_comp

            # Transparent Criteria Evaluation
            is_high_performer = (
                p["net_revenue"] >= median_revenue and
                p["return_rate_pct"] <= 6.5 and
                p["avg_rating"] >= 4.2 and
                p["profit_margin_pct"] >= 40.0
            )

            is_quality_risk = (
                p["return_rate_pct"] >= 12.0 or
                (p["avg_rating"] > 0 and p["avg_rating"] <= 3.2)
            )

            is_low_velocity = (
                p["units_sold"] <= 40 or
                p["order_frequency"] <= 35
            )

            if is_quality_risk:
                p_risk = dict(p_augmented)
                p_risk["classification"] = "Quality Risk (High Returns/Low CSAT)"
                p_risk["classification_reason"] = (
                    f"Return rate {p['return_rate_pct']:.1f}% exceeds 12.0% threshold, "
                    f"rating {p['avg_rating']:.1f}/5.0. Primary complaint: '{top_comp}'."
                )
                classified["quality_risk"].append(p_risk)

            if is_low_velocity:
                p_slow = dict(p_augmented)
                p_slow["classification"] = "Low Velocity (Dead Stock Candidate)"
                p_slow["classification_reason"] = (
                    f"Low sales volume ({p['units_sold']} units, {p['order_frequency']} orders across period). "
                    f"Stale inventory risking warehouse holding costs."
                )
                classified["low_velocity"].append(p_slow)

            if is_high_performer:
                p_high = dict(p_augmented)
                p_high["classification"] = "High-Performing (Cash Cow)"
                p_high["classification_reason"] = (
                    f"Strong net revenue (${p['net_revenue']:,.2f} >= median ${median_revenue:,.2f}), "
                    f"high CSAT {p['avg_rating']:.1f}/5.0, healthy margin {p['profit_margin_pct']:.1f}%, "
                    f"low return rate {p['return_rate_pct']:.1f}%."
                )
                classified["high_performing"].append(p_high)

            if not (is_quality_risk or is_low_velocity or is_high_performer):
                p_steady = dict(p_augmented)
                p_steady["classification"] = "Steady Performer"
                p_steady["classification_reason"] = (
                    f"Consistent catalog performer with stable return rate ({p['return_rate_pct']:.1f}%) "
                    f"and average CSAT ({p['avg_rating']:.1f}/5.0)."
                )
                classified["steady_performers"].append(p_steady)

        # Sort within each category by health score
        for key in classified:
            classified[key].sort(key=lambda x: x["health_score"], reverse=(key == "high_performing"))

        return classified

    def get_top_products(
        self,
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Return top products sorted by net revenue descending."""
        return self.get_revenue_by_product(
            start_date=start_date,
            end_date=end_date,
            sort_by="net_revenue",
            ascending=False,
            limit=limit
        )

    def get_underperforming_products(
        self,
        revenue_threshold: Optional[float] = None,
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Return products lagging in sales volume or exhibiting severe return rates."""
        products = self.get_revenue_by_product(
            start_date=start_date,
            end_date=end_date,
            sort_by="units_sold",
            ascending=True,
            limit=limit
        )
        if revenue_threshold is not None:
            return [p for p in products if p["net_revenue"] <= revenue_threshold]
        return products

    def get_category_breakdown(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Aggregate revenue, profit, units sold, and return distribution segmented by product category.
        """
        date_filter_orders = self._format_date_filter("o.order_date", start_date, end_date)

        query = f"""
            WITH cat_sales AS (
                SELECT 
                    p.category_id,
                    COALESCE(SUM(oi.quantity), 0) AS units_sold,
                    COALESCE(SUM(oi.item_total), 0.0) AS gross_revenue,
                    COALESCE(SUM(oi.discount_applied), 0.0) AS discounts,
                    COALESCE(SUM(oi.quantity * oi.unit_cost), 0.0) AS cogs
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id AND o.status = 'completed'
                JOIN products p ON oi.product_id = p.product_id
                WHERE 1=1 {date_filter_orders}
                GROUP BY p.category_id
            ),
            cat_returns AS (
                SELECT 
                    p.category_id,
                    COALESCE(SUM(r.quantity_returned), 0) AS units_returned,
                    COALESCE(SUM(r.refund_amount), 0.0) AS refund_amount
                FROM returns r
                JOIN products p ON r.product_id = p.product_id
                GROUP BY p.category_id
            )
            SELECT 
                c.category_id,
                c.name AS category_name,
                COALESCE(s.units_sold, 0) AS units_sold,
                ROUND(COALESCE(s.gross_revenue, 0.0), 2) AS gross_revenue,
                ROUND(COALESCE(s.discounts, 0.0), 2) AS discount_amount,
                ROUND(COALESCE(s.gross_revenue, 0.0) - COALESCE(s.discounts, 0.0), 2) AS net_revenue,
                ROUND((COALESCE(s.gross_revenue, 0.0) - COALESCE(s.discounts, 0.0)) - COALESCE(s.cogs, 0.0), 2) AS gross_profit,
                ROUND(
                    CASE 
                        WHEN (COALESCE(s.gross_revenue, 0.0) - COALESCE(s.discounts, 0.0)) > 0 
                        THEN (((COALESCE(s.gross_revenue, 0.0) - COALESCE(s.discounts, 0.0)) - COALESCE(s.cogs, 0.0)) * 100.0) 
                             / (COALESCE(s.gross_revenue, 0.0) - COALESCE(s.discounts, 0.0))
                        ELSE 0.0 
                    END, 2
                ) AS profit_margin_pct,
                COALESCE(r.units_returned, 0) AS units_returned,
                ROUND(COALESCE(r.refund_amount, 0.0), 2) AS refund_amount,
                ROUND(
                    CASE 
                        WHEN COALESCE(s.units_sold, 0) > 0 
                        THEN (COALESCE(r.units_returned, 0) * 100.0) / s.units_sold 
                        ELSE 0.0 
                    END, 2
                ) AS return_rate_pct
            FROM categories c
            LEFT JOIN cat_sales s ON c.category_id = s.category_id
            LEFT JOIN cat_returns r ON c.category_id = r.category_id
            ORDER BY net_revenue DESC;
        """
        return self.execute_query(query)
