"""
Streamlit View: 2. Realistic Business Dataset.

Renders dataset metrics, temporal coverage, embedded anomalies, and data generator summary.
"""

from typing import Any, Dict, List
import streamlit as st
from ecommerce_iq.database.connection import DatabaseManager
from ui.components.cards import render_table


def render_dataset_page(db: DatabaseManager) -> None:
    """Render Stage 2: Realistic Business Dataset."""
    st.title("📦 2. Realistic Business Dataset")
    st.caption("Deterministic synthetic dataset spanning 14 operating months with realistic business anomalies.")

    # 1. High-Level Dataset Scorecard
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Temporal Span", "14 Months", "Jan 2025 – Feb 2026")
    with col2:
        st.metric("Customer Base", "850 Profiles", "Active Purchasers: 832")
    with col3:
        st.metric("Order Volume", "4,061 Orders", "6,276 Line Items")
    with col4:
        st.metric("Net Revenue", "$647,823.33", "AOV: $159.52")

    st.markdown("---")

    # 2. Key Embedded Business Anomalies
    st.subheader("🎯 Embedded Realistic Business Scenarios")
    st.markdown(
        """
        The dataset is engineered to reflect authentic e-commerce operational dynamics rather than random noise:
        
        1. **August 2025 Revenue Contraction**:
           - Net revenue sharply collapsed by **-61.03%** from July ($93.2K down to $36.3K).
           - Completed order volume plummeted by **-54.7%**, providing an empirical test case for root-cause diagnosis.
        2. **Q4 Holiday Demand Surge**:
           - Strong seasonal volume peaks in November and December ($70K+ monthly revenue).
        3. **Isolated Product Quality Crisis**:
           - `PROD-ELEC-001` experienced a manufacturing defect batch resulting in a **26.55% return rate** and battery complaints.
        4. **Apparel Sizing Inconsistencies**:
           - `PROD-APP-001` shows an elevated return rate of **18.32%** driven by fit and sizing returns.
        """
    )

    st.markdown("---")

    # 3. Category Distribution Snapshot
    st.subheader("📊 Category Dataset Distribution")
    from ecommerce_iq.analytics.products import ProductAnalyticsEngine
    prod_engine = ProductAnalyticsEngine(db)
    cat_rows = prod_engine.get_category_breakdown()
    formatted_cat_rows = []
    for r in cat_rows:
        formatted_cat_rows.append({
            "Category": r.get("category_name", ""),
            "Products": f"{r.get('product_count', 0)} SKUs",
            "Orders": f"{r.get('total_orders', 0):,}",
            "Gross Revenue": f"${r.get('gross_revenue', 0.0):,.2f}"
        })

    render_table(formatted_cat_rows)
