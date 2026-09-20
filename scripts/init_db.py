"""
CLI Script to Initialize E-Commerce IQ Database Schema.

Usage:
    python scripts/init_db.py [--reset] [--path data/ecommerce_iq.db]
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(root_dir / "src") not in sys.path:
    sys.path.insert(0, str(root_dir / "src"))

from ecommerce_iq.database.schema import initialize_database, verify_schema_integrity


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize E-Commerce IQ SQL Database Schema")
    parser.add_argument("--reset", action="store_true", help="Drop existing tables before creating schema")
    parser.add_argument("--path", type=str, default=None, help="Custom database file path")
    args = parser.parse_args()

    print(f"Initializing E-Commerce IQ schema (reset={args.reset})...")
    tables = initialize_database(database_path=args.path, drop_existing=args.reset)
    print(f"Schema initialized successfully! Created {len(tables)} tables:")
    for t in tables:
        print(f"  - {t}")

    db_path = args.path or str(root_dir / "data" / "ecommerce_iq.db")
    if verify_schema_integrity(db_path):
        print("Schema integrity verified: All required tables, constraints, and indexes are valid.")
    else:
        print("Warning: Schema verification reported issues.")


if __name__ == "__main__":
    main()
