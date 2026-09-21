"""
Natural Language AI Copilot View.

Dedicated conversational assistant panel for business executives to query
business metrics in plain English with SQL safety inspection and data grounding.
"""

import streamlit as st
from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.ai.query_engine import NaturalLanguageQueryEngine
from ui.components.chat import render_copilot_chat


from typing import Any, Optional


def render_copilot_page(db_or_engine: Optional[Any] = None) -> None:
    """Render full conversational AI Copilot page."""
    if isinstance(db_or_engine, NaturalLanguageQueryEngine):
        query_engine = db_or_engine
    elif isinstance(db_or_engine, DatabaseManager):
        query_engine = NaturalLanguageQueryEngine(db_manager=db_or_engine)
    else:
        query_engine = NaturalLanguageQueryEngine()
    render_copilot_chat(query_engine)
