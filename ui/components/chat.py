"""
Conversational AI Copilot: Shoplytic.

Features:
- Branded 'Shoplytic' handwritten typography & dedicated logo
- Explicit Search input & Search button
- Search history tracking with quick re-run chips
- Automatic dynamic interactive Plotly chart generation for query results
- Strict SQL safety inspection & tabular data auditing
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from ecommerce_iq.ai.query_engine import NaturalLanguageQueryEngine
from ecommerce_iq.models.schemas import AIQueryResponse
from ui.components.cards import render_table
from ui.theme import get_current_theme


SAMPLE_QUESTIONS = [
    "What was our total sales revenue and order volume?",
    "What are our top 5 best selling products?",
    "Which products have the highest return rate?",
    "What is our revenue breakdown by category?",
    "How many customers are repeat buyers?",
    "What are customers saying about battery life in reviews?",
]


def generate_dynamic_chart(data: List[Dict[str, Any]], query: str, theme: Dict[str, Any]) -> Optional[Any]:
    """
    Intelligently generate an interactive Plotly chart based on the data columns and shape.
    """
    if not data or len(data) == 0:
        return None

    first_row = data[0]
    keys = list(first_row.keys())

    # Identify numerical vs string columns
    numeric_keys = [
        k for k in keys
        if isinstance(first_row[k], (int, float)) and not k.endswith("_id")
    ]
    text_keys = [
        k for k in keys
        if isinstance(first_row[k], str) or k in ("sku", "month", "order_date", "category_name", "title", "name", "reason")
    ]

    primary_color = theme.get("primary_color", "#2563EB")
    template = theme.get("plotly_template", "plotly_white")

    try:
        # Case 1: Multiple rows with categorical label + numeric metric (e.g. Top Products, Categories, Returns)
        if len(data) > 1 and text_keys and numeric_keys:
            cat_col = text_keys[0]
            num_col = numeric_keys[-1]  # usually the aggregate total or revenue

            labels = [str(r.get(cat_col, ""))[:28] for r in data]
            values = [float(r.get(num_col, 0) or 0) for r in data]

            col_display = num_col.replace("_", " ").title()
            cat_display = cat_col.replace("_", " ").title()

            if len(data) <= 6 and "category" in cat_col:
                # Donut Chart for categories
                fig = px.pie(
                    names=labels,
                    values=values,
                    hole=0.45,
                    title=f"Distribution of {col_display} by {cat_display}",
                    template=template
                )
            else:
                # Horizontal or Vertical Bar Chart
                fig = px.bar(
                    x=values,
                    y=labels,
                    orientation="h",
                    labels={"x": col_display, "y": cat_display},
                    title=f"{col_display} by {cat_display}",
                    template=template,
                    color_discrete_sequence=[primary_color]
                )
                fig.update_layout(yaxis=dict(autorange="reversed"))

            fig.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                height=320
            )
            return fig

        # Case 2: Time-series trajectory (month/date + numeric metric)
        date_candidates = [k for k in text_keys if any(d in k.lower() for d in ("month", "date", "year"))]
        if len(data) > 1 and date_candidates and numeric_keys:
            d_col = date_candidates[0]
            num_col = numeric_keys[0]

            dates = [str(r.get(d_col, "")) for r in data]
            vals = [float(r.get(num_col, 0) or 0) for r in data]

            fig = px.line(
                x=dates,
                y=vals,
                markers=True,
                title=f"{num_col.replace('_', ' ').title()} Over Time",
                template=template,
                color_discrete_sequence=[primary_color]
            )
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=300)
            return fig

        # Case 3: Single record with multiple numeric KPI columns (e.g. Total GMV, Orders, AOV)
        if len(data) == 1 and len(numeric_keys) >= 2:
            labels = [k.replace("_", " ").title() for k in numeric_keys]
            vals = [float(first_row[k] or 0) for k in numeric_keys]

            fig = px.bar(
                x=labels,
                y=vals,
                title="Performance Metric Comparison",
                template=template,
                color_discrete_sequence=[primary_color]
            )
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=280)
            return fig

    except Exception:
        return None

    return None


def render_copilot_chat(query_engine: Optional[NaturalLanguageQueryEngine] = None) -> None:
    """
    Render interactive Shoplytic Copilot with handwritten branding,
    dedicated search button, search history, and automatic data graph generation.
    """
    theme = get_current_theme()
    engine = query_engine or NaturalLanguageQueryEngine()
    shoplytic_logo_path = Path(__file__).resolve().parent.parent.parent / "docs" / "images" / "icons" / "shoplytic_logo.svg"

    # Initialize Session States
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am **Shoplytic**, your Conversational Business Copilot. "
                    "Ask me any question in simple English about your store's sales, product margins, "
                    "customer retention, or return leakage, and I will analyze the data with interactive graphs!"
                ),
                "response_obj": None
            }
        ]

    if "search_history" not in st.session_state:
        st.session_state.search_history = []

    # 1. Shoplytic Brand Header (Cursive Handwriting + Logo)
    header_col1, header_col2 = st.columns([1, 6])
    with header_col1:
        if shoplytic_logo_path.exists():
            st.image(str(shoplytic_logo_path), width=64)
        else:
            st.markdown("### 🛍️")

    with header_col2:
        st.markdown(
            f"""
            <div>
                <span class="shoplytic-title">Shoplytic</span>
                <span style="font-size: 0.95rem; font-weight: 600; color: {theme['secondary_text']}; margin-left: 8px;">
                    Conversational AI & Decision Copilot
                </span>
                <div style="font-size: 0.82rem; color: {theme['secondary_text']};">
                    Natural-language SQL engine with strict AST guardrails & instant data graph generation.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # 2. Search History Panel (Recent Searches)
    if st.session_state.search_history:
        with st.expander("🕒 Recent Search History", expanded=False):
            st.caption("Click any past search to re-run it:")
            hist_cols = st.columns(3)
            for h_idx, past_q in enumerate(reversed(st.session_state.search_history[-6:])):
                col = hist_cols[h_idx % 3]
                if col.button(f"🔍 {past_q[:35]}...", key=f"hist_btn_{h_idx}", use_container_width=True):
                    st.session_state.active_search_prompt = past_q

    # 3. Suggested Questions Chips
    st.markdown("**💡 Suggested Inquiries:**")
    cols = st.columns(3)
    suggested_prompt = None
    for idx, prompt in enumerate(SAMPLE_QUESTIONS):
        col = cols[idx % 3]
        if col.button(prompt, key=f"sugg_btn_{idx}", use_container_width=True):
            suggested_prompt = prompt

    # 4. Search Input Bar + Dedicated Search Button
    st.markdown("<br/>", unsafe_allow_html=True)
    scol1, scol2 = st.columns([5, 1])

    with scol1:
        search_query_input = st.text_input(
            "Search query",
            placeholder="Ask Shoplytic anything (e.g. 'What are our top 5 best selling products?')...",
            label_visibility="collapsed",
            key="shoplytic_search_input"
        )

    with scol2:
        search_button_clicked = st.button("🔍 Search", key="btn_exec_search", use_container_width=True)

    # Chat Input at bottom for conversational flow
    chat_box_input = st.chat_input("Or type your question here...")

    # Determine prompt to run
    prompt_to_run = (
        suggested_prompt
        or (search_query_input if search_button_clicked and search_query_input else None)
        or chat_box_input
        or st.session_state.pop("active_search_prompt", None)
    )

    # 5. Display Conversation History with Dynamic Graphs
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            resp: Optional[AIQueryResponse] = msg.get("response_obj")
            if resp and resp.is_safe and resp.data:
                # Dynamic Plotly Graph
                chart = generate_dynamic_chart(resp.data, resp.user_query, theme)
                if chart:
                    st.plotly_chart(chart, use_container_width=True)

                # Tabular Data Preview
                render_table(resp.data[:8])

                # Technical SQL Inspection
                with st.expander("🔍 Technical SQL Inspection & Audit", expanded=False):
                    st.caption(f"⏱️ Runtime: `{resp.execution_time_ms:.1f}ms` | Status: `Guardrail Approved`")
                    st.code(resp.generated_sql, language="sql")

    # 6. Execute New Prompt
    if prompt_to_run:
        # Add to search history if not already present
        if prompt_to_run not in st.session_state.search_history:
            st.session_state.search_history.append(prompt_to_run)

        # Append User Message
        st.session_state.chat_history.append({"role": "user", "content": prompt_to_run, "response_obj": None})
        with st.chat_message("user"):
            st.markdown(prompt_to_run)

        # Generate Shoplytic Answer
        with st.chat_message("assistant"):
            with st.spinner("Shoplytic is querying verified database records and building data graph..."):
                response: AIQueryResponse = engine.ask(prompt_to_run)

                if not response.is_safe:
                    error_text = f"🚨 **Security Guardrail Interception**: {response.error_message}"
                    st.error(error_text)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_text,
                        "response_obj": response
                    })
                else:
                    st.markdown(response.executive_summary)

                    # Generate and Display Dynamic Graph
                    if response.data:
                        chart = generate_dynamic_chart(response.data, prompt_to_run, theme)
                        if chart:
                            st.plotly_chart(chart, use_container_width=True)

                        render_table(response.data[:8])

                    with st.expander("🔍 Technical SQL Inspection & Audit", expanded=False):
                        st.caption(f"⏱️ Runtime: `{response.execution_time_ms:.1f}ms` | Status: `Guardrail Approved`")
                        st.code(response.generated_sql, language="sql")

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response.executive_summary,
                        "response_obj": response
                    })
