"""
Customer Behavior, RFM Segmentation & Retention Analytics View.

Analyzes purchasing behavior, lifetime value (LTV), repeat purchase velocity,
RFM score distribution, and flags dormant high-value accounts for churn intervention.
"""

import streamlit as st
import plotly.graph_objects as go

from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.analytics.customers import CustomerAnalyticsEngine
from ecommerce_iq.business_logic.segmentation import CustomerSegmentationEngine
from ecommerce_iq.ai.interpretation import AnalyticsInterpreter
from ui.components.cards import render_ai_insight_card, render_table


def render_customers_page(db: DatabaseManager, interpreter: AnalyticsInterpreter) -> None:
    """Render Customer Behavior analytics view."""
    st.title("👥 Customer Behavior & Retention Dynamics")
    st.caption("Customer lifetime value (LTV), order frequency distribution, RFM quintiles, and churn risk detection.")

    cust_engine = CustomerAnalyticsEngine(db)
    seg_engine = CustomerSegmentationEngine(db)

    summary = cust_engine.get_aggregate_customer_metrics()
    churn_cohort = seg_engine.get_churn_risk_cohort(limit=10)

    # 1. AI Executive Interpretation
    interp = interpreter.interpret_customer_behavior(summary, churn_risks=churn_cohort)
    render_ai_insight_card(interp)

    # 2. Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Repeat Purchase Rate", f"{summary.repeat_purchase_rate_pct:.2f}%", f"{summary.repeat_customers} Repeat Buyers")
    with c2:
        st.metric("Average Customer LTV", f"${summary.average_customer_ltv:,.2f}")
    with c3:
        st.metric("Average Order Frequency", f"{summary.average_order_frequency:.2f} orders")
    with c4:
        st.metric("Active Purchasers", f"{summary.active_purchasers:,} accounts")

    # 3. Order Frequency Distribution Chart
    st.markdown("---")
    st.subheader("📊 Customer Order Frequency Distribution")
    freq_data = cust_engine.get_order_frequency_distribution()
    if freq_data:
        brackets = [d.get("bracket", "") for d in freq_data]
        counts = [int(d.get("customer_count", 0)) for d in freq_data]
        pcts = [float(d.get("customer_pct", d.get("percentage", 0.0))) for d in freq_data]

        fig = go.Figure(
            data=[
                go.Bar(
                    x=brackets,
                    y=counts,
                    marker_color="#1E3A8A",
                    text=[f"{c} ({p:.1f}%)" for c, p in zip(counts, pcts)],
                    textposition="auto"
                )
            ]
        )
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(title="Order Count Bracket"),
            yaxis=dict(title="Customer Count", showgrid=True, gridcolor="#E2E8F0"),
            height=300,
            margin=dict(l=40, r=40, t=20, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)

    # 4. Churn Risk Dormant Cohort Table
    st.subheader("🚨 Dormant High-Value Customers (Churn Risk)")
    st.caption("High-value purchasers who have not transacted in 60+ days. Targeted retention incentives recommended.")
    if churn_cohort:
        churn_rows = [
            {
                "Customer (Masked)": c.display_name,
                "Location": f"{c.city}, {c.country}",
                "Segment": c.segment,
                "Orders Placed": c.orders_placed,
                "Lifetime Spend": f"${c.total_spend:,.2f}",
                "AOV": f"${c.average_order_value:,.2f}",
                "Days Inactive": f"{c.days_since_last_order} days",
                "Risk Level": c.risk_level,
                "Revenue at Risk": f"${c.estimated_revenue_at_risk:,.2f}"
            }
            for c in churn_cohort
        ]
        render_table(churn_rows)
