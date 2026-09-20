"""
Customer Behavior and Lifetime Value Analytics Engine.

Provides deep analytical insights into customer cohorts, purchasing habits,
retention velocity, return rates, and feedback activity while strictly
protecting Personally Identifiable Information (PII).
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from ecommerce_iq.analytics.base import BaseAnalyticsEngine
from ecommerce_iq.models.schemas import CustomerAggregateSummary, CustomerProfile


class CustomerAnalyticsEngine(BaseAnalyticsEngine):
    """
    Executes customer behavioral and cohort queries against the SQL database.
    """

    def get_aggregate_customer_metrics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> CustomerAggregateSummary:
        """
        Compute platform-wide customer behavioral scorecards:
        - Registered base vs. Active purchasers
        - Repeat customer count and Repeat Purchase Rate (%)
        - Average Customer Lifetime Value (LTV) and Order Frequency
        - Return and Review participation rates
        - Behavioral segment breakdown
        """
        date_filter_orders = self._format_date_filter("o.order_date", start_date, end_date)

        # 1. Total registered customers
        reg_query = "SELECT COUNT(*) AS total FROM customers;"
        total_registered = int(self.execute_query(reg_query)[0]["total"] or 0)

        # 2. Purchasing patterns (active vs repeat vs one-time)
        purchaser_query = f"""
            WITH customer_order_counts AS (
                SELECT 
                    o.customer_id,
                    COUNT(DISTINCT o.order_id) AS orders_placed,
                    SUM(o.total_amount) AS customer_spend
                FROM orders o
                WHERE o.status = 'completed' {date_filter_orders}
                GROUP BY o.customer_id
            )
            SELECT 
                COUNT(*) AS active_purchasers,
                SUM(CASE WHEN orders_placed >= 2 THEN 1 ELSE 0 END) AS repeat_customers,
                SUM(CASE WHEN orders_placed = 1 THEN 1 ELSE 0 END) AS one_time_buyers,
                COALESCE(SUM(customer_spend), 0.0) AS total_spend,
                COALESCE(SUM(orders_placed), 0) AS total_orders
            FROM customer_order_counts;
        """
        p_row = self.execute_query(purchaser_query)[0]
        active_purchasers = int(p_row["active_purchasers"] or 0)
        repeat_customers = int(p_row["repeat_customers"] or 0)
        one_time_buyers = int(p_row["one_time_buyers"] or 0)
        total_spend = float(p_row["total_spend"] or 0.0)
        total_orders = int(p_row["total_orders"] or 0)

        repeat_rate_pct = round(
            self.safe_divide(float(repeat_customers), float(active_purchasers)) * 100.0, 2
        )
        avg_ltv = round(self.safe_divide(total_spend, float(active_purchasers)), 2)
        avg_frequency = round(self.safe_divide(float(total_orders), float(active_purchasers)), 2)

        # 3. Returning customer count
        returning_query = """
            SELECT COUNT(DISTINCT customer_id) AS returning_customers
            FROM returns;
        """
        ret_customers = int(self.execute_query(returning_query)[0]["returning_customers"] or 0)
        ret_rate_pct = round(
            self.safe_divide(float(ret_customers), float(active_purchasers)) * 100.0, 2
        )

        # 4. Reviewing customer count
        reviewing_query = """
            SELECT COUNT(DISTINCT customer_id) AS reviewing_customers
            FROM reviews;
        """
        rev_customers = int(self.execute_query(reviewing_query)[0]["reviewing_customers"] or 0)
        rev_rate_pct = round(
            self.safe_divide(float(rev_customers), float(active_purchasers)) * 100.0, 2
        )

        # 5. Segment breakdown
        segment_query = """
            SELECT customer_segment, COUNT(*) AS count
            FROM customers
            GROUP BY customer_segment;
        """
        seg_rows = self.execute_query(segment_query)
        segment_breakdown = {r["customer_segment"]: r["count"] for r in seg_rows}

        return CustomerAggregateSummary(
            total_registered_customers=total_registered,
            active_purchasers=active_purchasers,
            repeat_customers=repeat_customers,
            one_time_buyers=one_time_buyers,
            repeat_purchase_rate_pct=repeat_rate_pct,
            average_customer_ltv=avg_ltv,
            average_order_frequency=avg_frequency,
            customer_return_rate_pct=ret_rate_pct,
            review_participation_rate_pct=rev_rate_pct,
            segment_breakdown=segment_breakdown,
        )

    def get_order_frequency_distribution(self) -> List[Dict[str, Any]]:
        """
        Categorize customers by order frequency brackets (1, 2-3, 4-6, 7-10, 10+ orders)
        showing customer volume, total revenue generated, and percentage contribution.
        """
        query = """
            WITH customer_totals AS (
                SELECT 
                    customer_id,
                    COUNT(DISTINCT order_id) AS order_count,
                    SUM(total_amount) AS total_spend
                FROM orders
                WHERE status = 'completed'
                GROUP BY customer_id
            ),
            bracketed AS (
                SELECT 
                    customer_id,
                    order_count,
                    total_spend,
                    CASE 
                        WHEN order_count = 1 THEN '1 Order (One-Time)'
                        WHEN order_count BETWEEN 2 AND 3 THEN '2-3 Orders (Developing)'
                        WHEN order_count BETWEEN 4 AND 6 THEN '4-6 Orders (Loyal)'
                        WHEN order_count BETWEEN 7 AND 9 THEN '7-9 Orders (High Frequency)'
                        ELSE '10+ Orders (Power Buyers)'
                    END AS bracket,
                    CASE 
                        WHEN order_count = 1 THEN 1
                        WHEN order_count BETWEEN 2 AND 3 THEN 2
                        WHEN order_count BETWEEN 4 AND 6 THEN 3
                        WHEN order_count BETWEEN 7 AND 9 THEN 4
                        ELSE 5
                    END AS bracket_order
                FROM customer_totals
            )
            SELECT 
                bracket,
                COUNT(*) AS customer_count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_totals), 1) AS customer_pct,
                SUM(order_count) AS total_orders,
                ROUND(SUM(total_spend), 2) AS total_revenue,
                ROUND(AVG(total_spend), 2) AS avg_spend_per_customer
            FROM bracketed
            GROUP BY bracket, bracket_order
            ORDER BY bracket_order ASC;
        """
        return self.execute_query(query)

    def get_customer_profiles(
        self,
        limit: int = 50,
        sort_by: str = "total_spend",
        ascending: bool = False,
        segment: Optional[str] = None,
        min_orders: Optional[int] = None
    ) -> List[CustomerProfile]:
        """
        Return customer-level behavioral profiles with strict PII masking:
        - Names are masked to 'First Initial.' (e.g. 'Emma S.')
        - Phone numbers, cleartext emails, and street addresses are omitted
        - Fully aggregates spend, order frequency, returns, and reviews
        """
        where_clauses = ["1=1"]
        if segment:
            where_clauses.append(f"c.customer_segment = '{segment}'")
        if min_orders:
            where_clauses.append(f"COALESCE(co.order_count, 0) >= {min_orders}")

        filter_clause = " AND ".join(where_clauses)

        query = f"""
            WITH cust_orders AS (
                SELECT 
                    customer_id,
                    COUNT(DISTINCT order_id) AS order_count,
                    COALESCE(SUM(total_amount), 0.0) AS total_spend,
                    MIN(order_date) AS first_order,
                    MAX(order_date) AS last_order
                FROM orders
                WHERE status = 'completed'
                GROUP BY customer_id
            ),
            cust_returns AS (
                SELECT 
                    customer_id,
                    COUNT(DISTINCT return_id) AS returns_count,
                    COALESCE(SUM(refund_amount), 0.0) AS total_refunds
                FROM returns
                GROUP BY customer_id
            ),
            cust_reviews AS (
                SELECT 
                    customer_id,
                    COUNT(DISTINCT review_id) AS reviews_count,
                    ROUND(AVG(rating), 2) AS avg_rating_given
                FROM reviews
                GROUP BY customer_id
            )
            SELECT 
                c.customer_id,
                c.first_name,
                c.last_name,
                c.city,
                c.country,
                c.customer_segment,
                COALESCE(co.order_count, 0) AS order_count,
                ROUND(COALESCE(co.total_spend, 0.0), 2) AS total_spend,
                ROUND(
                    CASE 
                        WHEN COALESCE(co.order_count, 0) > 0 
                        THEN co.total_spend / co.order_count 
                        ELSE 0.0 
                    END, 2
                ) AS average_order_value,
                COALESCE(co.first_order, 'Never') AS first_order_date,
                COALESCE(co.last_order, 'Never') AS last_order_date,
                COALESCE(cr.returns_count, 0) AS returns_count,
                ROUND(COALESCE(cr.total_refunds, 0.0), 2) AS total_refunds,
                ROUND(
                    CASE 
                        WHEN COALESCE(co.order_count, 0) > 0 
                        THEN (COALESCE(cr.returns_count, 0) * 100.0) / co.order_count 
                        ELSE 0.0 
                    END, 2
                ) AS return_rate_pct,
                COALESCE(rev.reviews_count, 0) AS reviews_count,
                COALESCE(rev.avg_rating_given, 0.0) AS average_rating_given
            FROM customers c
            LEFT JOIN cust_orders co ON c.customer_id = co.customer_id
            LEFT JOIN cust_returns cr ON c.customer_id = cr.customer_id
            LEFT JOIN cust_reviews rev ON c.customer_id = rev.customer_id
            WHERE {filter_clause}
            ORDER BY {sort_by} {"ASC" if ascending else "DESC"}
            LIMIT {limit};
        """
        rows = self.execute_query(query)
        profiles: List[CustomerProfile] = []

        for r in rows:
            # PII Masking: "Emma S."
            first = r["first_name"] or "Customer"
            last_initial = f"{r['last_name'][0]}." if r["last_name"] else ""
            display_name = f"{first} {last_initial}".strip()

            last_order = r["last_order_date"]
            if last_order != "Never":
                try:
                    last_dt = datetime.strptime(last_order[:10], "%Y-%m-%d")
                    # Calculate days from arbitrary baseline (e.g. 2026-03-01)
                    days_since = max(0, (datetime(2026, 3, 1) - last_dt).days)
                except Exception:
                    days_since = 0
            else:
                days_since = 999

            profiles.append(
                CustomerProfile(
                    customer_id=r["customer_id"],
                    display_name=display_name,
                    city=r["city"] or "Unknown",
                    country=r["country"] or "USA",
                    segment=r["customer_segment"],
                    order_count=r["order_count"],
                    total_spend=r["total_spend"],
                    average_order_value=r["average_order_value"],
                    first_order_date=r["first_order_date"][:10] if r["first_order_date"] != "Never" else "Never",
                    last_order_date=r["last_order_date"][:10] if r["last_order_date"] != "Never" else "Never",
                    days_since_last_order=days_since,
                    returns_count=r["returns_count"],
                    total_refunds=r["total_refunds"],
                    return_rate_pct=r["return_rate_pct"],
                    reviews_count=r["reviews_count"],
                    average_rating_given=r["average_rating_given"],
                    is_repeat_buyer=r["order_count"] >= 2,
                )
            )

        return profiles

    def get_customer_detail(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single customer's purchase history, review activity, and return events.
        """
        cust_query = f"""
            SELECT customer_id, first_name, last_name, city, country, customer_segment, created_at
            FROM customers
            WHERE customer_id = {customer_id};
        """
        c_rows = self.execute_query(cust_query)
        if not c_rows:
            return None

        c = c_rows[0]
        first = c["first_name"] or "Customer"
        last_init = f"{c['last_name'][0]}." if c["last_name"] else ""
        masked_name = f"{first} {last_init}".strip()

        # Orders placed
        orders_query = f"""
            SELECT order_id, order_date, status, total_amount
            FROM orders
            WHERE customer_id = {customer_id}
            ORDER BY order_date DESC;
        """
        orders = self.execute_query(orders_query)

        # Returns filed
        returns_query = f"""
            SELECT r.return_id, r.order_id, p.title, r.return_reason, r.refund_amount, r.return_date
            FROM returns r
            JOIN products p ON r.product_id = p.product_id
            WHERE r.customer_id = {customer_id}
            ORDER BY r.return_date DESC;
        """
        returns_list = self.execute_query(returns_query)

        # Reviews written
        reviews_query = f"""
            SELECT rev.review_id, p.title, rev.rating, rev.title AS review_headline,
                   rev.comment, ri.sentiment_label, rev.review_date
            FROM reviews rev
            JOIN products p ON rev.product_id = p.product_id
            LEFT JOIN review_insights ri ON rev.review_id = ri.review_id
            WHERE rev.customer_id = {customer_id}
            ORDER BY rev.review_date DESC;
        """
        reviews_list = self.execute_query(reviews_query)

        completed_orders = [o for o in orders if o["status"] == "completed"]
        total_spend = sum(float(o["total_amount"] or 0) for o in completed_orders)

        return {
            "customer_id": customer_id,
            "display_name": masked_name,
            "city": c["city"],
            "country": c["country"],
            "segment": c["customer_segment"],
            "registration_date": str(c["created_at"])[:10],
            "total_orders": len(orders),
            "completed_orders": len(completed_orders),
            "total_spend": round(total_spend, 2),
            "average_order_value": round(self.safe_divide(total_spend, len(completed_orders)), 2),
            "orders": orders,
            "returns": returns_list,
            "reviews": reviews_list,
        }

    def get_geographic_distribution(self, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Aggregate customer counts, completed orders, and net revenue by City/Country.
        """
        query = f"""
            SELECT 
                c.city,
                c.country,
                COUNT(DISTINCT c.customer_id) AS customer_count,
                COUNT(DISTINCT o.order_id) AS total_orders,
                ROUND(COALESCE(SUM(o.total_amount), 0.0), 2) AS total_revenue,
                ROUND(
                    AVG(CASE WHEN o.status = 'completed' THEN o.total_amount ELSE NULL END), 2
                ) AS average_order_value
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
            GROUP BY c.country, c.city
            ORDER BY total_revenue DESC
            LIMIT {limit};
        """
        return self.execute_query(query)
