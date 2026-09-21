"""
Unit and Integration Tests for Customer Review Analysis and Sentiment Intelligence.

Verifies:
- Explainable SentimentAnalyzer text classification, negation inversion, and intensifiers
- Platform-wide ReviewSentimentSummary scorecard and metrics
- 1-to-5 star rating distribution calculations and sentiment correlation
- Recurring defect issue clustering with verbatim customer quotes
- Positive feature theme extraction and praised products
- ProductReviewAnalysis 360-degree SKU review profile
- Strict architectural separation between RawReviewFeedback and DerivedReviewInsight
- PII masking compliance on customer-facing review records
- Temporal monthly sentiment trends
"""

from datetime import date
from pathlib import Path
import sys
import unittest

_root = Path(__file__).resolve().parent.parent
for _p in (str(_root / "src"), str(_root)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ecommerce_iq.ai.sentiment import SentimentAnalyzer
from ecommerce_iq.analytics.reviews import ReviewAnalyticsEngine
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


class TestReviewAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseManager()
        cls.engine = ReviewAnalyticsEngine(cls.db)
        cls.analyzer = SentimentAnalyzer()

    # ==========================================================================
    # 1. Explainable Sentiment Analyzer Tests
    # ==========================================================================

    def test_sentiment_analyzer_positive_feedback(self):
        """Verify positive vocabulary detection with high polarity score and explanation."""
        text = "Hands down the best purchase I made this year. Flawless quality and arrived fast!"
        result = self.analyzer.analyze_text(text, rating=5)

        self.assertEqual(result["sentiment_label"], "positive")
        self.assertGreater(result["sentiment_score"], 0.5)
        self.assertIn("best", result["matched_positive_cues"])
        self.assertIn("flawless", result["matched_positive_cues"])
        self.assertIn("POSITIVE", result["explanation"])
        self.assertIn("positive cues", result["explanation"])

    def test_sentiment_analyzer_negative_feedback_and_issue_detection(self):
        """Verify negative defect detection, topic mapping, and root cause extraction."""
        text = "Battery dies after 20 minutes and shuts off completely. Terribly defective hardware."
        result = self.analyzer.analyze_text(text, rating=1)

        self.assertEqual(result["sentiment_label"], "negative")
        self.assertLess(result["sentiment_score"], -0.5)
        self.assertEqual(result["primary_topic"], "Battery/Hardware")
        self.assertEqual(result["detected_issue"], "Battery failure / cuts out")
        self.assertIn("defective", result["matched_negative_cues"])
        self.assertIn("NEGATIVE", result["explanation"])

    def test_sentiment_analyzer_negation_inversion(self):
        """Verify negation tokens ('not', 'never') flip positive valence into negative."""
        text = "The headphones were not good and never worked."
        result = self.analyzer.analyze_text(text)

        self.assertEqual(result["sentiment_label"], "negative")
        self.assertLess(result["sentiment_score"], 0.0)
        self.assertTrue(any("not good" in cue for cue in result["matched_negative_cues"]))
        self.assertGreater(len(result["negations_detected"]), 0)

    def test_sentiment_analyzer_intensifiers(self):
        """Verify intensifiers ('extremely', 'very') boost polarity magnitude."""
        base_res = self.analyzer.analyze_text("Good quality product.")
        intensified_res = self.analyzer.analyze_text("Extremely good quality product.")

        self.assertGreater(intensified_res["sentiment_score"], base_res["sentiment_score"])
        self.assertGreater(len(intensified_res["intensifiers_detected"]), 0)

    def test_sentiment_analyzer_batch_process(self):
        """Verify batch review processing produces structured insight dicts."""
        batch = [
            {"review_id": 101, "title": "Great", "comment": "Superb product", "rating": 5},
            {"review_id": 102, "title": "Broke", "comment": "Awful and cheap", "rating": 1},
        ]
        results = self.analyzer.batch_process_reviews(batch)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["review_id"], 101)
        self.assertEqual(results[0]["sentiment_label"], "positive")
        self.assertEqual(results[1]["review_id"], 102)
        self.assertEqual(results[1]["sentiment_label"], "negative")

    # ==========================================================================
    # 2. Review Analytics Engine Scorecard & Distributions
    # ==========================================================================

    def test_overall_review_summary(self):
        """Verify platform-wide review scorecard calculates exact database metrics."""
        summary = self.engine.get_overall_review_summary()
        self.assertIsInstance(summary, ReviewSentimentSummary)
        self.assertEqual(summary.total_reviews, 2067)
        self.assertAlmostEqual(summary.average_rating, 4.10, delta=0.05)
        self.assertGreater(summary.positive_count, 1500)
        self.assertGreater(summary.negative_count, 400)
        self.assertGreater(summary.positive_percentage, 70.0)
        self.assertGreater(summary.negative_percentage, 15.0)

        # Check complaints and praises lists
        self.assertGreater(len(summary.top_complaints), 0)
        self.assertGreater(len(summary.top_praises), 0)

    def test_rating_distribution_overall(self):
        """Verify 1-to-5 star rating distribution has all brackets and sums to 100%."""
        distribution = self.engine.get_rating_distribution()
        self.assertEqual(len(distribution), 5)

        stars = [item.rating for item in distribution]
        self.assertEqual(stars, [1, 2, 3, 4, 5])

        total_pct = sum(item.percentage_of_total for item in distribution)
        self.assertAlmostEqual(total_pct, 100.0, delta=0.5)

        # 1 and 2 star reviews have negative sentiment polarity
        r1 = next(item for item in distribution if item.rating == 1)
        r5 = next(item for item in distribution if item.rating == 5)
        self.assertLess(r1.average_sentiment_score, 0.0)
        self.assertGreater(r5.average_sentiment_score, 0.5)

    def test_rating_distribution_by_product(self):
        """Verify rating distribution for specific defective SKU (PROD-ELEC-001)."""
        dist = self.engine.get_rating_distribution(product_id=1)
        self.assertEqual(len(dist), 5)

        # PROD-ELEC-001 has high 1-star and 2-star volume due to battery defect
        r1_cnt = next(item for item in dist if item.rating == 1).review_count
        r2_cnt = next(item for item in dist if item.rating == 2).review_count
        self.assertGreater(r1_cnt + r2_cnt, 40)

    # ==========================================================================
    # 3. Recurring Issues & Positive Themes
    # ==========================================================================

    def test_recurring_issues_clustering(self):
        """Verify extraction of recurring defect themes with verbatim customer quotes."""
        issues = self.engine.get_recurring_issues(limit=5)
        self.assertGreater(len(issues), 0)

        for issue in issues:
            self.assertIsInstance(issue, ThemeCluster)
            self.assertGreater(issue.review_count, 0)
            self.assertGreater(issue.percentage_of_reviews, 0.0)
            self.assertIn(issue.severity_or_sentiment, ("Critical", "Warning"))
            self.assertGreater(len(issue.affected_products), 0)
            self.assertGreater(len(issue.sample_quotes), 0)
            # Quotes start with quote marks
            self.assertTrue(issue.sample_quotes[0].startswith('"'))

    def test_positive_themes_clustering(self):
        """Verify extraction of praised product features and excellence themes."""
        praises = self.engine.get_positive_themes(limit=5)
        self.assertGreater(len(praises), 0)

        for theme in praises:
            self.assertIsInstance(theme, ThemeCluster)
            self.assertGreater(theme.review_count, 0)
            self.assertEqual(theme.severity_or_sentiment, "Praise")
            self.assertGreater(len(theme.affected_products), 0)
            self.assertGreater(len(theme.sample_quotes), 0)

    # ==========================================================================
    # 4. Product-Level Review Profile & Raw vs Derived Separation
    # ==========================================================================

    def test_product_review_analysis(self):
        """Verify 360-degree single-product review intelligence."""
        analysis = self.engine.get_product_review_analysis(product_id=1)
        self.assertIsNotNone(analysis)
        self.assertIsInstance(analysis, ProductReviewAnalysis)
        self.assertEqual(analysis.sku, "PROD-ELEC-001")
        self.assertLess(analysis.average_rating, 2.5)  # Defective product
        self.assertGreater(analysis.sentiment_summary["negative_percentage"], 70.0)
        self.assertGreater(len(analysis.recurring_issues), 0)
        self.assertGreater(len(analysis.recent_reviews), 0)

    def test_enriched_reviews_structural_separation_and_pii(self):
        """Verify strict bifurcation between raw feedback and derived insights, with PII masking."""
        enriched = self.engine.get_enriched_reviews(limit=10)
        self.assertEqual(len(enriched), 10)

        for record in enriched:
            self.assertIsInstance(record, EnrichedReviewRecord)

            # Untouched Raw Customer Feedback
            raw = record.raw_feedback
            self.assertIsInstance(raw, RawReviewFeedback)
            self.assertGreater(raw.review_id, 0)
            self.assertGreater(raw.product_id, 0)
            self.assertTrue(1 <= raw.rating <= 5)
            self.assertGreater(len(raw.comment), 0)

            # PII Masking verification ("First L.")
            parts = raw.customer_display_name.split()
            self.assertGreaterEqual(len(parts), 2)
            self.assertTrue(parts[-1].endswith("."))
            self.assertNotIn("@", raw.customer_display_name)

            # Derived Analytical Insight
            derived = record.derived_insight
            self.assertIsInstance(derived, DerivedReviewInsight)
            self.assertIn(derived.sentiment_label, ("positive", "neutral", "negative"))
            self.assertTrue(-1.0 <= derived.sentiment_score <= 1.0)
            self.assertGreater(len(derived.primary_topic), 0)
            self.assertGreaterEqual(derived.confidence, 0.5)
            self.assertIn("score:", derived.explanation)

    def test_temporal_sentiment_trend(self):
        """Verify monthly aggregation of review counts, ratings, and sentiment splits."""
        trend = self.engine.get_temporal_sentiment_trend(granularity="monthly")
        self.assertGreater(len(trend), 12)

        for month in trend:
            self.assertIn("period", month)
            self.assertGreater(month["review_count"], 0)
            self.assertTrue(1.0 <= month["average_rating"] <= 5.0)
            self.assertGreaterEqual(month["positive_percentage"], 0.0)
            self.assertGreaterEqual(month["negative_percentage"], 0.0)


if __name__ == "__main__":
    unittest.main()
