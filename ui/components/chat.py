"""
Conversational AI Copilot Chat Component.

Provides an interactive natural language interface for business owners,
featuring query suggestions, instant SQL safety inspection, and data-grounded answers.
"""

from typing import Any, Dict, List, Optional
from ecommerce_iq.ai.query_engine import NaturalLanguageQueryEngine
from ecommerce_iq.models.schemas import AIQueryResponse
from ui.components.cards import render_table


SAMPLE_QUESTIONS = [
    "What was our total sales revenue and order volume?",
    "What are our top 5 best selling products?",
    "Which products have the highest return rate?",
    "What are customers saying about battery life in reviews?",
    "How many customers are repeat buyers?",
    "What is our revenue breakdown by category?",
]


def render_copilot_chat(query_engine: Optional[NaturalLanguageQueryEngine] = None) -> None:
    """
    Render interactive AI Copilot conversation panel in Streamlit.
    """
    try:
        import streamlit as st

        engine = query_engine or NaturalLanguageQueryEngine()

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {
                    "role": "assistant",
                    "content": (
                        "Hello! I am your **E-Commerce IQ Business Copilot**. "
                        "Ask me any question about your revenue, sales trends, bestselling products, "
                        "customer reviews, or returns, and I will query the database securely."
                    ),
                    "response_obj": None
                }
            ]

        st.subheader("🤖 Natural-Language Executive Copilot")
        st.caption("Ask questions in simple business English. All queries are verified by SQL guardrails before execution.")

        # Quick Question Buttons
        st.markdown("**Suggested Questions:**")
        cols = st.columns(3)
        selected_prompt = None
        for idx, prompt in enumerate(SAMPLE_QUESTIONS):
            col = cols[idx % 3]
            if col.button(prompt, key=f"quick_btn_{idx}", use_container_width=True):
                selected_prompt = prompt

        # Display Conversation History
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                resp: Optional[AIQueryResponse] = msg.get("response_obj")
                if resp and resp.is_safe:
                    with st.expander("🔍 Technical SQL Inspection & Audit", expanded=False):
                        st.caption(f"⏱️ Runtime: `{resp.execution_time_ms:.1f}ms` | Status: `Guardrail Approved`")
                        st.code(resp.generated_sql, language="sql")
                        if resp.data:
                            render_table(resp.data[:10])

        # Handle New Query Input
        user_input = st.chat_input("Ask a business question (e.g. 'What is our monthly revenue in 2025?')...")
        prompt_to_run = selected_prompt or user_input

        if prompt_to_run:
            # Display user message
            st.session_state.chat_history.append({"role": "user", "content": prompt_to_run, "response_obj": None})
            with st.chat_message("user"):
                st.markdown(prompt_to_run)

            # Generate AI answer
            with st.chat_message("assistant"):
                with st.spinner("Analyzing business data and verifying security guardrails..."):
                    response: AIQueryResponse = engine.ask(prompt_to_run)

                    if not response.is_safe:
                        error_text = f"⚠️ **Query Intercepted by Security Guardrails**: {response.error_message}"
                        st.error(error_text)
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": error_text,
                            "response_obj": response
                        })
                    else:
                        st.markdown(response.executive_summary)
                        with st.expander("🔍 Technical SQL Inspection & Audit", expanded=False):
                            st.caption(f"⏱️ Runtime: `{response.execution_time_ms:.1f}ms` | Status: `Guardrail Approved`")
                            st.code(response.generated_sql, language="sql")
                            if response.data:
                                render_table(response.data[:10])

                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response.executive_summary,
                            "response_obj": response
                        })

    except Exception:
        pass
