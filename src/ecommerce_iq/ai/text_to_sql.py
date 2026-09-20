"""
Schema-Grounded Text-to-SQL Generator.

Translates natural language questions from business owners into optimized,
syntactically valid SQL queries grounded in the e-commerce schema.
"""

from typing import Any, Optional


class TextToSQLGenerator:
    """
    Converts natural language user questions to SQL queries.
    Implementation will be activated in Phase 5.
    """

    def __init__(self, llm_client: Any, schema_metadata: Optional[dict] = None) -> None:
        self.llm = llm_client
        self.schema_metadata = schema_metadata

    def generate_sql(self, natural_language_query: str) -> str:
        """
        Produce a safe, schema-grounded SQL query from a user question.
        """
        raise NotImplementedError("Text-to-SQL generation will be implemented in Phase 5.")
