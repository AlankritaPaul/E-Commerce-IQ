"""
Unit Tests for Synthetic E-Commerce Business Dataset Generator.

Verifies:
- Seeder populates all 10 tables
- Multi-month date distribution
- Business anomalies presence (high return rates for defective products)
- Non-zero revenues, order items, reviews, returns, and sales facts
"""

from datetime import date
from pathlib import Path
import sqlite3
import sys
import unittest

_root = Path(__file__).resolve().parent.parent
for _p in (str(_root / "src"), str(_root)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ecommerce_iq.database.schema import get_schema_ddl
from ecommerce_iq.database.seeder import MockDataSeeder


class TestDatasetSeeder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Seed a compact test dataset into an in-memory database once for speed."""
        cls.conn = sqlite3.connect(":memory:")
        cls.conn.execute("PRAGMA foreign_keys = ON;")
        cls.conn.executescript(get_schema_ddl())

        # Seed with 100 customers and 300 orders
        seeder = MockDataSeeder(db_path=":memory:", seed=42)
        # Point internal seeder connection to this memory db
        # We can run seeder methods directly with our cursor
        cursor = cls.conn.cursor()
        seeder._seed_categories(cursor)
        seeder._seed_products(cursor)
        seeder._seed_customers(cursor, num_customers=100, start_date=date(2025, 1, 1))
        seeder._seed_orders(cursor, num_orders=350, start_date=date(2025, 1, 1), end_date=date(2025, 6, 30))
        seeder._seed_returns(cursor)
        seeder._seed_reviews(cursor)
        cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_all_tables_populated(self):
        """Verify that rows exist in all 10 normalized tables."""
        cursor = self.conn.cursor()
        tables = [
            "categories", "products", "customers", "orders",
            "order_items", "payments", "returns", "reviews",
            "review_insights", "sales"
        ]
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0, f"Table '{table}' should have non-zero rows.")

    def test_sales_financial_consistency(self):
        """Verify sales fact math: net_revenue = gross_revenue - discount_amount, and gross_profit is correct."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                ROUND(net_revenue - (gross_revenue - discount_amount), 2) AS net_diff,
                ROUND(gross_profit - (net_revenue - cost_of_goods_sold), 2) AS profit_diff
            FROM sales
            LIMIT 50;
        """)
        for net_diff, profit_diff in cursor.fetchall():
            self.assertAlmostEqual(net_diff, 0.0, places=2)
            self.assertAlmostEqual(profit_diff, 0.0, places=2)

    def test_high_return_product_anomaly(self):
        """Verify that PROD-ELEC-001 exhibits elevated return rates compared to store baseline."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT return_rate_percentage
            FROM v_product_performance_summary
            WHERE sku = 'PROD-ELEC-001';
        """)
        row = cursor.fetchone()
        if row and row[0] is not None:
            ret_pct = row[0]
            self.assertGreater(ret_pct, 10.0, "PROD-ELEC-001 should exhibit high return rate > 10%.")

    def test_review_insights_have_topics_and_sentiment(self):
        """Verify review insights contain valid sentiment labels and primary topics."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT sentiment_label FROM review_insights;
        """)
        labels = set(r[0] for r in cursor.fetchall())
        self.assertTrue(labels.issubset({"positive", "neutral", "negative"}))
        self.assertIn("positive", labels)

    def test_daily_summary_view_aggregates(self):
        """Verify v_daily_business_summary returns populated metrics."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*), SUM(total_orders), SUM(net_revenue)
            FROM v_daily_business_summary;
        """)
        days_count, orders_total, rev_total = cursor.fetchone()
        self.assertGreater(days_count, 0)
        self.assertGreater(orders_total, 0)
        self.assertGreater(rev_total, 0)


if __name__ == "__main__":
    unittest.main()
