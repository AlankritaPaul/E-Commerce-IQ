"""
Returns, Refunds & Quality Leakage Analytics View.

Calculates return rates, refund capital leakage, RMA reasons,
and connects product return spikes with customer review defect themes.
"""

import streamlit as st

from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.analytics.returns import ReturnsAnalyticsEngine
from ecommerce_iq.ai.interpretation import AnalyticsInterpreter
from ui.components.cards import render_ai_insight_card, render_table
from ui.components.charts import render_returns_bar_chart


def render_returns_page(db: DatabaseManager, interpreter: AnalyticsInterpreter) -> None:
    """Render Returns & Refunds analytics view."""
    st.title("🔄 Returns, Refunds & Quality Leakage")
    st.caption("Platform-wide return velocity, refund capital leakage, return reasons, and SKU quality triage.")

    returns_engine = ReturnsAnalyticsEngine(db)
    summary = returns_engine.get_overall_return_summary()
    high_risk_skus = returns_engine.get_highest_return_products(limit=5)

    # 1. AI Executive Interpretation
    interp = interpreter.interpret_returns(summary, high_risk_products=high_risk_skus)
    render_ai_insight_card(interp)

    # 2. Executive Metric Scorecard
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Refund Cost", f"${summary.total_refund_amount:,.2f}", delta="Capital Leakage", delta_color="inverse")
    with c2:
        st.metric("Platform Return Rate", f"{summary.platform_return_rate_pct:.2f}%")
    with c3:
        st.metric("Total Return Incidents", f"{summary.total_return_events:,} events", f"{summary.total_units_returned} units")
    with c4:
        st.metric("High-Risk Products", f"{len(high_risk_skus)} SKUs", delta="Requires Triage", delta_color="inverse")

    # 3. Return Reasons Chart & High-Risk Products
    st.markdown("---")
    col_left, col_right = st.columns([1, 1])

    with col_left:
        reasons_data = [
            {
                "reason": r.reason,
                "incident_count": r.incident_count,
                "total_refund_amount": r.total_refund_amount
            }
            for r in summary.top_return_reasons
        ]
        st.plotly_chart(render_returns_bar_chart(reasons_data), use_container_width=True)

    with col_right:
        st.subheader("⚠️ High-Risk Return Products")
        if high_risk_skus:
            risk_rows = [
                {
                    "SKU": p.sku,
                    "Product Title": p.title,
                    "Units Sold": p.units_sold,
                    "Returned": p.units_returned,
                    "Return Rate": f"{p.return_rate_pct:.2f}%",
                    "Refunded ($)": f"${p.refund_amount:,.2f}",
                    "Primary Reason": p.primary_return_reason
                }
                for p in high_risk_skus
            ]
            render_table(risk_rows)

    # 4. Connected Returns & Review Sentiment Triangulation
    st.markdown("---")
    st.subheader("🔗 Triangulated Defect Diagnosis (Sales + Returns + Reviews)")
    connected = returns_engine.get_connected_return_review_insights(limit=5)
    if connected:
        conn_rows = [
            {
                "SKU": c.sku,
                "Product Title": c.title,
                "Return Rate": f"{c.return_rate_pct:.2f}%",
                "Total Refunded": f"${c.refund_amount:,.2f}",
                "Primary RMA Reason": c.primary_return_reason,
                "Avg Rating": f"{c.average_rating:.2f} ★",
                "Top Review Complaint": c.top_review_complaint,
                "Verdict": c.correlation_verdict
            }
            for c in connected
        ]
        render_table(conn_rows)
