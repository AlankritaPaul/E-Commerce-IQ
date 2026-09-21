"""
Natural-Language Business Query Engine & Executive Copilot.

Coordinates the end-to-end natural-language inquiry workflow:
1. Natural language question parsing & schema-grounded SQL translation
2. Strict SQL Guardrail AST verification (blocking mutations & SQL injection)
3. Safe database execution with row limits
4. Executive narrative synthesis translating raw data into business insights
"""

import time
from typing import Any, Dict, List, Optional
from ecommerce_iq.ai.advisor import BusinessAdvisor
from ecommerce_iq.ai.llm_client import LLMClient
from ecommerce_iq.ai.sql_guardrails import SQLGuardrail
from ecommerce_iq.ai.text_to_sql import TextToSQLGenerator
from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.models.schemas import AIQueryRequest, AIQueryResponse


class NaturalLanguageQueryEngine:
    """
    Orchestrates the natural-language question-to-executive answer pipeline.
    """

    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        llm_client: Optional[LLMClient] = None
    ) -> None:
        self.db = db_manager or DatabaseManager()
        self.llm = llm_client or LLMClient()
        self.sql_generator = TextToSQLGenerator(self.llm)
        self.guardrail = SQLGuardrail()
        self.advisor = BusinessAdvisor(self.llm)

    def ask(self, user_query: str) -> AIQueryResponse:
        """
        Process a business owner's question and produce a safe, data-grounded executive answer.
        """
        start_time = time.perf_counter()

        if not user_query or not user_query.strip():
            return AIQueryResponse(
                user_query=user_query,
                generated_sql="",
                is_safe=False,
                error_message="Question cannot be empty.",
                execution_time_ms=0.0
            )

        # 1. Translate natural language question to schema-grounded SQL
        intent_cat = self.sql_generator.get_intent_category(user_query)
        generated_sql = self.sql_generator.generate_sql(user_query)

        # 2. Enforce SQL Security Guardrails
        is_safe, rejection_reason = self.guardrail.validate_query(generated_sql)
        if not is_safe:
            elapsed = round((time.perf_counter() - start_time) * 1000.0, 2)
            return AIQueryResponse(
                user_query=user_query,
                generated_sql=generated_sql,
                is_safe=False,
                data=None,
                executive_summary=None,
                error_message=f"Security Guardrail Rejection: {rejection_reason}",
                execution_time_ms=elapsed
            )

        # 3. Sanitize and enforce safe row bounds
        bounded_sql = self.guardrail.sanitize_and_limit(generated_sql, max_limit=50)

        # 4. Execute validated query against database
        try:
            data = self.db.execute_query(bounded_sql)
        except Exception as e:
            elapsed = round((time.perf_counter() - start_time) * 1000.0, 2)
            return AIQueryResponse(
                user_query=user_query,
                generated_sql=bounded_sql,
                is_safe=False,
                data=None,
                executive_summary=None,
                error_message=f"Database Execution Error: {str(e)}",
                execution_time_ms=elapsed
            )

        # 5. Synthesize executive answer
        narrative = self.advisor.synthesize_answer(
            question=user_query,
            sql_query=bounded_sql,
            query_results=data,
            intent_category=intent_cat
        )

        elapsed = round((time.perf_counter() - start_time) * 1000.0, 2)

        return AIQueryResponse(
            user_query=user_query,
            generated_sql=bounded_sql,
            is_safe=True,
            data=data,
            executive_summary=narrative,
            error_message=None,
            execution_time_ms=elapsed
        )
