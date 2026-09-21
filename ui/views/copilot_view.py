"""
Natural Language AI Copilot View.

Dedicated conversational assistant panel for business executives to query
business metrics in plain English with SQL safety inspection and data grounding.
"""

import streamlit as st
from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.ai.query_engine import NaturalLanguageQueryEngine
from ui.components.chat import render_copilot_chat


def render_copilot_page(db: DatabaseManager) -> None:
    """Render full conversational AI Copilot page."""
    query_engine = NaturalLanguageQueryEngine(db_manager=db)
    render_copilot_chat(query_engine)
