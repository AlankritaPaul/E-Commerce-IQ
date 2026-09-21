"""
Unit and Integration Tests for AI Natural-Language Query Layer & SQL Guardrails.

Verifies:
- SQLGuardrail AST verification & security enforcement (blocking mutations, semicolon chaining, unauthorized tables)
- SQLGuardrail sanitize_and_limit enforcement
- TextToSQLGenerator schema-grounded query translation & intent mapping
- BusinessAdvisor executive narrative synthesis & metric formatting
- NaturalLanguageQueryEngine end-to-end question answering pipeline
- Guardrail protection against destructive SQL injection attempts
"""

import sys
from pathlib import Path
import unittest

_root = Path(__file__).resolve().parent.parent
for _p in (str(_root / "src"), str(_root)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ecommerce_iq.ai.advisor import BusinessAdvisor
from ecommerce_iq.ai.llm_client import LLMClient
from ecommerce_iq.ai.query_engine import NaturalLanguageQueryEngine
from ecommerce_iq.ai.prompts import TEXT_TO_SQL_SYSTEM_PROMPT, BUSINESS_ADVISOR_SYSTEM_PROMPT
from ecommerce_iq.ai.sentiment import SentimentAnalyzer
from ecommerce_iq.ai.sql_guardrails import SQLGuardrail
from ecommerce_iq.ai.text_to_sql import TextToSQLGenerator
from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.models.schemas import AIQueryResponse


class TestSQLGuardrail(unittest.TestCase):
    """Test SQL safety guardrails and AST verification."""

    def setUp(self):
        self.guardrail = SQLGuardrail()

    def test_sql_guardrail_allows_safe_select(self):
        """Verify that safe read-only SELECT queries are approved."""
        safe_query_1 = "SELECT customer_id, SUM(total_amount) FROM orders GROUP BY customer_id;"
        is_safe, reason = self.guardrail.validate_query(safe_query_1)
        self.assertTrue(is_safe, f"Safe query was rejected: {reason}")

        safe_query_2 = (
            "WITH monthly_rev AS ("
            "SELECT strftime('%Y-%m', order_date) AS mo, SUM(total_amount) AS rev FROM orders GROUP BY 1"
            ") SELECT * FROM monthly_rev"
        )
        is_safe, reason = self.guardrail.validate_query(safe_query_2)
        self.assertTrue(is_safe, f"CTE query was rejected: {reason}")

    def test_sql_guardrail_blocks_destructive_mutations(self):
        """Verify that DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE are blocked."""
        dangerous_queries = [
            "DROP TABLE orders;",
            "DELETE FROM customers WHERE id = 1;",
            "UPDATE products SET retail_price = 0;",
            "INSERT INTO orders (total_amount) VALUES (100);",
            "ALTER TABLE orders ADD COLUMN hack TEXT;",
            "TRUNCATE TABLE reviews;",
            "SELECT * FROM orders; DROP TABLE users;",  # Chained query
            "EXEC xp_cmdshell('dir');",
        ]

        for query in dangerous_queries:
            is_safe, reason = self.guardrail.validate_query(query)
            self.assertFalse(is_safe, f"Dangerous query was unexpectedly permitted: '{query}'")
            self.assertIsNotNone(reason)

    def test_sql_guardrail_blocks_unauthorized_tables(self):
        """Verify that queries referencing system tables or unauthorized schemas are rejected."""
        unauthorized = [
            "SELECT * FROM sqlite_master;",
            "SELECT * FROM sqlite_sequence;",
            "SELECT * FROM system_passwords;",
            "SELECT * FROM secret_credentials JOIN orders ON 1=1;",
        ]
        for query in unauthorized:
            is_safe, reason = self.guardrail.validate_query(query)
            self.assertFalse(is_safe, f"Unauthorized table access permitted: '{query}'")
            self.assertIn("unauthorized", reason.lower())

    def test_sql_guardrail_rejects_empty_query(self):
        """Verify empty or whitespace-only queries are rejected."""
        self.assertFalse(self.guardrail.validate_query("")[0])
        self.assertFalse(self.guardrail.validate_query("   ")[0])

    def test_sanitize_and_limit(self):
        """Verify LIMIT enforcement and capping."""
        # Query without limit gets default limit
        q1 = "SELECT * FROM products"
        bounded1 = self.guardrail.sanitize_and_limit(q1, max_limit=50)
        self.assertIn("LIMIT 50", bounded1)

        # Query with smaller limit is preserved
        q2 = "SELECT * FROM products LIMIT 10"
        bounded2 = self.guardrail.sanitize_and_limit(q2, max_limit=50)
        self.assertIn("LIMIT 10", bounded2)

        # Query with excessive limit is clamped
        q3 = "SELECT * FROM products LIMIT 1000"
        bounded3 = self.guardrail.sanitize_and_limit(q3, max_limit=50)
        self.assertIn("LIMIT 50", bounded3)


class TestTextToSQLGenerator(unittest.TestCase):
    """Test natural-language question translation and parameter extraction."""

    def setUp(self):
        self.generator = TextToSQLGenerator()

    def test_intent_classification(self):
        """Verify intent categories are accurately identified."""
        self.assertEqual(
            self.generator.get_intent_category("What was our total revenue in 2025?"),
            "revenue"
        )
        self.assertEqual(
            self.generator.get_intent_category("What are our top 5 best selling products?"),
            "top_products"
        )
        self.assertEqual(
            self.generator.get_intent_category("Which items are dead stock or slow moving?"),
            "underperforming"
        )
        self.assertEqual(
            self.generator.get_intent_category("Show me return rates and refund amounts"),
            "returns"
        )
        self.assertEqual(
            self.generator.get_intent_category("What are customers saying in reviews?"),
            "reviews"
        )
        self.assertEqual(
            self.generator.get_intent_category("How many repeat customers do we have?"),
            "customers"
        )

    def test_sql_generation_templates(self):
        """Verify generated SQL contains expected tables, columns, and filters."""
        sql_rev = self.generator.generate_sql("What is our monthly sales revenue?")
        self.assertIn("orders", sql_rev)
        self.assertIn("SUM(total_amount)", sql_rev)

        sql_top = self.generator.generate_sql("Top 10 best sellers")
        self.assertIn("order_items", sql_top)
        self.assertIn("LIMIT 10", sql_top)

        sql_returns = self.generator.generate_sql("Highest returned products")
        self.assertIn("returns", sql_returns)
        self.assertIn("return_rate", sql_returns.lower())

    def test_direct_sql_passthrough(self):
        """Verify direct SQL inputs are passed through to be evaluated by the guardrail."""
        direct_sql = "SELECT product_id, title FROM products WHERE retail_price > 100;"
        self.assertEqual(self.generator.generate_sql(direct_sql), direct_sql)


class TestBusinessAdvisor(unittest.TestCase):
    """Test narrative synthesis from structured tabular query results."""

    def setUp(self):
        self.advisor = BusinessAdvisor()

    def test_empty_results_handling(self):
        """Verify empty results produce clear informative feedback."""
        narrative = self.advisor.synthesize_answer(
            question="What were the sales of widget XYZ?",
            sql_query="SELECT * FROM products WHERE title = 'XYZ'",
            query_results=[]
        )
        self.assertIn("No records found", narrative)

    def test_revenue_answer_synthesis(self):
        """Verify revenue synthesis highlights total revenue and monthly figures."""
        sample_monthly = [
            {"month": "2025-01", "total_orders": 120, "total_revenue": 15400.50},
            {"month": "2025-02", "total_orders": 140, "total_revenue": 18200.00},
        ]
        monthly_narrative = self.advisor.synthesize_answer(
            question="What is our monthly revenue breakdown?",
            sql_query="SELECT ...",
            query_results=sample_monthly,
            intent_category="revenue"
        )
        self.assertIn("$15,400.50", monthly_narrative)
        self.assertIn("Monthly Revenue Breakdown", monthly_narrative)

        sample_total = [
            {"total_orders": 260, "total_revenue": 33600.50, "average_order_value": 129.23}
        ]
        total_narrative = self.advisor.synthesize_answer(
            question="What is our total revenue for 2025?",
            sql_query="SELECT ...",
            query_results=sample_total,
            intent_category="revenue"
        )
        self.assertIn("$33,600.50", total_narrative)
        self.assertIn("Key Takeaway", total_narrative)

    def test_top_products_synthesis(self):
        """Verify top products synthesis lists products and sales volumes."""
        sample_data = [
            {"title": "AuraSound Headphones", "units_sold": 450, "total_revenue": 89955.00},
            {"title": "Smart Watch Ultra", "units_sold": 220, "total_revenue": 43978.00},
        ]
        narrative = self.advisor.synthesize_answer(
            question="What are our top products?",
            sql_query="SELECT ...",
            query_results=sample_data,
            intent_category="top_products"
        )
        self.assertIn("AuraSound Headphones", narrative)
        self.assertIn("Smart Watch Ultra", narrative)
        self.assertIn("450 units", narrative)


class TestNaturalLanguageQueryEngine(unittest.TestCase):
    """Integration tests for end-to-end question answering pipeline."""

    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseManager()
        cls.engine = NaturalLanguageQueryEngine(db_manager=cls.db)

    def test_revenue_inquiry_end_to_end(self):
        """Test executive revenue inquiry execution and answer generation."""
        response = self.engine.ask("What is our total sales revenue and order volume?")
        self.assertIsInstance(response, AIQueryResponse)
        self.assertTrue(response.is_safe)
        self.assertIsNone(response.error_message)
        self.assertIsNotNone(response.data)
        self.assertGreater(len(response.data), 0)
        self.assertIsNotNone(response.executive_summary)
        self.assertIn("$", response.executive_summary)

    def test_top_products_inquiry_end_to_end(self):
        """Test top bestsellers inquiry execution."""
        response = self.engine.ask("What are our top 5 best selling products?")
        self.assertTrue(response.is_safe)
        self.assertIsNotNone(response.data)
        self.assertLessEqual(len(response.data), 5)
        self.assertIn("top", response.executive_summary.lower())

    def test_returns_inquiry_end_to_end(self):
        """Test returns and refunds inquiry execution."""
        response = self.engine.ask("Which products have the highest return rates?")
        self.assertTrue(response.is_safe)
        self.assertIsNotNone(response.data)
        self.assertIn("return", response.executive_summary.lower())

    def test_repeat_customers_inquiry_end_to_end(self):
        """Test customer retention inquiry execution."""
        response = self.engine.ask("How many customers are repeat buyers?")
        self.assertTrue(response.is_safe)
        self.assertIsNotNone(response.data)
        self.assertIn("repeat", response.executive_summary.lower())

    def test_malicious_query_blocked_by_guardrails(self):
        """Verify that malicious SQL injection attempts are intercepted and blocked."""
        malicious_prompt = "DROP TABLE orders; --"
        response = self.engine.ask(malicious_prompt)
        self.assertFalse(response.is_safe)
        self.assertIsNone(response.data)
        self.assertIn("Security Guardrail Rejection", response.error_message)

        # Verify table was NOT dropped
        check = self.db.execute_query("SELECT count(*) as cnt FROM orders;")
        self.assertGreater(check[0]["cnt"], 0)

    def test_empty_query_handling(self):
        """Verify empty question handling."""
        response = self.engine.ask("")
        self.assertFalse(response.is_safe)
        self.assertEqual(response.error_message, "Question cannot be empty.")


if __name__ == "__main__":
    unittest.main()
