"""
Customer Behavior and RFM Segmentation Engine.

Performs deterministic customer behavioral classification:
- Recency, Frequency, Monetary (RFM) quintile modeling
- Behavioral customer segmentation (Champions, Loyal, At Risk, Hibernating, etc.)
- Churn risk cohort identification with revenue-at-risk estimation
- Strict Personally Identifiable Information (PII) protection
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.models.schemas import ChurnRiskCustomer, RFMCustomerScore


class CustomerSegmentationEngine:
    """
    Groups customers into actionable behavioral cohorts and identifies churn risks.
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None) -> None:
        self.db = db_manager or DatabaseManager()

    def _get_anchor_date(self) -> date:
        """Find the latest order date in the database to serve as the recency anchor."""
        query = "SELECT MAX(order_date) AS max_date FROM orders WHERE status = 'completed';"
        rows = self.db.execute_query(query)
        if rows and rows[0]["max_date"]:
            return datetime.strptime(rows[0]["max_date"][:10], "%Y-%m-%d").date()
        return date(2026, 3, 1)

    @staticmethod
    def _mask_name(first_name: Optional[str], last_name: Optional[str]) -> str:
        """Strict PII masking returning 'First Initial.' (e.g. 'Emma S.')."""
        first = (first_name or "Customer").strip()
        last_init = f" {last_name[0].upper()}." if last_name else ""
        return f"{first}{last_init}".strip()

    def compute_rfm_scores(
        self,
        anchor_date: Optional[date] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Compute Recency, Frequency, and Monetary (RFM) quintiles (1-5) for active purchasers.
        Assigns standard marketing segments and returns individual profiles and segment rollups.
        """
        if anchor_date is None:
            anchor_date = self._get_anchor_date()

        query = """
            SELECT 
                c.customer_id,
                c.first_name,
                c.last_name,
                c.city,
                c.country,
                c.customer_segment,
                COUNT(DISTINCT o.order_id) AS frequency,
                COALESCE(SUM(o.total_amount), 0.0) AS monetary,
                MAX(o.order_date) AS last_order_date
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.status = 'completed'
            GROUP BY c.customer_id, c.first_name, c.last_name, c.city, c.country, c.customer_segment;
        """
        rows = self.db.execute_query(query)
        if not rows:
            return {
                "anchor_date": anchor_date.isoformat(),
                "total_customers_scored": 0,
                "segment_summary": {},
                "customers": [],
            }

        parsed_customers: List[Dict[str, Any]] = []
        for r in rows:
            last_dt = datetime.strptime(r["last_order_date"][:10], "%Y-%m-%d").date()
            recency_days = max(0, (anchor_date - last_dt).days)
            parsed_customers.append({
                "customer_id": r["customer_id"],
                "first_name": r["first_name"],
                "last_name": r["last_name"],
                "city": r["city"] or "Unknown",
                "country": r["country"] or "USA",
                "recency_days": recency_days,
                "frequency": int(r["frequency"]),
                "monetary": round(float(r["monetary"]), 2),
            })

        n = len(parsed_customers)

        # 1. Rank & Assign Recency score (Lower recency days = better = higher score 5)
        parsed_customers.sort(key=lambda x: x["recency_days"])
        for idx, item in enumerate(parsed_customers):
            # Rank 0 -> highest score (5), Rank n-1 -> lowest score (1)
            bucket = min(4, int(idx * 5 / n))
            item["r_score"] = 5 - bucket

        # 2. Rank & Assign Frequency score (Higher frequency = better = higher score 5)
        parsed_customers.sort(key=lambda x: x["frequency"])
        for idx, item in enumerate(parsed_customers):
            bucket = min(4, int(idx * 5 / n))
            item["f_score"] = 1 + bucket

        # 3. Rank & Assign Monetary score (Higher monetary = better = higher score 5)
        parsed_customers.sort(key=lambda x: x["monetary"])
        for idx, item in enumerate(parsed_customers):
            bucket = min(4, int(idx * 5 / n))
            item["m_score"] = 1 + bucket

        # 4. Map RFM Segment definitions
        scored_profiles: List[RFMCustomerScore] = []
        for item in parsed_customers:
            r = item["r_score"]
            f = item["f_score"]
            m = item["m_score"]

            if r >= 4 and f >= 4:
                seg = "Champions"
            elif r >= 3 and f >= 3:
                seg = "Loyal Customers"
            elif r >= 4 and f in (2, 3):
                seg = "Potential Loyalists"
            elif r >= 4 and f == 1:
                seg = "Recent Customers"
            elif r == 3 and f in (1, 2):
                seg = "Promising"
            elif r == 2 and f in (2, 3):
                seg = "Customers Needing Attention"
            elif r <= 2 and f >= 4:
                seg = "Can't Lose Them"
            elif r <= 2 and f == 3:
                seg = "At Risk"
            elif r == 2 and f in (1, 2):
                seg = "About to Sleep"
            elif r == 1 and f in (1, 2):
                seg = "Hibernating"
            else:
                seg = "At Risk"

            score_str = f"{r}{f}{m}"
            masked_name = self._mask_name(item["first_name"], item["last_name"])

            scored_profiles.append(
                RFMCustomerScore(
                    customer_id=item["customer_id"],
                    display_name=masked_name,
                    city=item["city"],
                    country=item["country"],
                    recency_days=item["recency_days"],
                    frequency_orders=item["frequency"],
                    monetary_spend=item["monetary"],
                    r_score=r,
                    f_score=f,
                    m_score=m,
                    rfm_score_str=score_str,
                    rfm_segment=seg,
                )
            )

        # 5. Build Aggregated Segment Summary
        segment_stats: Dict[str, Dict[str, Any]] = {}
        strategies = {
            "Champions": "Reward loyalty, offer early access to new collections and VIP incentives.",
            "Loyal Customers": "Upsell premium tiers, invite to referral programs, and solicit product reviews.",
            "Potential Loyalists": "Offer membership benefits and bundle discounts to increase frequency.",
            "Recent Customers": "Provide onboarding support and first-repeat purchase discount incentives.",
            "Promising": "Re-engage with tailored product recommendations based on past purchases.",
            "Customers Needing Attention": "Deploy time-sensitive win-back campaigns and personalized promotions.",
            "About to Sleep": "Share popular products and limited-time reactivation discounts.",
            "Can't Lose Them": "High-priority outreach, personalized win-back offers, and concierge support.",
            "At Risk": "Send personalized reactivation emails and surveys to diagnose dissatisfaction.",
            "Hibernating": "Offer deep clearance discounts or purge from active marketing lists.",
        }

        for p in scored_profiles:
            s = p.rfm_segment
            if s not in segment_stats:
                segment_stats[s] = {
                    "segment": s,
                    "customer_count": 0,
                    "total_revenue": 0.0,
                    "avg_recency_days": 0.0,
                    "avg_frequency": 0.0,
                    "avg_monetary": 0.0,
                    "strategy": strategies.get(s, "Standard engagement."),
                }
            segment_stats[s]["customer_count"] += 1
            segment_stats[s]["total_revenue"] += p.monetary_spend
            segment_stats[s]["avg_recency_days"] += p.recency_days
            segment_stats[s]["avg_frequency"] += p.frequency_orders

        # Finalize averages
        for s, stats in segment_stats.items():
            c_cnt = stats["customer_count"]
            stats["percentage_of_customers"] = round((c_cnt / n) * 100.0, 1)
            stats["total_revenue"] = round(stats["total_revenue"], 2)
            stats["avg_recency_days"] = round(stats["avg_recency_days"] / c_cnt, 1)
            stats["avg_frequency"] = round(stats["avg_frequency"] / c_cnt, 1)
            stats["avg_monetary"] = round(stats["total_revenue"] / c_cnt, 2)

        # Sort profiles by monetary spend DESC
        scored_profiles.sort(key=lambda x: x.monetary_spend, reverse=True)
        if limit:
            output_profiles = scored_profiles[:limit]
        else:
            output_profiles = scored_profiles

        return {
            "anchor_date": anchor_date.isoformat(),
            "total_customers_scored": n,
            "segment_summary": segment_stats,
            "customers": output_profiles,
        }

    def get_churn_risk_cohort(
        self,
        days_threshold: int = 90,
        min_orders: int = 2,
        limit: int = 50
    ) -> List[ChurnRiskCustomer]:
        """
        Identify high-value repeat customers who are inactive and at risk of churning.
        Categorizes risk into 'Critical', 'High', and 'Moderate' tiers with revenue-at-risk.
        """
        anchor_date = self._get_anchor_date()

        query = f"""
            WITH customer_order_summary AS (
                SELECT 
                    c.customer_id,
                    c.first_name,
                    c.last_name,
                    c.city,
                    c.country,
                    c.customer_segment,
                    COUNT(DISTINCT o.order_id) AS order_count,
                    SUM(o.total_amount) AS total_spend,
                    MAX(o.order_date) AS last_order_date
                FROM customers c
                JOIN orders o ON c.customer_id = o.customer_id
                WHERE o.status = 'completed'
                GROUP BY c.customer_id, c.first_name, c.last_name, c.city, c.country, c.customer_segment
                HAVING order_count >= {min_orders}
            )
            SELECT *
            FROM customer_order_summary
            ORDER BY total_spend DESC;
        """
        rows = self.db.execute_query(query)
        churn_candidates: List[ChurnRiskCustomer] = []

        for r in rows:
            last_dt = datetime.strptime(r["last_order_date"][:10], "%Y-%m-%d").date()
            days_since = max(0, (anchor_date - last_dt).days)

            if days_since < days_threshold:
                continue

            order_cnt = int(r["order_count"])
            total_spd = round(float(r["total_spend"]), 2)
            aov = round(total_spd / order_cnt, 2)

            # Determine risk tier
            if days_since >= 180 or (days_since >= 120 and total_spd >= 1000.0):
                risk_level = "Critical"
            elif days_since >= 120 or (days_since >= 90 and total_spd >= 500.0):
                risk_level = "High"
            else:
                risk_level = "Moderate"

            # Revenue at risk: Estimated 12-month value based on past purchasing frequency
            annualized_risk = round(aov * max(2.0, float(order_cnt) * (365.0 / max(365, days_since * 2))), 2)

            masked_name = self._mask_name(r["first_name"], r["last_name"])

            churn_candidates.append(
                ChurnRiskCustomer(
                    customer_id=r["customer_id"],
                    display_name=masked_name,
                    city=r["city"] or "Unknown",
                    country=r["country"] or "USA",
                    segment=r["customer_segment"],
                    orders_placed=order_cnt,
                    total_spend=total_spd,
                    average_order_value=aov,
                    days_since_last_order=days_since,
                    risk_level=risk_level,
                    estimated_revenue_at_risk=annualized_risk,
                )
            )

        churn_candidates.sort(key=lambda x: x.total_spend, reverse=True)
        return churn_candidates[:limit]
