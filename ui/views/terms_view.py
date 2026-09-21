"""
Terms & Conditions / Compliance View for E-Commerce IQ.

Provides corporate governance, data privacy, AI usage boundaries,
and executive disclaimers.
"""

import streamlit as st
from ui.theme import get_current_theme


def render_terms_page() -> None:
    """Render corporate terms and conditions page."""
    theme = get_current_theme()

    st.title("📜 Terms of Service & Data Governance")
    st.caption("E-Commerce IQ Operating Guidelines, Security Guardrails & Executive Policies")

    st.markdown(
        f"""
        <div style="background: {theme['card_bg']}; border-left: 4px solid {theme['primary_color']}; border-radius: 8px; padding: 1.2rem; margin: 1rem 0 1.5rem 0;">
            <div style="font-weight: 700; color: {theme['text_color']}; font-size: 1.05rem;">
                🏛️ Platform Overview & Agreement
            </div>
            <div style="font-size: 0.9rem; color: {theme['text_color']}; margin-top: 0.3rem; line-height: 1.5;">
                Welcome to <b>E-Commerce IQ</b>. By accessing this platform, executive dashboards, and the <b>Shoplytic AI Copilot</b>, users and enterprise operators agree to the following data governance and operational guidelines.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    t1, t2, t3, t4, t5 = st.tabs([
        "1. Financial Integrity",
        "2. AI Guardrails",
        "3. Privacy & PII",
        "4. Advisory Disclaimer",
        "5. Attribution & IP"
    ])

    with t1:
        st.markdown(
            f"""
            #### 1. Deterministic Financial Calculations & Auditability
            - **Single Source of Truth**: All transactional figures (GMV, Net Revenue, completed orders, AOV, return rates) are derived directly from the underlying normalized relational database (`orders`, `order_items`, `products`, `returns`).
            - **Zero Financial Hallucination**: Large Language Models (LLMs) are strictly barred from performing raw arithmetic. All numbers presented in executive summaries must be backed by verified database rows.
            - **Accounting Boundaries**: Calculated margins represent gross product contribution margins based on unit sales and cost price ledgers.
            """
        )

    with t2:
        st.markdown(
            f"""
            #### 2. Shoplytic AI Copilot & AST Security Guardrails
            - **Read-Only Enforcement**: Shoplytic operates under strict Abstract Syntax Tree (AST) inspection. Only safe `SELECT` and `WITH` statements are permitted.
            - **Mutation Blocking**: The query gateway automatically intercepts and terminates any query containing mutation tokens (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, `--`, `;`).
            - **Bounded Execution**: All queries are limited to a maximum of 50 records to prevent denial-of-service or database starvation.
            """
        )

    with t3:
        st.markdown(
            f"""
            #### 3. Data Privacy & Customer PII Masking
            - **PII Protection**: Customer personally identifiable information (including email addresses, phone numbers, and physical shipping addresses) is anonymized or masked in analytical cohorts.
            - **Review Data**: Written review insights and sentiment metrics reflect aggregated textual feedback with customer identification separated.
            """
        )

    with t4:
        st.markdown(
            f"""
            #### 4. Executive Advisory & Decision Support Disclaimer
            - **Decision Support System**: E-Commerce IQ provides analytical intelligence and evidence-backed diagnostics. Strategic business decisions, inventory orders, and financial allocations remain the sole responsibility of the business leadership.
            - **Anomaly Diagnostics**: Root-cause diagnostic attributions (e.g., product manufacturing defects) represent statistical correlations derived from return rates, review sentiment, and transaction drops.
            """
        )

    with t5:
        st.markdown(
            f"""
            #### 5. Intellectual Property & Founder Attribution
            - **Project**: E-Commerce IQ
            - **Founder & Lead Architect**: **Alankrita Paul**
            - **Repository**: [github.com/AlankritaPaul/E-Commerce-IQ](https://github.com/AlankritaPaul/E-Commerce-IQ)
            - **License**: MIT License — open, auditable, and extensible for modern e-commerce decision intelligence.
            """
        )
