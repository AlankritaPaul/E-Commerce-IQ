"""
AI and Natural Language Processing Package.

Provides LLM provider abstractions, schema-grounded Text-to-SQL generation,
AST-based SQL security guardrails, sentiment analysis, executive insight generation,
and the end-to-end natural language business query engine.
"""

from ecommerce_iq.ai.sentiment import SentimentAnalyzer
from ecommerce_iq.ai.sql_guardrails import SQLGuardrail
from ecommerce_iq.ai.text_to_sql import TextToSQLGenerator
from ecommerce_iq.ai.advisor import BusinessAdvisor
from ecommerce_iq.ai.llm_client import LLMClient
from ecommerce_iq.ai.query_engine import NaturalLanguageQueryEngine
from ecommerce_iq.ai.interpretation import AnalyticsInterpreter, NumericalGroundingVerifier

__all__ = [
    "SentimentAnalyzer",
    "SQLGuardrail",
    "TextToSQLGenerator",
    "BusinessAdvisor",
    "LLMClient",
    "NaturalLanguageQueryEngine",
    "AnalyticsInterpreter",
    "NumericalGroundingVerifier",
]

