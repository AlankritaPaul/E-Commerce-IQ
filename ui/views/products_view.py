"""
Product Performance & Catalog Unit Economics View.

Evaluates SKU-level revenue, units sold, profit margins, return rates,
and customer satisfaction to identify cash cows and underperforming inventory.
"""

from typing import Any, Dict
import streamlit as st

from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.analytics.products import ProductAnalyticsEngine
from ecommerce_iq.ai.interpretation import AnalyticsInterpreter
from ui.components.cards import render_ai_insight_card, render_table
from ui.components.charts import render_category_donut_chart


def _get_val(obj: Any, key: str, default: Any = "") -> Any:
    """Helper to safely get field from object or dict."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def render_products_page(db: DatabaseManager, interpreter: AnalyticsInterpreter) -> None:
    """Render Product Performance analytics view."""
    st.title("🛍️ Product Performance & Unit Economics")
    st.caption("SKU velocity, category contribution, profit margins, and catalog health classification.")

    prod_engine = ProductAnalyticsEngine(db)
    all_metrics = prod_engine.get_revenue_by_product()

    # 1. AI Executive Interpretation
    interp = interpreter.interpret_product_performance(all_metrics)
    render_ai_insight_card(interp)

    # 2. Category Share and Top Products Split
    col_left, col_right = st.columns([2, 3])

    with col_left:
        cat_data = prod_engine.get_category_breakdown()
        st.plotly_chart(render_category_donut_chart(cat_data), use_container_width=True)

    with col_right:
        st.subheader("🏆 Top Bestselling SKUs")
        top_products = prod_engine.get_top_products(limit=5)
        top_rows = [
            {
                "SKU": _get_val(p, "sku"),
                "Product Title": _get_val(p, "title") or _get_val(p, "product_name"),
                "Category": _get_val(p, "category_name"),
                "Units Sold": f"{int(_get_val(p, 'units_sold', 0)):,}",
                "Net Revenue": f"${float(_get_val(p, 'net_revenue', _get_val(p, 'total_revenue', 0.0))):,.2f}",
                "Rating": f"{float(_get_val(p, 'avg_rating', 0.0)):.2f} ★"
            }
            for p in top_products
        ]
        render_table(top_rows)

    # 3. Underperforming & Dead Stock Inventory
    st.subheader("⚠️ Underperforming & Low-Velocity Inventory")
    st.caption("Products with lowest unit velocity or elevated return rates requiring clearance or quality review.")
    underperforming = prod_engine.get_underperforming_products(limit=5)
    under_rows = [
        {
            "SKU": _get_val(p, "sku"),
            "Product Title": _get_val(p, "title") or _get_val(p, "product_name"),
            "Category": _get_val(p, "category_name"),
            "Units Sold": f"{int(_get_val(p, 'units_sold', 0)):,}",
            "Revenue": f"${float(_get_val(p, 'net_revenue', _get_val(p, 'total_revenue', 0.0))):,.2f}",
            "Return Rate": f"{float(_get_val(p, 'return_rate_pct', 0.0)):.2f}%",
            "Rating": f"{float(_get_val(p, 'avg_rating', 0.0)):.2f} ★"
        }
        for p in underperforming
    ]
    render_table(under_rows)

    # 4. Full Catalog Ledger
    with st.expander("📊 Full Catalog Metrics Table", expanded=False):
        all_rows = [
            {
                "ID": _get_val(p, "product_id"),
                "SKU": _get_val(p, "sku"),
                "Title": _get_val(p, "title") or _get_val(p, "product_name"),
                "Category": _get_val(p, "category_name"),
                "Units Sold": _get_val(p, "units_sold", 0),
                "Total Revenue ($)": f"${float(_get_val(p, 'net_revenue', _get_val(p, 'total_revenue', 0.0))):,.2f}",
                "Return Rate (%)": f"{float(_get_val(p, 'return_rate_pct', 0.0)):.2f}%",
                "Rating": f"{float(_get_val(p, 'avg_rating', 0.0)):.2f} ★"
            }
            for p in all_metrics
        ]
        render_table(all_rows)
