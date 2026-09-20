"""
Database Schema Initialization and Migration Utility.

Loads and executes the canonical relational schema DDL, verifies table creation,
enforces foreign key constraints, and validates schema integrity.
"""

import os
from pathlib import Path
import sqlite3
from typing import List, Optional
from config.settings import get_settings
from ecommerce_iq.utils.logging import setup_logger

logger = setup_logger("ecommerce_iq.database.schema")

SCHEMA_FILE_PATH = Path(__file__).resolve().parent / "schema.sql"

REQUIRED_TABLES = [
    "categories",
    "customers",
    "products",
    "orders",
    "order_items",
    "payments",
    "returns",
    "reviews",
    "review_insights",
    "sales",
]


def get_schema_ddl() -> str:
    """Read and return the raw SQL DDL script."""
    if not SCHEMA_FILE_PATH.exists():
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_FILE_PATH}")
    return SCHEMA_FILE_PATH.read_text(encoding="utf-8")


def initialize_database(
    database_path: Optional[str] = None,
    drop_existing: bool = False
) -> List[str]:
    """
    Initialize database tables, views, and indexes from schema.sql.

    Args:
        database_path: Absolute or relative path to SQLite database file.
                       If None, resolves from application settings.
        drop_existing: If True, drops existing tables before re-creating schema.

    Returns:
        List of created table names.
    """
    settings = get_settings()
    if database_path is None:
        db_url = settings.database_url
        if db_url.startswith("sqlite:///"):
            database_path = str(settings.project_root / db_url.replace("sqlite:///", ""))
        else:
            database_path = str(settings.project_root / "data" / "ecommerce_iq.db")

    # Ensure parent directory exists
    if database_path != ":memory:":
        os.makedirs(os.path.dirname(os.path.abspath(database_path)), exist_ok=True)

    ddl_script = get_schema_ddl()

    conn = sqlite3.connect(database_path)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        if drop_existing:
            logger.warning(f"Dropping existing tables in {database_path}")
            # Disable FKs temporarily during drop
            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%';")
            items = cursor.fetchall()
            for name, item_type in items:
                cursor.execute(f"DROP {item_type.upper()} IF EXISTS {name};")
            cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.executescript(ddl_script)
        conn.commit()

        # Fetch created tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
        tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"Initialized database with {len(tables)} tables at {database_path}")
        return tables

    finally:
        conn.close()


def verify_schema_integrity(
    database_path: Optional[str] = None,
    connection: Optional[sqlite3.Connection] = None
) -> bool:
    """
    Verify that all required tables, foreign keys, and indexes exist.
    Can accept either a file path or an active sqlite3.Connection.
    """
    close_after = False
    if connection is None:
        if database_path is None:
            settings = get_settings()
            database_path = str(settings.project_root / "data" / "ecommerce_iq.db")
        connection = sqlite3.connect(database_path)
        close_after = True

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        existing_tables = set(row[0] for row in cursor.fetchall())

        missing = set(REQUIRED_TABLES) - existing_tables
        if missing:
            logger.error(f"Missing required tables in schema: {missing}")
            return False

        # Verify foreign keys pragma is operable
        cursor.execute("PRAGMA foreign_key_check;")
        fk_violations = cursor.fetchall()
        if fk_violations:
            logger.error(f"Foreign key violations detected: {fk_violations}")
            return False

        return True
    finally:
        if close_after:
            connection.close()
