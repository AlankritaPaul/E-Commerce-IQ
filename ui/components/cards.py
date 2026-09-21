"""
Executive KPI and AI Insight Card Components.

Renders high-contrast, decision-focused metric cards, KPI grids,
and verified AI interpretation briefings for business executives.
"""

from typing import Any, Dict, List, Optional
from ecommerce_iq.models.schemas import AnalyticalInterpretation, KPISummary


def format_metric_card_html(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    subtitle: Optional[str] = None
) -> str:
    """Generate clean, styled HTML string for an executive metric card."""
    delta_class = "delta-neutral"
    arrow = ""
    if delta:
        if delta.startswith("+"):
            delta_class = "delta-positive" if delta_color != "inverse" else "delta-negative"
            arrow = "▲ "
        elif delta.startswith("-"):
            delta_class = "delta-negative" if delta_color != "inverse" else "delta-positive"
            arrow = "▼ "

    delta_html = f'<div class="metric-delta {delta_class}">{arrow}{delta}</div>' if delta else ""
    subtitle_html = f'<div class="metric-subtitle">{subtitle}</div>' if subtitle else ""

    return f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
        {subtitle_html}
    </div>
    """


def render_table(rows: List[Dict[str, Any]]) -> None:
    """Render a clean, dependency-free Markdown table from records."""
    if not rows:
        return
    headers = list(rows[0].keys())
    lines = [
        "| " + " | ".join(str(h) for h in headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |"
    ]
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(h, "")) for h in headers) + " |")
    try:
        import streamlit as st
        st.markdown("\n".join(lines), unsafe_allow_html=True)
    except Exception:
        pass


def render_metric_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    subtitle: Optional[str] = None
) -> None:
    """Render an individual executive metric card in Streamlit."""
    try:
        import streamlit as st
        card_html = format_metric_card_html(title, value, delta, delta_color, subtitle)
        st.markdown(card_html, unsafe_allow_html=True)
    except Exception:
        # Graceful fallback for non-Streamlit testing environments
        pass


def render_kpi_grid(kpis: KPISummary) -> None:
    """Render a comprehensive executive 4-column KPI grid."""
    try:
        import streamlit as st

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            margin_str = f"{kpis.gross_margin_percentage:.1f}% Margin" if kpis.gross_margin_percentage else None
            st.metric(label="Net Revenue", value=f"${kpis.net_revenue:,.2f}", delta=margin_str)
        with col2:
            st.metric(label="Completed Orders", value=f"{kpis.total_orders:,}")
        with col3:
            st.metric(label="Average Order Value (AOV)", value=f"${kpis.average_order_value:,.2f}")
        with col4:
            st.metric(
                label="Return Rate",
                value=f"{kpis.return_rate_percentage:.2f}%",
                delta=f"${kpis.total_refunds:,.2f} Refunds",
                delta_color="inverse"
            )

        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric(label="Gross Sales", value=f"${kpis.total_revenue:,.2f}")
        with col6:
            st.metric(label="Active Purchasers", value=f"{kpis.active_customers:,}")
        with col7:
            refund_pct = (kpis.total_refunds / max(1.0, kpis.total_revenue)) * 100.0
            st.metric(label="Refund Leakage Ratio", value=f"{refund_pct:.2f}%")
        with col8:
            rev_per_buyer = kpis.net_revenue / max(1, kpis.active_customers)
            st.metric(label="Revenue per Active Buyer", value=f"${rev_per_buyer:,.2f}")

    except Exception:
        pass


def render_ai_insight_card(interpretation: AnalyticalInterpretation) -> None:
    """Render an evidence-grounded executive briefing card."""
    try:
        import streamlit as st

        grounding_badge = (
            '<span class="badge badge-grounded">Verified Grounded: 100% Data Backed</span>'
            if interpretation.is_grounded
            else '<span class="badge badge-warning">Audit Warning: Unverified Figures Detected</span>'
        )

        st.markdown(
            f"""
            <div class="ai-insight-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <div style="font-weight: 700; font-size: 1.1rem; color: #1E293B;">
                        🤖 AI Executive Briefing: {interpretation.title}
                    </div>
                    <div>{grounding_badge}</div>
                </div>
                <div style="font-size: 0.95rem; line-height: 1.5; color: #334155; margin-bottom: 1rem;">
                    {interpretation.summary}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("📌 Key Findings & Underlying Drivers", expanded=True):
            for finding in interpretation.key_findings:
                st.markdown(f"- {finding}")

        if interpretation.evidence_based_insights:
            with st.expander("🔍 Root Causes & Causal Insights", expanded=False):
                for insight in interpretation.evidence_based_insights:
                    st.markdown(f"- {insight}")

        if interpretation.actionable_recommendations:
            with st.expander("⚡ Actionable Operational Recommendations", expanded=True):
                for rec in interpretation.actionable_recommendations:
                    st.markdown(f"1. **Action**: {rec}")

        if interpretation.evidence_citations:
            with st.expander("📊 Data Citations & Verification Audit", expanded=False):
                for c in interpretation.evidence_citations:
                    st.caption(f"• **{c.metric_name}**: Verified value `{c.formatted_value}` (Attribute: `{c.source_attribute}`) — {c.context}")

    except Exception:
        pass
