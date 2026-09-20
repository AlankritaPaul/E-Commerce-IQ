"""
Unit and Integration Tests for E-Commerce IQ Relational Database Schema.

Verifies:
- Creation of all 10 normalized tables and views
- Foreign key integrity enforcement
- CHECK constraints (e.g. price >= 0, rating between 1 and 5, allowed enums)
- Cascading delete behavior
- Index creation on foreign keys, dates, and status fields
"""

from datetime import date, datetime
from pathlib import Path
import sqlite3
import sys
import unittest

_root = Path(__file__).resolve().parent.parent
for _p in (str(_root / "src"), str(_root)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ecommerce_iq.database.schema import (
    REQUIRED_TABLES,
    get_schema_ddl,
    verify_schema_integrity,
)


class TestDatabaseSchema(unittest.TestCase):
    def setUp(self):
        """Create a fresh in-memory SQLite database for each test with foreign keys enabled."""
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.ddl = get_schema_ddl()
        self.conn.executescript(self.ddl)

    def tearDown(self):
        """Close connection."""
        self.conn.close()

    def test_all_required_tables_exist(self):
        """Verify that all 10 required normalized tables are created."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        created_tables = set(row[0] for row in cursor.fetchall())

        for table in REQUIRED_TABLES:
            self.assertIn(table, created_tables, f"Expected table '{table}' was not created.")

        self.assertTrue(verify_schema_integrity(connection=self.conn))

    def test_analytical_views_exist(self):
        """Verify analytical views are created."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view';")
        views = set(row[0] for row in cursor.fetchall())
        self.assertIn("v_product_performance_summary", views)
        self.assertIn("v_daily_business_summary", views)

    def test_foreign_key_enforcement(self):
        """Verify that foreign key constraints are strictly enforced."""
        cursor = self.conn.cursor()

        # Attempt to insert an order referencing a non-existent customer (ID 999)
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO orders (customer_id, order_date, status, subtotal, total_amount)
                VALUES (999, '2025-01-15 10:00:00', 'completed', 100.0, 100.0);
            """)

    def test_price_check_constraints(self):
        """Verify products cannot have negative cost or retail prices."""
        cursor = self.conn.cursor()

        # Insert valid category first
        cursor.execute("INSERT INTO categories (name, slug) VALUES ('Electronics', 'electronics');")
        cat_id = cursor.lastrowid

        # Negative price should fail
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO products (category_id, sku, title, cost_price, retail_price, stock_quantity)
                VALUES (?, 'SKU-NEG', 'Test Product', -10.00, 50.00, 10);
            """, (cat_id,))

        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO products (category_id, sku, title, cost_price, retail_price, stock_quantity)
                VALUES (?, 'SKU-NEG-2', 'Test Product', 10.00, -50.00, 10);
            """, (cat_id,))

    def test_review_rating_check_constraint(self):
        """Verify customer reviews reject ratings outside 1-5."""
        cursor = self.conn.cursor()

        # Setup valid parent records
        cursor.execute("INSERT INTO categories (name, slug) VALUES ('Books', 'books');")
        cat_id = cursor.lastrowid
        cursor.execute("INSERT INTO products (category_id, sku, title, cost_price, retail_price) VALUES (?, 'BK-1', 'Python Book', 5.0, 20.0);", (cat_id,))
        prod_id = cursor.lastrowid
        cursor.execute("INSERT INTO customers (first_name, last_name, email, city) VALUES ('John', 'Doe', 'john@test.com', 'New York');")
        cust_id = cursor.lastrowid

        # Rating 0 should fail
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO reviews (product_id, customer_id, rating, comment)
                VALUES (?, ?, 0, 'Terrible');
            """, (prod_id, cust_id))

        # Rating 6 should fail
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO reviews (product_id, customer_id, rating, comment)
                VALUES (?, ?, 6, 'Too good!');
            """, (prod_id, cust_id))

        # Rating 5 should succeed
        cursor.execute("""
            INSERT INTO reviews (product_id, customer_id, rating, comment)
            VALUES (?, ?, 5, 'Perfect!');
        """, (prod_id, cust_id))
        self.assertEqual(cursor.rowcount, 1)

    def test_order_cascade_delete(self):
        """Verify that deleting an order cascades and removes related line items and payments."""
        cursor = self.conn.cursor()

        # Setup parents
        cursor.execute("INSERT INTO customers (first_name, last_name, email, city) VALUES ('Alice', 'Smith', 'alice@test.com', 'Chicago');")
        cust_id = cursor.lastrowid
        cursor.execute("INSERT INTO categories (name, slug) VALUES ('Apparel', 'apparel');")
        cat_id = cursor.lastrowid
        cursor.execute("INSERT INTO products (category_id, sku, title, cost_price, retail_price) VALUES (?, 'APP-1', 'T-Shirt', 8.0, 25.0);", (cat_id,))
        prod_id = cursor.lastrowid

        # Insert Order
        cursor.execute("""
            INSERT INTO orders (customer_id, order_date, status, subtotal, total_amount)
            VALUES (?, '2025-02-01 12:00:00', 'completed', 50.0, 50.0);
        """, (cust_id,))
        order_id = cursor.lastrowid

        # Insert OrderItem
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, unit_cost, item_total)
            VALUES (?, ?, 2, 25.0, 8.0, 50.0);
        """, (order_id, prod_id))
        item_id = cursor.lastrowid

        # Insert Payment
        cursor.execute("""
            INSERT INTO payments (order_id, payment_method, transaction_reference, amount, status)
            VALUES (?, 'credit_card', 'TXN-998877', 50.0, 'completed');
        """, (order_id,))

        # Verify child records exist
        cursor.execute("SELECT COUNT(*) FROM order_items WHERE order_id = ?;", (order_id,))
        self.assertEqual(cursor.fetchone()[0], 1)
        cursor.execute("SELECT COUNT(*) FROM payments WHERE order_id = ?;", (order_id,))
        self.assertEqual(cursor.fetchone()[0], 1)

        # Delete Order
        cursor.execute("DELETE FROM orders WHERE order_id = ?;", (order_id,))

        # Verify children were cascaded and removed
        cursor.execute("SELECT COUNT(*) FROM order_items WHERE order_id = ?;", (order_id,))
        self.assertEqual(cursor.fetchone()[0], 0)
        cursor.execute("SELECT COUNT(*) FROM payments WHERE order_id = ?;", (order_id,))
        self.assertEqual(cursor.fetchone()[0], 0)

    def test_indexes_exist(self):
        """Verify performance indexes are registered in sqlite_master."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = set(row[0] for row in cursor.fetchall())

        critical_indexes = [
            "idx_orders_customer_id",
            "idx_orders_order_date",
            "idx_order_items_product_id",
            "idx_payments_order_id",
            "idx_returns_product_reason",
            "idx_reviews_product_rating",
            "idx_sales_sale_date",
        ]
        for idx in critical_indexes:
            self.assertIn(idx, indexes, f"Index '{idx}' was not found in database schema.")


if __name__ == "__main__":
    unittest.main()
