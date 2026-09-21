"""
Main Streamlit Application Entrypoint for E-Commerce IQ.

Corporate-grade decision intelligence platform featuring:
- Official 'eC' brand logo & favicon
- Dynamic 3-Theme & Vibe Engine (Corporate Executive, Modern Dark Mode, Luxury Minimalist)
- Hero Landing Page & Executive Dashboard
- Shoplytic Conversational Copilot with dynamic chart generation & search history
- Clean, non-repetitive e-commerce navigation
- Full Terms & Conditions governance
- Automated database self-healing on cloud boot
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure project root is available on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir / "src") not in sys.path:
    sys.path.insert(0, str(root_dir / "src"))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st

from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.analytics.kpis import KPICalculator
from ecommerce_iq.analytics.products import ProductAnalyticsEngine
from ecommerce_iq.business_logic.diagnosis import BusinessPerformanceDiagnostic
from ecommerce_iq.ai.interpretation import AnalyticsInterpreter
from ecommerce_iq.ai.query_engine import NaturalLanguageQueryEngine

from ui.theme import apply_theme, get_current_theme
from ui.components.cards import render_kpi_grid, render_ai_insight_card
from ui.components.charts import (
    render_revenue_trend_chart,
    render_category_donut_chart,
    render_returns_bar_chart,
    render_rating_distribution_chart,
    render_variance_bar_chart,
)
from ui.components.chat import render_copilot_chat
from ui.views.landing_view import render_landing_page
from ui.views.terms_view import render_terms_page
from ui.views.connect_view import render_connect_page
from ui.views.guide_view import render_guide_page


def ensure_database_ready(db: DatabaseManager) -> None:
    """Auto-heal and initialize database if missing or empty on cloud boot."""
    try:
        res = db.execute_query("SELECT COUNT(*) as cnt FROM orders")
        if res and res[0]["cnt"] > 0:
            return
    except Exception:
        pass

    # Database needs seeding
    try:
        from scripts.init_db import init_database
        from scripts.seed_mock_data import seed_dataset
        init_database()
        seed_dataset()
    except Exception as e:
        print(f"Notice: Database auto-init error: {e}")


def init_app() -> None:
    """Initialize Streamlit page configuration and stylesheets."""
    logo_path = Path(__file__).resolve().parent / "app_logo.png"
    icon = str(logo_path) if logo_path.exists() else "📊"

    st.set_page_config(
        page_title="E-Commerce IQ | Executive BI Platform",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded"
    )


def get_db_manager() -> DatabaseManager:
    """Cached connection provider for database operations."""
    return DatabaseManager()


# ------------------------------------------------------------------------------
# View: Executive Overview Dashboard
# ------------------------------------------------------------------------------
def render_overview_view(db: DatabaseManager, interpreter: AnalyticsInterpreter) -> None:
    """Render the high-level Executive Overview dashboard."""
    theme = get_current_theme()

    st.title("📊 Executive Overview & Business Scorecard")
    st.caption("Real-time performance metrics, automated AI briefings, and operational alerts.")

    # 1. High-Level KPI Grid
    kpi_calc = KPICalculator(db)
    kpis = kpi_calc.calculate_summary()
    render_kpi_grid(kpis)

    st.markdown("---")

    # 2. AI Executive Briefing Card
    interp = interpreter.interpret_kpis(kpis)
    render_ai_insight_card(interp)

    # 3. Monthly Revenue Trend & Category Breakdown
    col_left, col_right = st.columns([3, 2])

    with col_left:
        monthly_sales = kpi_calc.get_revenue_by_month()
        fig_trend = render_revenue_trend_chart(monthly_sales)
        fig_trend.update_layout(template=theme["plotly_template"])
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_right:
        prod_engine = ProductAnalyticsEngine(db)
        cat_data = prod_engine.get_category_breakdown()
        fig_cat = render_category_donut_chart(cat_data)
        fig_cat.update_layout(template=theme["plotly_template"])
        st.plotly_chart(fig_cat, use_container_width=True)

    # 4. Critical Anomaly Notification Banner
    st.markdown(
        """
        <div style="background-color: #FFF1F2; border: 1px solid #FECDD3; border-left: 4px solid #E11D48; border-radius: 6px; padding: 1rem; margin-top: 1rem;">
            <div style="font-weight: 700; color: #9F1239; margin-bottom: 0.3rem;">
                🚨 Executive Performance Alert: August 2025 Revenue Contraction
            </div>
            <div style="font-size: 0.9rem; color: #881337;">
                Net revenue contracted by <b>-$56,904.60 (-61.03%)</b> from July baseline, driven by a 54.7% collapse in completed orders and elevated hardware defect complaints on <b>PROD-ELEC-001</b>.
                Switch to the <b>Sales Collapse Diagnosis</b> tab for empirical root-cause attribution.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ------------------------------------------------------------------------------
# Main Routing Application
# ------------------------------------------------------------------------------
def main() -> None:
    """Main routing controller."""
    init_app()

    db = get_db_manager()
    ensure_database_ready(db)

    interpreter = AnalyticsInterpreter()
    query_engine = NaturalLanguageQueryEngine(db_manager=db)

    # Apply Selected Theme & Inject Dynamic Backgrounds
    theme_key = apply_theme()
    theme = get_current_theme()

    # Sidebar Header with Official Brand Logo
    logo_path = Path(__file__).resolve().parent / "app_logo.png"
    if logo_path.exists():
        st.sidebar.image(str(logo_path), width=100)

    st.sidebar.markdown(
        f"""
        <div style="margin-bottom: 0.8rem;">
            <h2 style="margin: 0; color: {theme['primary_color']}; font-weight: 800; letter-spacing: -0.02em; font-size: 1.4rem;">
                E-COMMERCE IQ
            </h2>
            <div style="font-size: 0.75rem; color: {theme['secondary_text']}; font-weight: 600;">
                Executive Decision Intelligence
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")

    # Clean, Non-Repetitive Navigation
    nav_options = [
        "🏠 Home",
        "📊 Executive Dashboard",
        "🤖 Shoplytic Copilot",
        "🔌 Connect Store / Data",
        "📖 How to Use",
        "🛍️ Product Economics",
        "👥 Customer RFM",
        "🔄 Returns & Leakage",
        "📉 Sales Collapse Diagnosis",
        "📜 Terms & Conditions"
    ]

    if "selected_nav" not in st.session_state:
        st.session_state.selected_nav = "🏠 Home"

    if st.session_state.get("jump_to_copilot"):
        st.session_state.jump_to_copilot = False
        st.session_state.selected_nav = "🤖 Shoplytic Copilot"

    current_nav_idx = 0
    if st.session_state.selected_nav in nav_options:
        current_nav_idx = nav_options.index(st.session_state.selected_nav)

    selected_view = st.sidebar.radio("Navigation Menu", nav_options, index=current_nav_idx)
    st.session_state.selected_nav = selected_view

    st.sidebar.markdown("---")

    # Advanced Engineering Stages Expander (Preserves all 11 technical stages)
    with st.sidebar.expander("🔬 Technical Stages (1–11)", expanded=False):
        stage_nav = st.selectbox(
            "Select Technical Stage",
            [
                "None (Use Menu Above)",
                "Stage 1: Foundation Schema & ORM",
                "Stage 2: Synthetic Dataset & Anomaly",
                "Stage 3: Sales & Revenue Analytics",
                "Stage 4: Product Performance & Margins",
                "Stage 5: Customer Retention & LTV",
                "Stage 6: Reviews & VADER Sentiment",
                "Stage 7: Returns & Refund Dollar Leakage",
                "Stage 8: August Collapse Diagnosis",
                "Stage 9: Natural Language Text-to-SQL",
                "Stage 10: AI Executive Interpretation",
                "Stage 11: Corporate BI Interface"
            ],
            index=0
        )

    # Sidebar Footer with Founder Attribution
    st.sidebar.markdown(
        f"""
        <div style="text-align: center; margin-top: 1.5rem; padding: 0.8rem 0; border-top: 1px solid {theme['border_color']};">
            <div style="font-size: 0.82rem; font-weight: 700; color: {theme['text_color']};">Crafted by Alankrita Paul</div>
            <div style="font-size: 0.72rem; color: {theme['secondary_text']};">Founder & Lead Architect</div>
            <div style="font-size: 0.68rem; color: #10B981; margin-top: 4px;">● System Active (4,061 Orders)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Route based on technical stage override if selected
    if stage_nav and stage_nav != "None (Use Menu Above)":
        if "Stage 1" in stage_nav:
            from ui.views.foundation_view import render_foundation_page
            render_foundation_page(db)
            return
        elif "Stage 2" in stage_nav:
            from ui.views.dataset_view import render_dataset_page
            render_dataset_page(db)
            return
        elif "Stage 3" in stage_nav:
            from ui.views.sales_view import render_sales_page
            render_sales_page(db, interpreter)
            return
        elif "Stage 4" in stage_nav:
            from ui.views.products_view import render_products_page
            render_products_page(db, interpreter)
            return
        elif "Stage 5" in stage_nav:
            from ui.views.customers_view import render_customers_page
            render_customers_page(db, interpreter)
            return
        elif "Stage 6" in stage_nav:
            from ui.views.reviews_view import render_reviews_page
            render_reviews_page(db, interpreter)
            return
        elif "Stage 7" in stage_nav:
            from ui.views.returns_view import render_returns_page
            render_returns_page(db, interpreter)
            return
        elif "Stage 8" in stage_nav:
            from ui.views.diagnosis_view import render_diagnosis_page
            render_diagnosis_page(db, interpreter)
            return
        elif "Stage 9" in stage_nav:
            render_copilot_chat(query_engine)
            return
        elif "Stage 10" in stage_nav:
            from ui.views.interpretation_view import render_interpretation_page
            render_interpretation_page(db, interpreter)
            return
        elif "Stage 11" in stage_nav:
            render_overview_view(db, interpreter)
            return

    # Standard Main Navigation Routing
    if selected_view == "🏠 Home":
        render_landing_page(db)

    elif selected_view == "📊 Executive Dashboard":
        render_overview_view(db, interpreter)

    elif selected_view == "🤖 Shoplytic Copilot":
        render_copilot_chat(query_engine)

    elif selected_view == "🔌 Connect Store / Data":
        render_connect_page(db)

    elif selected_view == "📖 How to Use":
        render_guide_page()

    elif selected_view == "🛍️ Product Economics":
        from ui.views.products_view import render_products_page
        render_products_page(db, interpreter)

    elif selected_view == "👥 Customer RFM":
        from ui.views.customers_view import render_customers_page
        render_customers_page(db, interpreter)

    elif selected_view == "🔄 Returns & Leakage":
        from ui.views.returns_view import render_returns_page
        render_returns_page(db, interpreter)

    elif selected_view == "📉 Sales Collapse Diagnosis":
        from ui.views.diagnosis_view import render_diagnosis_page
        render_diagnosis_page(db, interpreter)

    elif selected_view == "📜 Terms & Conditions":
        render_terms_page()


if __name__ == "__main__":
    main()
