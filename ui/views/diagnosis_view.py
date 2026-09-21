"""
Business Performance Diagnosis View: "Why Did Sales Decrease?"

Empirical multi-factor root-cause investigation module decomposing revenue collapses
into order volume contraction, AOV erosion, product-level drag, and customer review defect signals.
"""

import streamlit as st

from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.business_logic.diagnosis import BusinessPerformanceDiagnostic
from ecommerce_iq.ai.interpretation import AnalyticsInterpreter
from ui.components.cards import render_ai_insight_card, render_table


def render_diagnosis_page(db: DatabaseManager, interpreter: AnalyticsInterpreter) -> None:
    """Render Business Decline Diagnosis view."""
    st.title("🔍 Business Performance Diagnosis")
    st.caption("Empirical root-cause investigation module answering: 'Why Did Sales Decrease?'")

    diagnostic = BusinessPerformanceDiagnostic(db)

    # 1. Period Selector
    col1, col2 = st.columns(2)
    with col1:
        target_year = st.selectbox("Target Year", [2025, 2026], index=0)
    with col2:
        target_month = st.selectbox(
            "Evaluation Month",
            [8, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12],
            format_func=lambda m: f"Month {m:02d} (e.g. August)" if m == 8 else f"Month {m:02d}",
            index=0
        )

    # Run Empirical Month-over-Month Diagnosis
    report = diagnostic.diagnose_month_over_month(target_year, target_month)

    # 2. AI Executive Briefing Callout
    interp = interpreter.interpret_diagnostic(report)
    render_ai_insight_card(interp)

    # 3. Macro Metric Evidence Ledger
    st.subheader("📊 Quantitative Metric Evidence Breakdown")
    st.caption("Empirical indicators comparing target period against the baseline with impact significance ranking.")

    if report.metric_evidences:
        evidence_rows = [
            {
                "Metric Name": m.metric_name,
                "Significance": m.significance,
                "Impact Direction": m.impact_direction,
                "Baseline Value": f"{m.baseline_value:,.2f} {m.unit}",
                "Current Value": f"{m.current_value:,.2f} {m.unit}",
                "Absolute Shift": f"{m.absolute_change:+,.2f} {m.unit}",
                "Percentage Shift": f"{m.percentage_change:+.2f}%"
            }
            for m in report.metric_evidences
        ]
        render_table(evidence_rows)

    # 4. Product-Level Decline Attribution
    st.markdown("---")
    st.subheader("📉 Top Declining Products Attribution")
    st.caption("Individual SKUs that contributed most heavily to the top-line revenue collapse.")

    if report.top_declining_products:
        sku_rows = [
            {
                "SKU": p.sku,
                "Product Title": p.title,
                "Category": p.category_name,
                "Revenue Loss": f"-${p.revenue_loss:,.2f}",
                "Change (%)": f"{p.percentage_change:.1f}%",
                "Units Lost": f"{p.units_sold_change} units",
                "Return Rate": f"{p.return_rate_pct:.1f}%",
                "Rating": f"{p.average_rating:.2f} ★",
                "Top Complaint": p.top_complaint_theme,
                "Primary Driver": p.primary_driver_type
            }
            for p in report.top_declining_products
        ]
        render_table(sku_rows)

    # 5. Customer Review Feedback Signals
    if report.customer_feedback_signals:
        st.markdown("---")
        st.subheader("💬 Corroborating Customer Feedback Signals")
        for signal in report.customer_feedback_signals:
            st.warning(signal)

    # 6. Actionable Turnaround Recommendations
    if report.recommended_actions:
        st.markdown("---")
        st.subheader("⚡ Actionable Turnaround Recommendations")
        for idx, action in enumerate(report.recommended_actions, 1):
            st.success(f"**Step {idx}**: {action}")
