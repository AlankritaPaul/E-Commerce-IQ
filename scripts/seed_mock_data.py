"""
CLI Script to Seed E-Commerce IQ Database with Realistic Business Data.

Usage:
    python scripts/seed_mock_data.py [--reset] [--orders 4000] [--customers 850] [--path data/ecommerce_iq.db]
"""

import argparse
from pathlib import Path
import sqlite3
import sys

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(root_dir / "src") not in sys.path:
    sys.path.insert(0, str(root_dir / "src"))

from ecommerce_iq.database.schema import initialize_database
from ecommerce_iq.database.seeder import MockDataSeeder
from ecommerce_iq.utils.formatting import format_currency, format_percentage


def print_executive_data_summary(db_path: str) -> None:
    """Query the analytical database and output executive validation statistics."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("         E-COMMERCE IQ: EXECUTIVE DATASET VALIDATION REPORT        ")
    print("=" * 70)

    # 1. Overall Revenue and Orders
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT order_id) AS total_orders,
            SUM(total_amount) AS net_revenue,
            AVG(total_amount) AS aov
        FROM orders
        WHERE status = 'completed';
    """)
    orders_count, net_rev, aov = cursor.fetchone()

    # Total refunds
    cursor.execute("SELECT COALESCE(SUM(refund_amount), 0) FROM returns;")
    total_refunds = cursor.fetchone()[0]

    # Return rate
    cursor.execute("""
        SELECT 
            SUM(oi.quantity) AS total_sold,
            COALESCE(SUM(r.quantity_returned), 0) AS total_returned
        FROM order_items oi
        LEFT JOIN returns r ON oi.order_item_id = r.order_item_id;
    """)
    total_sold, total_ret = cursor.fetchone()
    overall_ret_pct = (total_ret * 100.0 / total_sold) if total_sold else 0.0

    print(f"\n[1] Overall Store Performance (14-Month Period):")
    print(f"  - Completed Orders:       {orders_count:,}")
    print(f"  - Total Net Revenue:      {format_currency(net_rev or 0)}")
    print(f"  - Average Order Value:    {format_currency(aov or 0)}")
    print(f"  - Total Units Sold:       {total_sold:,}")
    print(f"  - Total Units Returned:   {total_ret:,} ({format_percentage(overall_ret_pct)})")
    print(f"  - Total Financial Refunds:{format_currency(total_refunds)}")

    # 2. Monthly Revenue Trajectory (Demonstrating Growth & August Dip)
    print("\n[2] Monthly Net Revenue Trend (Demonstrating Seasonality & Dips):")
    cursor.execute("""
        SELECT 
            strftime('%Y-%m', order_date) AS order_month,
            COUNT(DISTINCT order_id) AS orders,
            SUM(total_amount) AS revenue
        FROM orders
        WHERE status = 'completed'
        GROUP BY 1
        ORDER BY 1;
    """)
    monthly_rows = cursor.fetchall()
    for mo, mo_orders, mo_rev in monthly_rows:
        bar = "#" * int((mo_rev or 0) / 4000)
        note = ""
        if mo == "2025-08":
            note = " <-- DELIBERATE DECLINE ANOMALY"
        elif mo in ("2025-11", "2025-12"):
            note = " <-- Q4 HOLIDAY SURGE"
        print(f"  {mo}: {format_currency(mo_rev or 0):>12} ({mo_orders:>3} orders) | {bar}{note}")

    # 3. Top Best-Selling Products (Cash Cows)
    print("\n[3] Top 3 Best-Selling Products:")
    cursor.execute("""
        SELECT 
            p.sku,
            p.title,
            SUM(oi.quantity) AS units_sold,
            SUM(oi.item_total) AS revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN orders o ON oi.order_id = o.order_id AND o.status = 'completed'
        GROUP BY p.product_id
        ORDER BY revenue DESC
        LIMIT 3;
    """)
    for sku, title, units, rev in cursor.fetchall():
        print(f"  * {sku} ({title}): {units} units sold, {format_currency(rev)}")

    # 4. Highest Return Rate Products (Defective Batch Anomaly Demonstration)
    print("\n[4] Products with Highest Return Rates:")
    cursor.execute("""
        SELECT 
            sku,
            title,
            total_units_sold,
            total_units_returned,
            return_rate_percentage,
            average_rating
        FROM v_product_performance_summary
        WHERE total_units_sold >= 15
        ORDER BY return_rate_percentage DESC
        LIMIT 3;
    """)
    for sku, title, sold, ret, ret_pct, rating in cursor.fetchall():
        print(f"  ! {sku} ({title}):")
        print(f"      Sold: {sold} | Returned: {ret} ({ret_pct:.1f}%) | Avg Rating: {rating:.1f}/5.0")

    # 5. Customer Sentiment & NLP Insights
    print("\n[5] Customer Review Sentiment & Feedback Topics:")
    cursor.execute("""
        SELECT 
            ri.sentiment_label,
            COUNT(*) AS count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM review_insights), 1) AS pct
        FROM review_insights ri
        GROUP BY ri.sentiment_label;
    """)
    for label, count, pct in cursor.fetchall():
        print(f"  - {label.capitalize():<10}: {count:>4} reviews ({pct}%)")

    print("\nTop Negative Review Complaints Extracted:")
    cursor.execute("""
        SELECT 
            ri.detected_issue,
            COUNT(*) AS occurrences
        FROM review_insights ri
        WHERE ri.sentiment_label = 'negative' AND ri.detected_issue != 'None'
        GROUP BY ri.detected_issue
        ORDER BY occurrences DESC
        LIMIT 4;
    """)
    for issue, occurrences in cursor.fetchall():
        print(f"  - \"{issue}\" ({occurrences} times)")

    print("=" * 70 + "\n")
    conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed realistic e-commerce synthetic dataset")
    parser.add_argument("--reset", action="store_true", default=True, help="Re-initialize schema before seeding")
    parser.add_argument("--orders", type=int, default=4200, help="Number of orders to generate")
    parser.add_argument("--customers", type=int, default=850, help="Number of customers to generate")
    parser.add_argument("--path", type=str, default=None, help="SQLite database path")
    args = parser.parse_args()

    target_db = args.path or str(root_dir / "data" / "ecommerce_iq.db")

    if args.reset:
        print(f"Initializing database schema at {target_db}...")
        initialize_database(database_path=target_db, drop_existing=True)

    print(f"Generating realistic e-commerce dataset (Customers={args.customers}, Target Orders={args.orders})...")
    seeder = MockDataSeeder(db_path=target_db)
    counts = seeder.seed_all(num_customers=args.customers, num_orders=args.orders)

    print("Populated table counts:")
    for table, count in counts.items():
        print(f"  - {table:<20}: {count:>6,} rows")

    print_executive_data_summary(target_db)


if __name__ == "__main__":
    main()
