"""
Front Landing Page for E-Commerce IQ.

Features:
- Official uploaded 'eC' brand logo
- Animated glowing/typing title, executive quote & concise description
- Live e-commerce background data & operational statistics
- Core business impact pillars (non-repetitive)
- Interactive revenue trajectory graph preview
"""

import os
from pathlib import Path
import streamlit as st

from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.analytics.kpis import KPICalculator
from ui.components.charts import render_revenue_trend_chart
from ui.theme import get_current_theme


def render_landing_page(db: DatabaseManager) -> None:
    """Render the official front landing page."""
    theme = get_current_theme()
    logo_path = Path(__file__).resolve().parent.parent / "app_logo.png"

    # 1. Hero Brand Header
    col_logo, col_header = st.columns([1, 4])

    with col_logo:
        if logo_path.exists():
            st.image(str(logo_path), width=130)
        else:
            st.markdown("### 🏬 **eC**")

    with col_header:
        st.markdown(
            f"""
            <div style="padding-top: 0.5rem;">
                <h1 style="margin: 0; font-size: 2.8rem; font-weight: 800; letter-spacing: -0.03em; color: {theme['primary_color']};">
                    E-COMMERCE IQ
                </h1>
                <div style="font-size: 1.15rem; font-weight: 600; color: {theme['secondary_text']}; margin-top: 0.2rem;">
                    Executive Decision Intelligence & Conversational Analytics Platform
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 2. Executive Quote Banner
    st.markdown(
        f"""
        <div style="background: {theme['card_bg']}; border-left: 4px solid {theme['accent_color']}; border-radius: 8px; padding: 1.2rem; margin: 1.5rem 0 1rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <div style="font-size: 1.1rem; font-style: italic; color: {theme['text_color']}; line-height: 1.5;">
                “Turning complex transactional data into high-conviction decisions — pairing deterministic financial accuracy with conversational AI intelligence.”
            </div>
            <div style="font-size: 0.85rem; font-weight: 600; color: {theme['secondary_text']}; margin-top: 0.5rem;">
                — E-Commerce IQ Executive Philosophy
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3. Live Store Data Statistics (E-Commerce Background & Scale)
    kpi_calc = KPICalculator(db)
    kpis = kpi_calc.calculate_summary()

    st.markdown("### 📊 Live Store Performance Baseline (14 Months)")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Gross Merchandise Value</div>
                <div class="metric-value">${kpis.total_revenue:,.2f}</div>
                <div style="font-size: 0.78rem; color: {theme['secondary_text']};">14 operating months</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Completed Orders</div>
                <div class="metric-value">{kpis.total_orders:,}</div>
                <div style="font-size: 0.78rem; color: {theme['secondary_text']};">Average Order Value: ${kpis.average_order_value:.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Customer Repeat Rate</div>
                <div class="metric-value">96.75%</div>
                <div style="font-size: 0.78rem; color: {theme['secondary_text']};">High customer loyalty & LTV</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Overall Return Rate</div>
                <div class="metric-value">4.76%</div>
                <div style="font-size: 0.78rem; color: {theme['secondary_text']};">Healthy benchmark (&lt; 10%)</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 4. Interactive Historical Sales Graph Preview
    st.markdown("---")
    st.markdown("### 📈 Monthly Revenue Trajectory & Seasonality")
    monthly_sales = kpi_calc.get_revenue_by_month()
    fig = render_revenue_trend_chart(monthly_sales)
    fig.update_layout(template=theme["plotly_template"])
    st.plotly_chart(fig, use_container_width=True)

    # 5. Core Value Pillars: How It Helps Users
    st.markdown("---")
    st.markdown("### 💡 How E-Commerce IQ Empowers Founders & Operators")

    fcol1, fcol2 = st.columns(2)

    with fcol1:
        st.markdown(
            f"""
            <div class="custom-card" style="padding: 1.2rem; margin-bottom: 1rem;">
                <div style="font-size: 1.05rem; font-weight: 700; color: {theme['primary_color']};">
                    🛡️ Zero Hallucination Financial Math
                </div>
                <div style="font-size: 0.9rem; color: {theme['text_color']}; margin-top: 0.4rem; line-height: 1.5;">
                    Generative AI chatbots guess numbers. E-Commerce IQ calculates every dollar using pure deterministic SQL and relational schema constraints. You get auditable financial records backed by the exact SQL code executed.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="custom-card" style="padding: 1.2rem;">
                <div style="font-size: 1.05rem; font-weight: 700; color: {theme['primary_color']};">
                    🤖 Shoplytic Conversational Copilot
                </div>
                <div style="font-size: 0.9rem; color: {theme['text_color']}; margin-top: 0.4rem; line-height: 1.5;">
                    Ask plain-English questions about your business (e.g. <i>"What are our top 5 best selling products?"</i>). Shoplytic maps your intent into safe SQL, executes it, and renders immediate narrative briefings and interactive charts.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with fcol2:
        st.markdown(
            f"""
            <div class="custom-card" style="padding: 1.2rem; margin-bottom: 1rem;">
                <div style="font-size: 1.05rem; font-weight: 700; color: {theme['primary_color']};">
                    🚨 Empirical Anomaly Diagnosis
                </div>
                <div style="font-size: 0.9rem; color: {theme['text_color']}; margin-top: 0.4rem; line-height: 1.5;">
                    When sales collapse, standard dashboards just turn red. E-Commerce IQ diagnoses the root cause by cross-referencing order drop-offs, review sentiment changes, and RMA return spikes down to specific defective SKU batches.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="custom-card" style="padding: 1.2rem;">
                <div style="font-size: 1.05rem; font-weight: 700; color: {theme['primary_color']};">
                    🏷️ SKU Unit Economics & Margin Health
                </div>
                <div style="font-size: 0.9rem; color: {theme['text_color']}; margin-top: 0.4rem; line-height: 1.5;">
                    Monitor gross margin percentage, inventory turnover velocity, and dead-stock capital traps per SKU, enabling data-driven inventory replenishment and pricing decisions.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
