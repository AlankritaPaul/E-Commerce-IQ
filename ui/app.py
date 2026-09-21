"""
Main Streamlit Application Entrypoint for E-Commerce IQ.

Corporate-grade decision intelligence platform featuring executive KPI scorecards,
interactive Plotly visualizations, AI interpretation briefings, and a secure
natural-language SQL copilot.
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
from ecommerce_iq.analytics.customers import CustomerAnalyticsEngine
from ecommerce_iq.analytics.returns import ReturnsAnalyticsEngine
from ecommerce_iq.analytics.reviews import ReviewAnalyticsEngine
from ecommerce_iq.business_logic.diagnosis import BusinessPerformanceDiagnostic
from ecommerce_iq.ai.interpretation import AnalyticsInterpreter
from ecommerce_iq.ai.query_engine import NaturalLanguageQueryEngine

from ui.components.cards import render_kpi_grid, render_ai_insight_card
from ui.components.charts import (
    render_revenue_trend_chart,
    render_category_donut_chart,
    render_returns_bar_chart,
    render_rating_distribution_chart,
    render_variance_bar_chart,
)
from ui.components.chat import render_copilot_chat


CUSTOM_CSS = """
<style>
    /* Global Typography & Palette */
    .main {
        background-color: #F8FAFC;
    }
    h1, h2, h3, h4 {
        color: #0F172A;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Executive Metric Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 0.8rem;
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0.3rem 0;
    }
    .metric-delta {
        font-size: 0.85rem;
        font-weight: 600;
    }
    .delta-positive { color: #059669; }
    .delta-negative { color: #E11D48; }
    .delta-neutral { color: #64748B; }
    .metric-subtitle {
        font-size: 0.75rem;
        color: #94A3B8;
        margin-top: 0.2rem;
    }

    /* AI Executive Briefing Callout */
    .ai-insight-card {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-left: 4px solid #16A34A;
        border-radius: 6px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
    }
    .badge {
        font-size: 0.75rem;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-weight: 600;
    }
    .badge-grounded {
        background-color: #DCFCE7;
        color: #15803D;
        border: 1px solid #86EFAC;
    }
    .badge-warning {
        background-color: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #FECACA;
    }
    .badge-critical {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #F87171;
    }
</style>
"""


def init_app() -> None:
    """Initialize Streamlit page configuration and stylesheets."""
    st.set_page_config(
        page_title="E-Commerce IQ | Executive BI Platform",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def get_db_manager() -> DatabaseManager:
    """Cached connection provider for database operations."""
    return DatabaseManager()


# ------------------------------------------------------------------------------
# View: 1. Executive Overview
# ------------------------------------------------------------------------------
def render_overview_view(db: DatabaseManager, interpreter: AnalyticsInterpreter) -> None:
    """Render the high-level Executive Overview dashboard."""
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
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_right:
        prod_engine = ProductAnalyticsEngine(db)
        cat_data = prod_engine.get_category_breakdown()
        fig_cat = render_category_donut_chart(cat_data)
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
                Switch to the <b>Business Decline Diagnosis</b> tab for empirical root-cause attribution.
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
    interpreter = AnalyticsInterpreter()
    query_engine = NaturalLanguageQueryEngine(db_manager=db)

    # Sidebar Navigation
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 1rem;">
            <h2 style="margin: 0; color: #1E3A8A; font-weight: 800; letter-spacing: -0.02em;">E-COMMERCE IQ</h2>
            <div style="font-size: 0.75rem; color: #64748B; font-weight: 600;">Executive Decision Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    nav_options = [
        "11. Professional Interface (Overview)",
        "1. The Foundation of The Whole System",
        "2. Realistic Business Dataset",
        "3. Sales & Revenue Analytics",
        "4. Product Performance",
        "5. Customer Analysis",
        "6. Customer Response",
        "7. Returns & Refunds",
        "8. Why did sales decrease?",
        "9. Natural-language business questions",
        "10. AI answer layer"
    ]

    selected_view = st.sidebar.radio("Navigation", nav_options, index=0)

    st.sidebar.markdown("---")
    st.sidebar.caption("System Status: **Relational Database Connected**")
    st.sidebar.caption("Historical Data: **Jan 2025 – Feb 2026**")

    # Route based on selection matching user-defined stage names
    if selected_view == "11. Professional Interface (Overview)":
        render_overview_view(db, interpreter)

    elif selected_view == "1. The Foundation of The Whole System":
        from ui.pages.foundation_view import render_foundation_page
        render_foundation_page(db)

    elif selected_view == "2. Realistic Business Dataset":
        from ui.pages.dataset_view import render_dataset_page
        render_dataset_page(db)

    elif selected_view == "3. Sales & Revenue Analytics":
        from ui.pages.sales_view import render_sales_page
        render_sales_page(db, interpreter)

    elif selected_view == "4. Product Performance":
        from ui.pages.products_view import render_products_page
        render_products_page(db, interpreter)

    elif selected_view == "5. Customer Analysis":
        from ui.pages.customers_view import render_customers_page
        render_customers_page(db, interpreter)

    elif selected_view == "6. Customer Response":
        from ui.pages.reviews_view import render_reviews_page
        render_reviews_page(db, interpreter)

    elif selected_view == "7. Returns & Refunds":
        from ui.pages.returns_view import render_returns_page
        render_returns_page(db, interpreter)

    elif selected_view == "8. Why did sales decrease?":
        from ui.pages.diagnosis_view import render_diagnosis_page
        render_diagnosis_page(db, interpreter)

    elif selected_view == "9. Natural-language business questions":
        render_copilot_chat(query_engine)

    elif selected_view == "10. AI answer layer":
        from ui.pages.interpretation_view import render_interpretation_page
        render_interpretation_page(db, interpreter)


if __name__ == "__main__":
    main()
