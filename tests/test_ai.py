import sys
from pathlib import Path
import unittest

_root = Path(__file__).resolve().parent.parent
for _p in (str(_root / "src"), str(_root)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ecommerce_iq.ai.llm_client import LLMClient
from ecommerce_iq.ai.text_to_sql import TextToSQLGenerator
from ecommerce_iq.ai.sql_guardrails import SQLGuardrail
from ecommerce_iq.ai.sentiment import SentimentAnalyzer
from ecommerce_iq.ai.advisor import BusinessAdvisor
from ecommerce_iq.ai.prompts import TEXT_TO_SQL_SYSTEM_PROMPT, BUSINESS_ADVISOR_SYSTEM_PROMPT


class TestAIAndGuardrails(unittest.TestCase):
    def test_sql_guardrail_allows_safe_select(self):
        """Verify that safe read-only SELECT queries are approved."""
        guardrail = SQLGuardrail()

        safe_query_1 = "SELECT customer_id, SUM(total_amount) FROM orders GROUP BY customer_id;"
        is_safe, reason = guardrail.validate_query(safe_query_1)
        self.assertTrue(is_safe, f"Safe query was rejected: {reason}")

        safe_query_2 = "WITH monthly_rev AS (SELECT strftime('%Y-%m', order_date) AS mo, SUM(total_amount) AS rev FROM orders GROUP BY 1) SELECT * FROM monthly_rev"
        is_safe, reason = guardrail.validate_query(safe_query_2)
        self.assertTrue(is_safe, f"CTE query was rejected: {reason}")

    def test_sql_guardrail_blocks_destructive_mutations(self):
        """Verify that DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE are blocked."""
        guardrail = SQLGuardrail()

        dangerous_queries = [
            "DROP TABLE orders;",
            "DELETE FROM customers WHERE id = 1;",
            "UPDATE products SET retail_price = 0;",
            "INSERT INTO orders (total_amount) VALUES (100);",
            "ALTER TABLE orders ADD COLUMN hack TEXT;",
            "TRUNCATE TABLE reviews;",
            "SELECT * FROM orders; DROP TABLE users;",  # Chained query
        ]

        for query in dangerous_queries:
            is_safe, reason = guardrail.validate_query(query)
            self.assertFalse(is_safe, f"Dangerous query was unexpectedly permitted: '{query}'")

    def test_sql_guardrail_rejects_empty_query(self):
        """Verify empty queries are rejected."""
        guardrail = SQLGuardrail()
        is_safe, reason = guardrail.validate_query("")
        self.assertFalse(is_safe)

    def test_ai_classes_instantiation(self):
        """Verify that AI engine classes can be instantiated."""
        client = LLMClient(provider="gemini")
        self.assertEqual(client.provider, "gemini")

        generator = TextToSQLGenerator(llm_client=client)
        self.assertIs(generator.llm, client)

        sentiment = SentimentAnalyzer()
        self.assertIsNotNone(sentiment)

        advisor = BusinessAdvisor(llm_client=client)
        self.assertIs(advisor.llm, client)

        # Prompts are populated
        self.assertIn("SELECT", TEXT_TO_SQL_SYSTEM_PROMPT)
        self.assertIn("Root Cause", BUSINESS_ADVISOR_SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
