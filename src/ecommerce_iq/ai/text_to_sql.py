"""
Schema-Grounded Text-to-SQL Generator.

Translates natural language questions from business owners into optimized,
syntactically valid, schema-grounded SQL queries. Supports deterministic intent
matching for core executive questions and pluggable LLM generation.
"""

import re
from typing import Any, Dict, Optional, Tuple
from ecommerce_iq.ai.prompts import TEXT_TO_SQL_SYSTEM_PROMPT


class TextToSQLGenerator:
    """
    Converts natural language business questions into safe, schema-grounded SQL queries.
    """

    def __init__(self, llm_client: Optional[Any] = None, schema_metadata: Optional[dict] = None) -> None:
        self.llm = llm_client
        self.schema_metadata = schema_metadata

    def get_intent_category(self, query: str) -> str:
        """Categorize user query to guide answer synthesis."""
        q = query.lower().strip()

        if any(w in q for w in ("return", "refund", "rma", "defective", "damaged")):
            return "returns"
        elif any(w in q for w in ("review", "rating", "csat", "complaint", "feedback", "praise", "sentiment", "star")):
            return "reviews"
        elif any(w in q for w in ("repeat", "lifetime value", "ltv", "segment", "churn", "customer")):
            return "customers"
        elif any(w in q for w in ("underperform", "dead stock", "slow moving", "laggard", "lowest sales")):
            return "underperforming"
        elif any(w in q for w in ("top", "best", "bestseller", "most sold", "highest revenue", "most units")):
            return "top_products"
        elif any(w in q for w in ("category", "categories")):
            return "categories"
        elif any(w in q for w in ("aov", "average order value", "order count", "orders")):
            return "orders"
        elif any(w in q for w in ("revenue", "sales", "made", "income", "profit", "earnings")):
            return "revenue"
        elif any(w in q for w in ("aurasound", "puffer", "projector", "dumbbell", "espresso", "kettle", "knife")):
            return "product_lookup"
        return "general"

    def _extract_limit(self, query: str, default: int = 5) -> int:
        """Extract requested numeric count like 'top 3', 'top 10'."""
        match = re.search(r"\b(?:top|limit|first|best)\s+(\d+)\b", query.lower())
        if match:
            return min(50, max(1, int(match.group(1))))
        return default

    def _extract_year(self, query: str) -> Optional[int]:
        """Extract 4-digit year like 2025 or 2026."""
        match = re.search(r"\b(202[4-6])\b", query)
        if match:
            return int(match.group(1))
        return None

    def _extract_month(self, query: str) -> Optional[Tuple[int, int]]:
        """Extract month name and return (year, month)."""
        month_map = {
            "january": 1, "jan": 1, "february": 2, "feb": 2,
            "march": 3, "mar": 3, "april": 4, "apr": 4,
            "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
            "august": 8, "aug": 8, "september": 9, "sep": 9,
            "october": 10, "oct": 10, "november": 11, "nov": 11,
            "december": 12, "dec": 12
        }
        q_lower = query.lower()
        for m_name, m_num in month_map.items():
            if re.search(rf"\b{m_name}\b", q_lower):
                year = self._extract_year(query) or 2025
                return (year, m_num)
        return None

    def generate_sql(self, natural_language_query: str) -> str:
        """
        Produce a safe, schema-grounded SQL query from a user question.
        Uses deterministic intent matching with parameter extraction,
        falling back to LLM generation if configured.
        """
        q = natural_language_query.lower().strip()
        tokens = natural_language_query.strip().split()
        first_token = tokens[0].upper() if tokens else ""

        # Direct SQL statements or injection attempts: pass through to guardrail for AST security verification
        if first_token in ("SELECT", "WITH", "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE", "PRAGMA", "ATTACH") or ";" in natural_language_query:
            return natural_language_query.strip()

        limit = self._extract_limit(q, default=5)
        month_info = self._extract_month(q)
        year_info = self._extract_year(q)

        # ----------------------------------------------------------------------
        # 1. Revenue & Sales Inquiries
        # ----------------------------------------------------------------------
        if ("revenue" in q or "sales" in q or "made" in q or "income" in q) and not any(
            w in q for w in ("product", "category", "why", "decrease", "drop")
        ):
            if month_info:
                yr, mo = month_info
                mo_str = f"{mo:02d}"
                return (
                    f"SELECT "
                    f"COUNT(DISTINCT order_id) AS total_orders, "
                    f"ROUND(SUM(total_amount), 2) AS total_revenue, "
                    f"ROUND(AVG(total_amount), 2) AS average_order_value "
                    f"FROM orders "
                    f"WHERE status = 'completed' "
                    f"AND strftime('%Y-%m', order_date) = '{yr}-{mo_str}';"
                )
            elif year_info:
                return (
                    f"SELECT "
                    f"COUNT(DISTINCT order_id) AS total_orders, "
                    f"ROUND(SUM(total_amount), 2) AS total_revenue, "
                    f"ROUND(AVG(total_amount), 2) AS average_order_value "
                    f"FROM orders "
                    f"WHERE status = 'completed' "
                    f"AND strftime('%Y', order_date) = '{year_info}';"
                )
            elif "by month" in q or "monthly" in q:
                return (
                    "SELECT "
                    "strftime('%Y-%m', order_date) AS month, "
                    "COUNT(DISTINCT order_id) AS total_orders, "
                    "ROUND(SUM(total_amount), 2) AS total_revenue "
                    "FROM orders "
                    "WHERE status = 'completed' "
                    "GROUP BY month "
                    "ORDER BY month ASC;"
                )
            else:
                return (
                    "SELECT "
                    "COUNT(DISTINCT order_id) AS total_orders, "
                    "ROUND(SUM(total_amount), 2) AS total_revenue, "
                    "ROUND(AVG(total_amount), 2) AS average_order_value "
                    "FROM orders "
                    "WHERE status = 'completed';"
                )

        # ----------------------------------------------------------------------
        # 2. Top / Bestselling Products
        # ----------------------------------------------------------------------
        if any(w in q for w in ("bestseller", "best seller", "best-selling", "top seller", "most sold")) or (
            any(w in q for w in ("top", "best", "popular")) and any(w in q for w in ("product", "item", "sku", "seller", "selling"))
        ):
            if "unit" in q or "volume" in q or "most sold" in q:
                return (
                    f"SELECT p.product_id, p.sku, p.title, "
                    f"SUM(oi.quantity) AS units_sold, "
                    f"ROUND(SUM(oi.item_total), 2) AS total_revenue "
                    f"FROM order_items oi "
                    f"JOIN orders o ON oi.order_id = o.order_id "
                    f"JOIN products p ON oi.product_id = p.product_id "
                    f"WHERE o.status = 'completed' "
                    f"GROUP BY p.product_id, p.sku, p.title "
                    f"ORDER BY units_sold DESC "
                    f"LIMIT {limit};"
                )
            else:
                return (
                    f"SELECT p.product_id, p.sku, p.title, "
                    f"SUM(oi.quantity) AS units_sold, "
                    f"ROUND(SUM(oi.item_total), 2) AS total_revenue "
                    f"FROM order_items oi "
                    f"JOIN orders o ON oi.order_id = o.order_id "
                    f"JOIN products p ON oi.product_id = p.product_id "
                    f"WHERE o.status = 'completed' "
                    f"GROUP BY p.product_id, p.sku, p.title "
                    f"ORDER BY total_revenue DESC "
                    f"LIMIT {limit};"
                )

        # ----------------------------------------------------------------------
        # 3. Underperforming / Dead Stock Products
        # ----------------------------------------------------------------------
        if any(w in q for w in ("underperform", "dead stock", "worst", "lowest sales", "slow moving")):
            return (
                f"SELECT p.product_id, p.sku, p.title, "
                f"COALESCE(SUM(oi.quantity), 0) AS units_sold, "
                f"ROUND(COALESCE(SUM(oi.item_total), 0.0), 2) AS total_revenue "
                f"FROM products p "
                f"LEFT JOIN order_items oi ON p.product_id = oi.product_id "
                f"LEFT JOIN orders o ON oi.order_id = o.order_id AND o.status = 'completed' "
                f"GROUP BY p.product_id, p.sku, p.title "
                f"ORDER BY total_revenue ASC, units_sold ASC "
                f"LIMIT {limit};"
            )

        # ----------------------------------------------------------------------
        # 4. Returns & Refunds
        # ----------------------------------------------------------------------
        if "return" in q or "refund" in q:
            if "reason" in q:
                return (
                    "SELECT return_reason, COUNT(*) AS return_count, "
                    "ROUND(SUM(refund_amount), 2) AS total_refunds "
                    "FROM returns "
                    "GROUP BY return_reason "
                    "ORDER BY return_count DESC;"
                )
            elif "rate" in q or "highest" in q or "product" in q:
                return (
                    f"WITH prod_sold AS ("
                    f"SELECT product_id, SUM(quantity) AS units_sold "
                    f"FROM order_items GROUP BY product_id"
                    f"), "
                    f"prod_ret AS ("
                    f"SELECT product_id, COUNT(*) AS return_count, SUM(quantity_returned) AS units_returned, SUM(refund_amount) AS total_refunds "
                    f"FROM returns GROUP BY product_id"
                    f") "
                    f"SELECT p.sku, p.title, ps.units_sold, COALESCE(pr.units_returned, 0) AS units_returned, "
                    f"ROUND(COALESCE(pr.units_returned, 0) * 100.0 / ps.units_sold, 1) AS return_rate_pct, "
                    f"ROUND(COALESCE(pr.total_refunds, 0.0), 2) AS total_refunds "
                    f"FROM products p "
                    f"JOIN prod_sold ps ON p.product_id = ps.product_id "
                    f"LEFT JOIN prod_ret pr ON p.product_id = pr.product_id "
                    f"ORDER BY return_rate_pct DESC "
                    f"LIMIT {limit};"
                )
            else:
                return (
                    "SELECT COUNT(*) AS total_return_events, "
                    "SUM(quantity_returned) AS total_units_returned, "
                    "ROUND(SUM(refund_amount), 2) AS total_refund_amount "
                    "FROM returns;"
                )

        # ----------------------------------------------------------------------
        # 5. Customer Reviews & Feedback
        # ----------------------------------------------------------------------
        if any(w in q for w in ("review", "rating", "csat", "complaint", "feedback", "sentiment")):
            if "complaint" in q or "negative" in q:
                return (
                    f"SELECT COALESCE(ri.detected_issue, ri.primary_topic) AS complaint, "
                    f"COUNT(*) AS complaint_count, "
                    f"ROUND(AVG(r.rating), 2) AS avg_rating "
                    f"FROM reviews r "
                    f"JOIN review_insights ri ON r.review_id = ri.review_id "
                    f"WHERE ri.sentiment_label = 'negative' "
                    f"GROUP BY complaint "
                    f"ORDER BY complaint_count DESC "
                    f"LIMIT {limit};"
                )
            elif "sentiment" in q:
                return (
                    "SELECT ri.sentiment_label, COUNT(*) AS count, "
                    "ROUND(AVG(r.rating), 2) AS average_rating "
                    "FROM reviews r "
                    "JOIN review_insights ri ON r.review_id = ri.review_id "
                    "GROUP BY ri.sentiment_label "
                    "ORDER BY count DESC;"
                )
            else:
                return (
                    "SELECT COUNT(*) AS total_reviews, "
                    "ROUND(AVG(rating), 2) AS average_rating, "
                    "SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) AS positive_reviews, "
                    "SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) AS negative_reviews "
                    "FROM reviews;"
                )

        # ----------------------------------------------------------------------
        # 6. Customer Demographics, Retention & LTV
        # ----------------------------------------------------------------------
        if any(w in q for w in ("customer", "repeat", "ltv", "lifetime value", "churn")):
            if "repeat" in q:
                return (
                    "WITH cust_orders AS ("
                    "SELECT customer_id, COUNT(DISTINCT order_id) AS order_cnt "
                    "FROM orders WHERE status = 'completed' GROUP BY customer_id"
                    ") "
                    "SELECT "
                    "COUNT(*) AS total_purchasers, "
                    "SUM(CASE WHEN order_cnt >= 2 THEN 1 ELSE 0 END) AS repeat_buyers, "
                    "ROUND(SUM(CASE WHEN order_cnt >= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS repeat_rate_pct "
                    "FROM cust_orders;"
                )
            elif "segment" in q:
                return (
                    "SELECT customer_segment, COUNT(*) AS customer_count "
                    "FROM customers "
                    "GROUP BY customer_segment "
                    "ORDER BY customer_count DESC;"
                )
            else:
                return (
                    "SELECT COUNT(*) AS total_registered, "
                    "ROUND(AVG(order_count), 2) AS avg_orders_per_customer, "
                    "ROUND(AVG(total_spend), 2) AS avg_customer_ltv "
                    "FROM ("
                    "SELECT c.customer_id, COUNT(o.order_id) AS order_count, SUM(o.total_amount) AS total_spend "
                    "FROM customers c "
                    "JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed' "
                    "GROUP BY c.customer_id"
                    ");"
                )

        # ----------------------------------------------------------------------
        # 7. Category Performance
        # ----------------------------------------------------------------------
        if "category" in q:
            return (
                "SELECT c.name AS category_name, "
                "COUNT(DISTINCT oi.order_id) AS order_count, "
                "SUM(oi.quantity) AS units_sold, "
                "ROUND(SUM(oi.item_total), 2) AS gross_revenue "
                "FROM categories c "
                "JOIN products p ON c.category_id = p.category_id "
                "JOIN order_items oi ON p.product_id = oi.product_id "
                "JOIN orders o ON oi.order_id = o.order_id AND o.status = 'completed' "
                "GROUP BY c.category_id, c.name "
                "ORDER BY gross_revenue DESC;"
            )

        # ----------------------------------------------------------------------
        # 8. Specific Product Lookup (AuraSound, Puffer, Projector, etc.)
        # ----------------------------------------------------------------------
        specific_prod_terms = {
            "aurasound": ("PROD-ELEC-001", "AuraSound Pro Wireless ANC Headphones"),
            "headphone": ("PROD-ELEC-001", "AuraSound Pro Wireless ANC Headphones"),
            "puffer": ("PROD-APP-001", "Apex Thermal Puffer Winter Jacket"),
            "jacket": ("PROD-APP-001", "Apex Thermal Puffer Winter Jacket"),
            "projector": ("PROD-ELEC-003", "UltraVision 4K Smart Cinema Projector"),
            "dumbbell": ("PROD-SPRT-001", "IronGrip 55lb Fast-Adjustable Dumbbell Pair"),
            "espresso": ("PROD-HOME-001", "BaristaTouch Automatic Espresso & Latte Machine"),
        }
        for term, (sku, title) in specific_prod_terms.items():
            if term in q:
                return (
                    f"SELECT p.sku, p.title, c.name AS category, "
                    f"SUM(oi.quantity) AS units_sold, "
                    f"ROUND(SUM(oi.item_total), 2) AS total_revenue, "
                    f"COALESCE(r.avg_rating, 0.0) AS avg_rating "
                    f"FROM products p "
                    f"JOIN categories c ON p.category_id = c.category_id "
                    f"LEFT JOIN order_items oi ON p.product_id = oi.product_id "
                    f"LEFT JOIN orders o ON oi.order_id = o.order_id AND o.status = 'completed' "
                    f"LEFT JOIN (SELECT product_id, ROUND(AVG(rating), 2) AS avg_rating FROM reviews GROUP BY product_id) r ON p.product_id = r.product_id "
                    f"WHERE p.sku = '{sku}' "
                    f"GROUP BY p.product_id, p.sku, p.title, c.name;"
                )

        # ----------------------------------------------------------------------
        # 9. LLM Fallback (if configured)
        # ----------------------------------------------------------------------
        if self.llm:
            try:
                prompt = f"Convert this question into a single read-only SQLite SELECT query:\nQuestion: {natural_language_query}"
                generated = self.llm.generate_text(prompt, system_instruction=TEXT_TO_SQL_SYSTEM_PROMPT)
                cleaned = generated.strip().strip("`").replace("sql\n", "").strip()
                if cleaned.upper().startswith("SELECT") or cleaned.upper().startswith("WITH"):
                    return cleaned
            except Exception:
                pass

        # ----------------------------------------------------------------------
        # 10. Default General Performance Summary Query
        # ----------------------------------------------------------------------
        return (
            "SELECT "
            "COUNT(DISTINCT order_id) AS total_orders, "
            "ROUND(SUM(total_amount), 2) AS total_revenue, "
            "ROUND(AVG(total_amount), 2) AS average_order_value "
            "FROM orders "
            "WHERE status = 'completed';"
        )
