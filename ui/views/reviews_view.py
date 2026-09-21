"""
Customer Feedback & Sentiment Intelligence View.

Analyzes ratings, reviews, CSAT scorecards, sentiment polarity distributions,
and clusters recurring defect themes and positive praise patterns.
"""

import streamlit as st

from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.analytics.reviews import ReviewAnalyticsEngine
from ecommerce_iq.ai.interpretation import AnalyticsInterpreter
from ui.components.cards import render_ai_insight_card
from ui.components.charts import render_rating_distribution_chart


def render_reviews_page(db: DatabaseManager, interpreter: AnalyticsInterpreter) -> None:
    """Render Customer Feedback & Sentiment analytics view."""
    st.title("💬 Customer Feedback & Sentiment Intelligence")
    st.caption("CSAT scorecards, 1-to-5 star rating distributions, recurring defect clusters, and praise analysis.")

    review_engine = ReviewAnalyticsEngine(db)
    summary = review_engine.get_overall_review_summary()
    dist_data = review_engine.get_rating_distribution()
    issues = review_engine.get_recurring_issues(limit=5)
    praises = review_engine.get_positive_themes(limit=5)

    # 1. AI Executive Interpretation
    interp = interpreter.interpret_customer_reviews(summary, recurring_issues=issues)
    render_ai_insight_card(interp)

    # 2. Metric Scorecards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Platform CSAT Score", f"{summary.average_rating:.2f} / 5.0", "★ Average Rating")
    with c2:
        st.metric("Total Verified Reviews", f"{summary.total_reviews:,}")
    with c3:
        st.metric("Positive Reviews (4-5 ★)", f"{summary.positive_percentage:.1f}%", f"{summary.positive_count:,} reviews")
    with c4:
        st.metric("Negative Reviews (1-2 ★)", f"{summary.negative_percentage:.1f}%", f"{summary.negative_count:,} reviews", delta_color="inverse")

    # 3. Rating Distribution Chart & Themes Split
    st.markdown("---")
    col_left, col_right = st.columns([1, 1])

    with col_left:
        # Format distribution data dicts
        dist_dicts = [
            {"rating": item.rating, "review_count": item.review_count}
            for item in dist_data
        ]
        st.plotly_chart(render_rating_distribution_chart(dist_dicts), use_container_width=True)

    with col_right:
        st.subheader("🚨 Critical Customer Defect Themes")
        if issues:
            for issue in issues[:3]:
                st.markdown(
                    f"""
                    <div style="background-color: #FEF2F2; border-left: 4px solid #DC2626; padding: 0.6rem 0.8rem; margin-bottom: 0.5rem; border-radius: 4px;">
                        <div style="font-weight: 700; color: #991B1B;">{issue.theme_title} ({issue.review_count} complaints)</div>
                        <div style="font-size: 0.85rem; color: #7F1D1D;">Topic: {issue.topic} | Severity: <b>{issue.severity_or_sentiment}</b></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.subheader("✨ Top Customer Praise Themes")
        if praises:
            for praise in praises[:3]:
                st.markdown(
                    f"""
                    <div style="background-color: #F0FDF4; border-left: 4px solid #16A34A; padding: 0.6rem 0.8rem; margin-bottom: 0.5rem; border-radius: 4px;">
                        <div style="font-weight: 700; color: #166534;">{praise.theme_title} ({praise.review_count} mentions)</div>
                        <div style="font-size: 0.85rem; color: #14532D;">Topic: {praise.topic}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
