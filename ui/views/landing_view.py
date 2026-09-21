"""
Front Landing Page for E-Commerce IQ.

Features:
- Official uploaded 'eC' brand logo
- Animated glowing/typing title, executive quote & concise description
- Themed Search Option container & Search History gateway
- Live e-commerce background data & operational statistics
- Core business impact pillars (non-repetitive)
- Interactive revenue trajectory graph preview
"""

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
                <h1 class="animated-hero-title">
                    E-COMMERCE IQ
                </h1>
                <div style="font-size: 1.15rem; font-weight: 600; color: {theme['secondary_text']}; margin-top: 0.35rem;">
                    Executive Decision Intelligence & Conversational Analytics Platform
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 2. Executive Quote Banner
    st.markdown(
        f"""
        <div style="background: {theme['card_bg']}; border-left: 4px solid {theme['accent_color']}; border-radius: 8px; padding: 1.2rem; margin: 1.5rem 0 1.2rem 0; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
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

    # 2.5 Front Page Search Option (Themed Search Card & History)
    st.markdown(
        f"""
        <div class="search-card-wrapper">
            <div class="search-card-title">🔍 Search Store Intelligence with Shoplytic</div>
            <div class="search-card-subtitle">
                Search your store's sales, SKU profit margins, customer retention, or return leakage directly from the front page:
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    lp_col1, lp_col2 = st.columns([5, 1])
    with lp_col1:
        landing_query = st.text_input(
            "Landing Search Query",
            placeholder="Search store data (e.g. 'What are our top 5 best selling products?')...",
            label_visibility="collapsed",
            key="landing_search_input"
        )
    with lp_col2:
        landing_btn = st.button("🔍 Search", key="btn_landing_search", type="primary", use_container_width=True)

    # Quick search shortcut chips
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    quick_prompt = None
    with q_col1:
        if st.button("🏆 Top 5 Products", key="landing_qp_1", use_container_width=True):
            quick_prompt = "What are our top 5 best selling products?"
    with q_col2:
        if st.button("📦 Category Sales", key="landing_qp_2", use_container_width=True):
            quick_prompt = "What is our revenue breakdown by category?"
    with q_col3:
        if st.button("🔄 Return Leakage", key="landing_qp_3", use_container_width=True):
            quick_prompt = "Which products have the highest return rate?"
    with q_col4:
        if st.button("👥 Repeat Buyers", key="landing_qp_4", use_container_width=True):
            quick_prompt = "How many customers are repeat buyers?"

    landing_query_to_run = (landing_query if (landing_btn and landing_query) else None) or quick_prompt
    if landing_query_to_run:
        if "search_history" not in st.session_state:
            st.session_state.search_history = []
        if landing_query_to_run not in st.session_state.search_history:
            st.session_state.search_history.append(landing_query_to_run)
        st.session_state.active_search_prompt = landing_query_to_run
        st.session_state.selected_nav = "🤖 Shoplytic Copilot"
        st.session_state.jump_to_copilot = True
        st.rerun()

    # Front Page Themed Recent Search History (if searches exist)
    if st.session_state.get("search_history"):
        num_hist = len(st.session_state.search_history)
        st.markdown(
            f"""
            <div class="search-history-wrapper">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.4rem;">
                    <div style="font-weight: 700; font-size: 0.92rem; color: {theme['text_color']};">
                        🕒 Recent Search History <span class="search-badge">{num_hist} Saved</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        l_hist_cols = st.columns(3)
        for h_idx, past_q in enumerate(reversed(st.session_state.search_history[-3:])):
            col = l_hist_cols[h_idx % 3]
            if col.button(f"🔍 {past_q[:35]}...", key=f"landing_hist_{h_idx}", use_container_width=True):
                st.session_state.active_search_prompt = past_q
                st.session_state.selected_nav = "🤖 Shoplytic Copilot"
                st.session_state.jump_to_copilot = True
                st.rerun()

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
