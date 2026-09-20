"""
Product Performance and Unit Economics Analytics Engine.

Calculates SKU and category-level metrics directly from the database:
- Product-level Net Revenue, Gross Margin, and Units Sold
- Top-Performing Products ("Cash Cows")
- Underperforming or Lagging Products ("Dead Stock")
- Return Rates and Rating Distributions by SKU
- Category Revenue Contribution and Margin Breakdown
"""

from datetime import date
from typing import Any, Dict, List, Optional
from ecommerce_iq.analytics.base import BaseAnalyticsEngine


class ProductAnalyticsEngine(BaseAnalyticsEngine):
    """
    Executes product-level analytical queries against the SQL database.
    """

    def get_revenue_by_product(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None,
        sort_by: str = "net_revenue",
        ascending: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Calculate revenue, units sold, COGS, gross profit, and return rate per product.

        Args:
            start_date: Optional date lower bound.
            end_date: Optional date upper bound.
            category_id: Optional filter for a specific category.
            sort_by: Column to order by ('net_revenue', 'units_sold', 'gross_profit', 'return_rate_pct').
            ascending: Sort direction (default False for descending).
            limit: Maximum records to return.

        Returns:
            List of dictionary records with complete unit economics per SKU.
        """
        date_filter_orders = self._format_date_filter("o.order_date", start_date, end_date)
        cat_filter = f"AND p.category_id = {category_id}" if category_id else ""

        # Using CTE to cleanly aggregate sales, returns, and reviews without join fan-out
        query = f"""
            WITH product_sales AS (
                SELECT 
                    oi.product_id,
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
                    COALESCE(SUM(r.refund_amount), 0.0) AS refund_total
                FROM returns r
                GROUP BY r.product_id
            ),
            product_reviews AS (
                SELECT 
                    rev.product_id,
                    ROUND(AVG(rev.rating), 2) AS avg_rating,
                    COUNT(rev.review_id) AS total_reviews
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
                ROUND(COALESCE(r.refund_total, 0.0), 2) AS refund_total,
                ROUND(
                    CASE 
                        WHEN COALESCE(s.units_sold, 0) > 0 
                        THEN (COALESCE(r.units_returned, 0) * 100.0) / s.units_sold 
                        ELSE 0.0 
                    END, 2
                ) AS return_rate_pct,
                COALESCE(rev.avg_rating, 0.0) AS avg_rating,
                COALESCE(rev.total_reviews, 0) AS total_reviews
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

    def get_top_products(
        self,
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Return the highest revenue-generating products ("Cash Cows").
        """
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
        """
        Return lagging products with the lowest sales volume or revenue ("Dead Stock").
        """
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
                    COALESCE(SUM(r.refund_amount), 0.0) AS refund_total
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
                ROUND(COALESCE(r.refund_total, 0.0), 2) AS refund_total,
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
