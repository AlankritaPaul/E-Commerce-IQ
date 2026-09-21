"""
Sales & Revenue Analytics View.

Provides in-depth time-series analysis of GMV, Net Revenue, Orders,
Discount impact, and Month-over-Month / Week-over-Week variances.
"""

from typing import Any, Dict, List
import streamlit as st

from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.analytics.kpis import KPICalculator
from ecommerce_iq.analytics.comparisons import PeriodComparisonEngine
from ecommerce_iq.ai.interpretation import AnalyticsInterpreter
from ui.components.cards import render_ai_insight_card, render_table
from ui.components.charts import render_revenue_trend_chart, render_variance_bar_chart


def render_sales_page(db: DatabaseManager, interpreter: AnalyticsInterpreter) -> None:
    """Render Sales & Revenue analytics dashboard."""
    st.title("📈 Sales & Revenue Dynamics")
    st.caption("Detailed revenue trajectory, volume trends, and period-over-period variance decomposition.")

    kpi_calc = KPICalculator(db)
    comp_engine = PeriodComparisonEngine(db)

    # 1. Variance Analysis Controls
    selected_month_str = st.selectbox(
        "Select Evaluation Month (Compares with preceding month)",
        options=["2025-08", "2025-12", "2025-07", "2025-06", "2025-05", "2025-04", "2025-03", "2025-02"],
        index=0
    )

    year, month = [int(p) for p in selected_month_str.split("-")]

    # Compute Period Comparison
    comparisons = comp_engine.compare_month_over_month(year, month)
    interp = interpreter.interpret_period_comparison(comparisons, period_label=f"{selected_month_str} MoM")
    render_ai_insight_card(interp)

    # 2. Charts
    col_left, col_right = st.columns([3, 2])
    with col_left:
        monthly_data = kpi_calc.get_revenue_by_month()
        st.plotly_chart(render_revenue_trend_chart(monthly_data), use_container_width=True)

    with col_right:
        var_data = [
            {"metric_name": c.metric_name, "percentage_change": c.percentage_change}
            for c in comparisons
        ]
        st.plotly_chart(render_variance_bar_chart(var_data), use_container_width=True)

    # 3. Monthly Financial Ledger Table
    st.subheader("📋 Historical Monthly Performance Ledger")
    display_rows = [
        {
            "Month": d.get("month", ""),
            "Completed Orders": f"{int(d.get('total_orders', 0)):,}",
            "Net Revenue ($)": f"${float(d.get('total_revenue', 0.0)):,.2f}",
            "AOV ($)": f"${float(d.get('average_order_value', 0.0)):,.2f}"
        }
        for d in monthly_data
    ]
    render_table(display_rows)
