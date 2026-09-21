"""
Customer Review Analysis and Sentiment Intelligence Engine.

Performs deterministic review analytics:
- Rating distribution and CSAT scorecards
- Positive, neutral, and negative sentiment breakdowns
- Recurring defect issue clustering and positive feature themes
- Clear architectural separation between raw customer input and derived insights
- PII-protected customer attribution
"""

from datetime import date
from typing import Any, Dict, List, Optional
from ecommerce_iq.ai.sentiment import SentimentAnalyzer
from ecommerce_iq.analytics.base import BaseAnalyticsEngine
from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.models.schemas import (
    DerivedReviewInsight,
    EnrichedReviewRecord,
    ProductReviewAnalysis,
    RatingDistributionItem,
    RawReviewFeedback,
    ReviewSentimentSummary,
    ThemeCluster,
)


class ReviewAnalyticsEngine(BaseAnalyticsEngine):
    """
    Analyzes customer feedback, rating patterns, sentiment polarity,
    and product-specific issue themes from the database.
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None) -> None:
        super().__init__(db_manager)
        self.analyzer = SentimentAnalyzer()

    @staticmethod
    def _mask_customer_name(first_name: Optional[str], last_name: Optional[str]) -> str:
        """Format customer name to protect PII: 'First L.'"""
        first = (first_name or "Customer").strip()
        last_init = f" {last_name[0].upper()}." if last_name else ""
        return f"{first}{last_init}".strip()

    def get_overall_review_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> ReviewSentimentSummary:
        """
        Compute platform-wide review and sentiment scorecard.
        """
        date_filter = self._format_date_filter("r.review_date", start_date, end_date)

        query = f"""
            SELECT 
                COUNT(r.review_id) AS total_reviews,
                ROUND(AVG(r.rating), 2) AS average_rating,
                SUM(CASE WHEN ri.sentiment_label = 'positive' THEN 1 ELSE 0 END) AS positive_count,
                SUM(CASE WHEN ri.sentiment_label = 'neutral' THEN 1 ELSE 0 END) AS neutral_count,
                SUM(CASE WHEN ri.sentiment_label = 'negative' THEN 1 ELSE 0 END) AS negative_count
            FROM reviews r
            LEFT JOIN review_insights ri ON r.review_id = ri.review_id
            WHERE 1=1 {date_filter};
        """
        rows = self.execute_query(query)
        r = rows[0] if rows else {}

        total = int(r.get("total_reviews") or 0)
        avg_rating = float(r.get("average_rating") or 0.0)
        pos_cnt = int(r.get("positive_count") or 0)
        neu_cnt = int(r.get("neutral_count") or 0)
        neg_cnt = int(r.get("negative_count") or 0)

        pos_pct = round(self.safe_divide(float(pos_cnt), float(total)) * 100.0, 1)
        neg_pct = round(self.safe_divide(float(neg_cnt), float(total)) * 100.0, 1)

        # Extract top complaints (from negative reviews)
        complaint_query = f"""
            SELECT 
                COALESCE(ri.detected_issue, ri.primary_topic) AS issue,
                COUNT(*) AS cnt
            FROM reviews r
            JOIN review_insights ri ON r.review_id = ri.review_id
            WHERE ri.sentiment_label = 'negative' {date_filter}
            GROUP BY issue
            ORDER BY cnt DESC
            LIMIT 5;
        """
        complaint_rows = self.execute_query(complaint_query)
        top_complaints = [f"{row['issue']} ({row['cnt']} complaints)" for row in complaint_rows]

        # Extract top praises (from positive reviews)
        praise_query = f"""
            SELECT 
                ri.primary_topic AS topic,
                COUNT(*) AS cnt
            FROM reviews r
            JOIN review_insights ri ON r.review_id = ri.review_id
            WHERE ri.sentiment_label = 'positive' {date_filter}
            GROUP BY topic
            ORDER BY cnt DESC
            LIMIT 5;
        """
        praise_rows = self.execute_query(praise_query)
        top_praises = [f"{row['topic']} praise ({row['cnt']} mentions)" for row in praise_rows]

        return ReviewSentimentSummary(
            total_reviews=total,
            average_rating=avg_rating,
            positive_count=pos_cnt,
            neutral_count=neu_cnt,
            negative_count=neg_cnt,
            positive_percentage=pos_pct,
            negative_percentage=neg_pct,
            top_complaints=top_complaints,
            top_praises=top_praises,
        )

    def get_rating_distribution(
        self,
        product_id: Optional[int] = None,
        category_id: Optional[int] = None
    ) -> List[RatingDistributionItem]:
        """
        Calculate the 1-star to 5-star distribution, average sentiment polarity,
        and verified purchase ratio across the catalog or filtered by SKU/category.
        """
        where_clauses = ["1=1"]
        if product_id:
            where_clauses.append(f"r.product_id = {product_id}")
        if category_id:
            where_clauses.append(f"p.category_id = {category_id}")

        filter_clause = " AND ".join(where_clauses)

        query = f"""
            SELECT 
                r.rating,
                COUNT(r.review_id) AS review_count,
                ROUND(AVG(COALESCE(ri.sentiment_score, 0.0)), 4) AS avg_sentiment,
                SUM(CASE WHEN r.verified_purchase = 1 THEN 1 ELSE 0 END) AS verified_count
            FROM reviews r
            JOIN products p ON r.product_id = p.product_id
            LEFT JOIN review_insights ri ON r.review_id = ri.review_id
            WHERE {filter_clause}
            GROUP BY r.rating
            ORDER BY r.rating ASC;
        """
        rows = self.execute_query(query)
        total_reviews = sum(int(row["review_count"]) for row in rows)

        # Ensure all ratings 1 to 5 are populated
        data_by_rating = {int(row["rating"]): row for row in rows}
        distribution: List[RatingDistributionItem] = []

        for star in range(1, 6):
            if star in data_by_rating:
                row = data_by_rating[star]
                cnt = int(row["review_count"])
                pct = round(self.safe_divide(float(cnt), float(total_reviews)) * 100.0, 1)
                avg_sent = float(row["avg_sentiment"] or 0.0)
                ver_cnt = int(row["verified_count"] or 0)
                ver_pct = round(self.safe_divide(float(ver_cnt), float(cnt)) * 100.0, 1)
            else:
                cnt = 0
                pct = 0.0
                avg_sent = 0.0
                ver_pct = 100.0

            distribution.append(
                RatingDistributionItem(
                    rating=star,
                    review_count=cnt,
                    percentage_of_total=pct,
                    average_sentiment_score=avg_sent,
                    verified_percentage=ver_pct,
                )
            )

        return distribution

    def get_recurring_issues(
        self,
        limit: int = 10,
        min_occurrences: int = 2
    ) -> List[ThemeCluster]:
        """
        Identify recurring negative customer issues with verbatim quotes and affected products.
        """
        query = f"""
            SELECT 
                COALESCE(ri.detected_issue, ri.primary_topic) AS issue_title,
                ri.primary_topic AS topic,
                COUNT(r.review_id) AS occurrence_count,
                ROUND(AVG(r.rating), 2) AS avg_rating,
                GROUP_CONCAT(DISTINCT p.title) AS products_affected
            FROM reviews r
            JOIN products p ON r.product_id = p.product_id
            JOIN review_insights ri ON r.review_id = ri.review_id
            WHERE ri.sentiment_label = 'negative'
            GROUP BY issue_title, ri.primary_topic
            HAVING occurrence_count >= {min_occurrences}
            ORDER BY occurrence_count DESC
            LIMIT {limit};
        """
        issue_rows = self.execute_query(query)

        # Get total negative reviews for percentage calculation
        total_neg_query = "SELECT COUNT(*) AS total FROM review_insights WHERE sentiment_label = 'negative';"
        total_neg = int(self.execute_query(total_neg_query)[0]["total"] or 1)

        clusters: List[ThemeCluster] = []
        for row in issue_rows:
            issue = row["issue_title"]
            cnt = int(row["occurrence_count"])
            pct = round((cnt / total_neg) * 100.0, 1)

            # Sample verbatim customer quotes for this issue
            quotes_query = f"""
                SELECT r.title, r.comment
                FROM reviews r
                JOIN review_insights ri ON r.review_id = ri.review_id
                WHERE (ri.detected_issue = '{issue}' OR ri.primary_topic = '{issue}')
                  AND ri.sentiment_label = 'negative'
                LIMIT 2;
            """
            quotes_rows = self.execute_query(quotes_query)
            sample_quotes = [
                f'"{q["title"]}: {q["comment"]}"' if q["title"] else f'"{q["comment"]}"'
                for q in quotes_rows
            ]

            raw_prods = row.get("products_affected") or ""
            prods = [p.strip() for p in raw_prods.split(",") if p.strip()][:3]

            severity = "Critical" if cnt >= 40 or float(row["avg_rating"]) <= 1.8 else "Warning"

            clusters.append(
                ThemeCluster(
                    theme_title=issue,
                    topic=row["topic"],
                    review_count=cnt,
                    percentage_of_reviews=pct,
                    severity_or_sentiment=severity,
                    affected_products=prods,
                    sample_quotes=sample_quotes,
                )
            )

        return clusters

    def get_positive_themes(
        self,
        limit: int = 10,
        min_occurrences: int = 2
    ) -> List[ThemeCluster]:
        """
        Identify recurring positive feedback themes and praised product features.
        """
        query = f"""
            SELECT 
                ri.primary_topic AS topic,
                COUNT(r.review_id) AS occurrence_count,
                ROUND(AVG(r.rating), 2) AS avg_rating,
                GROUP_CONCAT(DISTINCT p.title) AS praised_products
            FROM reviews r
            JOIN products p ON r.product_id = p.product_id
            JOIN review_insights ri ON r.review_id = ri.review_id
            WHERE ri.sentiment_label = 'positive'
            GROUP BY ri.primary_topic
            HAVING occurrence_count >= {min_occurrences}
            ORDER BY occurrence_count DESC
            LIMIT {limit};
        """
        rows = self.execute_query(query)

        total_pos_query = "SELECT COUNT(*) AS total FROM review_insights WHERE sentiment_label = 'positive';"
        total_pos = int(self.execute_query(total_pos_query)[0]["total"] or 1)

        themes: List[ThemeCluster] = []
        for row in rows:
            topic = row["topic"]
            cnt = int(row["occurrence_count"])
            pct = round((cnt / total_pos) * 100.0, 1)

            # Sample customer praises
            quotes_query = f"""
                SELECT r.title, r.comment
                FROM reviews r
                JOIN review_insights ri ON r.review_id = ri.review_id
                WHERE ri.primary_topic = '{topic}' AND ri.sentiment_label = 'positive'
                LIMIT 2;
            """
            quotes_rows = self.execute_query(quotes_query)
            sample_quotes = [
                f'"{q["title"]}: {q["comment"]}"' if q["title"] else f'"{q["comment"]}"'
                for q in quotes_rows
            ]

            raw_prods = row.get("praised_products") or ""
            prods = [p.strip() for p in raw_prods.split(",") if p.strip()][:3]

            themes.append(
                ThemeCluster(
                    theme_title=f"{topic} Excellence",
                    topic=topic,
                    review_count=cnt,
                    percentage_of_reviews=pct,
                    severity_or_sentiment="Praise",
                    affected_products=prods,
                    sample_quotes=sample_quotes,
                )
            )

        return themes

    def get_enriched_reviews(
        self,
        product_id: Optional[int] = None,
        sentiment: Optional[str] = None,
        rating: Optional[int] = None,
        limit: int = 50
    ) -> List[EnrichedReviewRecord]:
        """
        Retrieve reviews with clear structural separation between raw customer input
        and derived analytical insights, strictly enforcing customer PII masking.
        """
        where_clauses = ["1=1"]
        if product_id:
            where_clauses.append(f"r.product_id = {product_id}")
        if sentiment:
            where_clauses.append(f"ri.sentiment_label = '{sentiment}'")
        if rating:
            where_clauses.append(f"r.rating = {rating}")

        filter_clause = " AND ".join(where_clauses)

        query = f"""
            SELECT 
                r.review_id,
                r.product_id,
                p.title AS product_title,
                r.customer_id,
                c.first_name,
                c.last_name,
                r.rating,
                r.title AS review_title,
                r.comment,
                r.review_date,
                r.verified_purchase,
                r.helpful_votes,
                COALESCE(ri.sentiment_label, 'neutral') AS sentiment_label,
                COALESCE(ri.sentiment_score, 0.0) AS sentiment_score,
                COALESCE(ri.primary_topic, 'General') AS primary_topic,
                ri.detected_issue
            FROM reviews r
            JOIN products p ON r.product_id = p.product_id
            JOIN customers c ON r.customer_id = c.customer_id
            LEFT JOIN review_insights ri ON r.review_id = ri.review_id
            WHERE {filter_clause}
            ORDER BY r.review_date DESC
            LIMIT {limit};
        """
        rows = self.execute_query(query)
        enriched: List[EnrichedReviewRecord] = []

        for row in rows:
            masked_name = self._mask_customer_name(row["first_name"], row["last_name"])
            raw_feedback = RawReviewFeedback(
                review_id=row["review_id"],
                product_id=row["product_id"],
                product_title=row["product_title"],
                customer_id=row["customer_id"],
                customer_display_name=masked_name,
                rating=row["rating"],
                title=row["review_title"],
                comment=row["comment"],
                review_date=str(row["review_date"])[:19],
                verified_purchase=bool(row["verified_purchase"]),
                helpful_votes=int(row["helpful_votes"] or 0),
            )

            # Analyze text for explainable cues and rationale
            full_text = f"{row['review_title'] or ''} {row['comment']}".strip()
            analysis = self.analyzer.analyze_text(full_text, rating=row["rating"])

            derived_insight = DerivedReviewInsight(
                sentiment_label=row["sentiment_label"],
                sentiment_score=float(row["sentiment_score"]),
                primary_topic=row["primary_topic"],
                detected_issue=row["detected_issue"],
                confidence=analysis["confidence"],
                explanation=analysis["explanation"],
            )

            enriched.append(
                EnrichedReviewRecord(
                    raw_feedback=raw_feedback,
                    derived_insight=derived_insight,
                )
            )

        return enriched

    def get_product_review_analysis(self, product_id: int) -> Optional[ProductReviewAnalysis]:
        """
        Assemble a 360-degree review and sentiment profile for a single product.
        """
        prod_query = f"SELECT product_id, title, sku FROM products WHERE product_id = {product_id};"
        prod_rows = self.execute_query(prod_query)
        if not prod_rows:
            return None

        p = prod_rows[0]
        title = p["title"]
        sku = p["sku"]

        # Rating distribution
        rating_dist = self.get_rating_distribution(product_id=product_id)
        total_reviews = sum(item.review_count for item in rating_dist)
        if total_reviews > 0:
            avg_rating = round(
                sum(item.rating * item.review_count for item in rating_dist) / total_reviews, 2
            )
        else:
            avg_rating = 0.0

        # Sentiment breakdown
        sent_query = f"""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN ri.sentiment_label = 'positive' THEN 1 ELSE 0 END) AS positive,
                SUM(CASE WHEN ri.sentiment_label = 'neutral' THEN 1 ELSE 0 END) AS neutral,
                SUM(CASE WHEN ri.sentiment_label = 'negative' THEN 1 ELSE 0 END) AS negative,
                ROUND(AVG(ri.sentiment_score), 4) AS avg_polarity
            FROM reviews r
            LEFT JOIN review_insights ri ON r.review_id = ri.review_id
            WHERE r.product_id = {product_id};
        """
        s_row = self.execute_query(sent_query)[0]
        pos_cnt = int(s_row["positive"] or 0)
        neu_cnt = int(s_row["neutral"] or 0)
        neg_cnt = int(s_row["negative"] or 0)
        tot_cnt = int(s_row["total"] or 0)

        sentiment_summary = {
            "positive_count": pos_cnt,
            "neutral_count": neu_cnt,
            "negative_count": neg_cnt,
            "positive_percentage": round(self.safe_divide(float(pos_cnt), float(tot_cnt)) * 100.0, 1),
            "negative_percentage": round(self.safe_divide(float(neg_cnt), float(tot_cnt)) * 100.0, 1),
            "average_sentiment_polarity": float(s_row["avg_polarity"] or 0.0),
        }

        # Specific recurring issues for this product
        issues_query = f"""
            SELECT 
                COALESCE(ri.detected_issue, ri.primary_topic) AS issue_title,
                ri.primary_topic AS topic,
                COUNT(*) AS cnt
            FROM reviews r
            JOIN review_insights ri ON r.review_id = ri.review_id
            WHERE r.product_id = {product_id} AND ri.sentiment_label = 'negative'
            GROUP BY issue_title, ri.primary_topic
            ORDER BY cnt DESC
            LIMIT 3;
        """
        prod_issues: List[ThemeCluster] = []
        for i_row in self.execute_query(issues_query):
            cnt = int(i_row["cnt"])
            pct = round(self.safe_divide(float(cnt), float(neg_cnt)) * 100.0, 1)
            prod_issues.append(
                ThemeCluster(
                    theme_title=i_row["issue_title"],
                    topic=i_row["topic"],
                    review_count=cnt,
                    percentage_of_reviews=pct,
                    severity_or_sentiment="Critical" if pct >= 30.0 else "Warning",
                    affected_products=[title],
                    sample_quotes=[],
                )
            )

        # Specific positive themes for this product
        praise_query = f"""
            SELECT 
                ri.primary_topic AS topic,
                COUNT(*) AS cnt
            FROM reviews r
            JOIN review_insights ri ON r.review_id = ri.review_id
            WHERE r.product_id = {product_id} AND ri.sentiment_label = 'positive'
            GROUP BY ri.primary_topic
            ORDER BY cnt DESC
            LIMIT 3;
        """
        prod_praises: List[ThemeCluster] = []
        for pr_row in self.execute_query(praise_query):
            cnt = int(pr_row["cnt"])
            pct = round(self.safe_divide(float(cnt), float(pos_cnt)) * 100.0, 1)
            prod_praises.append(
                ThemeCluster(
                    theme_title=f"{pr_row['topic']} Praise",
                    topic=pr_row["topic"],
                    review_count=cnt,
                    percentage_of_reviews=pct,
                    severity_or_sentiment="Praise",
                    affected_products=[title],
                    sample_quotes=[],
                )
            )

        # Recent enriched reviews
        recent_reviews = self.get_enriched_reviews(product_id=product_id, limit=5)

        return ProductReviewAnalysis(
            product_id=product_id,
            product_title=title,
            sku=sku,
            average_rating=avg_rating,
            total_reviews=total_reviews,
            rating_distribution=rating_dist,
            sentiment_summary=sentiment_summary,
            recurring_issues=prod_issues,
            positive_themes=prod_praises,
            recent_reviews=recent_reviews,
        )

    def get_temporal_sentiment_trend(self, granularity: str = "monthly") -> List[Dict[str, Any]]:
        """
        Track rating and sentiment evolution across temporal intervals.
        """
        period_format = "%Y-%m" if granularity == "monthly" else "%Y-%W"

        query = f"""
            SELECT 
                strftime('{period_format}', r.review_date) AS period,
                COUNT(r.review_id) AS review_count,
                ROUND(AVG(r.rating), 2) AS average_rating,
                SUM(CASE WHEN ri.sentiment_label = 'positive' THEN 1 ELSE 0 END) AS positive_count,
                SUM(CASE WHEN ri.sentiment_label = 'negative' THEN 1 ELSE 0 END) AS negative_count,
                ROUND(AVG(COALESCE(ri.sentiment_score, 0.0)), 4) AS avg_sentiment_score
            FROM reviews r
            LEFT JOIN review_insights ri ON r.review_id = ri.review_id
            GROUP BY period
            ORDER BY period ASC;
        """
        rows = self.execute_query(query)
        trend: List[Dict[str, Any]] = []

        for row in rows:
            tot = int(row["review_count"])
            pos = int(row["positive_count"] or 0)
            neg = int(row["negative_count"] or 0)

            trend.append({
                "period": row["period"],
                "review_count": tot,
                "average_rating": float(row["average_rating"] or 0.0),
                "positive_count": pos,
                "negative_count": neg,
                "positive_percentage": round(self.safe_divide(float(pos), float(tot)) * 100.0, 1),
                "negative_percentage": round(self.safe_divide(float(neg), float(tot)) * 100.0, 1),
                "average_sentiment_score": float(row["avg_sentiment_score"] or 0.0),
            })

        return trend
