"""
Interactive User Guide & How-to-Use View for E-Commerce IQ.

Provides a clear, beginner-friendly walkthrough of the platform,
prompt cheatsheet for Shoplytic Copilot, theme customization guide, and FAQs.
"""

import streamlit as st
from ui.theme import get_current_theme


def render_guide_page() -> None:
    """Render the comprehensive How to Use guide."""
    theme = get_current_theme()

    st.title("📖 How to Use E-Commerce IQ")
    st.caption("A beginner-to-executive guide for founders, operators, and evaluators.")

    st.markdown(
        f"""
        <div style="background: {theme['card_bg']}; border-left: 4px solid {theme['primary_color']}; border-radius: 8px; padding: 1.2rem; margin: 1rem 0 1.5rem 0;">
            <div style="font-weight: 700; color: {theme['text_color']}; font-size: 1.05rem;">
                🚀 Welcome to Your Executive Command Center
            </div>
            <div style="font-size: 0.9rem; color: {theme['text_color']}; margin-top: 0.3rem; line-height: 1.5;">
                <b>E-Commerce IQ</b> transforms raw store data into clear profit insights, visual charts, and conversational intelligence. Follow this 3-step quick start to get the most out of your experience.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    g1, g2, g3, g4, g5 = st.tabs([
        "⚡ 3-Step Quick Start",
        "🤖 Shoplytic Prompt Cheatsheet",
        "🔌 Connecting Your Store",
        "🎨 Customizing Themes",
        "❓ Frequently Asked Questions"
    ])

    with g1:
        st.markdown("### ⚡ Quick Start in 3 Simple Steps")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div class="custom-card" style="padding: 1.2rem; height: 100%;">
                    <div style="font-size: 1.2rem; font-weight: 800; color: {theme['primary_color']};">1. Check Dashboard</div>
                    <div style="font-size: 0.88rem; color: {theme['text_color']}; margin-top: 0.5rem; line-height: 1.5;">
                        Click <b>📊 Executive Dashboard</b> in the sidebar to immediately see your Gross Revenue, Net Profit, completed order volume, and category donut chart.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div class="custom-card" style="padding: 1.2rem; height: 100%;">
                    <div style="font-size: 1.2rem; font-weight: 800; color: {theme['primary_color']};">2. Ask Shoplytic</div>
                    <div style="font-size: 0.88rem; color: {theme['text_color']}; margin-top: 0.5rem; line-height: 1.5;">
                        Click <b>🤖 Shoplytic Copilot</b>. Type any question in plain English (or click a suggested chip) and hit <b>Search</b> to get instant numbers, narratives, and data graphs!
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div class="custom-card" style="padding: 1.2rem; height: 100%;">
                    <div style="font-size: 1.2rem; font-weight: 800; color: {theme['primary_color']};">3. Deep Dive</div>
                    <div style="font-size: 0.88rem; color: {theme['text_color']}; margin-top: 0.5rem; line-height: 1.5;">
                        Explore <b>Product Economics</b> to find dead stock, <b>Customer RFM</b> for loyalty cohorts, or <b>Sales Collapse Diagnosis</b> to investigate why revenue contracted.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with g2:
        st.markdown("### 🤖 Shoplytic Prompt Cheatsheet")
        st.write("You can ask Shoplytic questions in everyday English. Here are the most valuable inquiries to copy and try:")

        pcol1, pcol2 = st.columns(2)

        with pcol1:
            st.markdown("**💰 Sales & Financials**")
            st.code("What was our total sales revenue and order volume?", language="text")
            st.code("What is our revenue breakdown by category?", language="text")
            st.code("What was our monthly revenue in 2025?", language="text")

            st.markdown("**🛍️ Products & Unit Economics**")
            st.code("What are our top 5 best selling products?", language="text")
            st.code("Which products have the highest profit margins?", language="text")

        with pcol2:
            st.markdown("**🔄 Returns & Quality Issues**")
            st.code("Which products have the highest return rate?", language="text")
            st.code("What are the top reasons customers return orders?", language="text")

            st.markdown("**👥 Customer Retention & Reviews**")
            st.code("How many customers are repeat buyers?", language="text")
            st.code("What are customers saying about battery life in reviews?", language="text")

    with g3:
        st.markdown("### 🔌 How to Connect Your Own Store")
        st.write(
            """
            1. Click **`🔌 Connect Store / Upload Data`** in the sidebar.
            2. Choose your preferred connection method:
               - **Option 1 (CSV Files)**: Drag & drop your `orders.csv`, `products.csv`, and `returns.csv` files.
               - **Option 2 (Database)**: Enter your read-only database connection URL (PostgreSQL / MySQL / Snowflake).
               - **Option 3 (API Sync)**: Connect directly to Shopify, WooCommerce, or Stripe.
            3. Click **Ingest & Process Data**. The app validates your data and updates all dashboards instantly!
            """
        )

    with g4:
        st.markdown("### 🎨 Customizing Themes & Vibes")
        st.write(
            """
            In the sidebar under **🎨 Theme & Vibe**, you can switch between 3 distinct themes at any time:
            - 🏛️ **Corporate Executive**: Crisp white/slate background with deep navy blue, emerald green, and sharp cards (ideal for board meetings and investor presentations).
            - ⚡ **Modern Dark Mode**: Deep cosmic obsidian background with glowing neon cyan/purple accents (ideal for evening monitoring and modern tech aesthetic).
            - ⚜️ **Luxury Minimalist**: Warm silk ivory background with deep charcoal typography and metallic gold borders (ideal for high-end boutique brands).
            """
        )

    with g5:
        st.markdown("### ❓ Frequently Asked Questions (FAQ)")
        with st.expander("Is my data safe from accidental deletion?"):
            st.write("Yes! E-Commerce IQ enforces strict Abstract Syntax Tree (AST) guardrails. Shoplytic is restricted to read-only `SELECT` queries and cannot execute `DROP`, `DELETE`, or `UPDATE` commands.")

        with st.expander("Can the AI hallucinate or invent fake revenue numbers?"):
            st.write("No! Unlike generic chatbots, E-Commerce IQ never allows the LLM to do raw arithmetic. All numbers are calculated by deterministic SQL queries running directly against your relational database.")

        with st.expander("Can I use this app on my phone or tablet?"):
            st.write("Yes! The web application is fully responsive and adjusts cleanly to mobile browsers, tablets, and desktop screens.")
