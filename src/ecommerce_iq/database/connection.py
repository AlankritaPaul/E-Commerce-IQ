"""
Database Connection and Session Management Interface.

Provides unified database lifecycle management:
- Connection pooling and dialect configuration (SQLite, DuckDB, PostgreSQL)
- Thread-safe session scoping with automatic commit/rollback context management
- Safe query execution gateway
"""

from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional
from config.settings import get_settings


class DatabaseManager:
    """
    Manages database lifecycle, connection pools, and transactional sessions.
    Designed for zero-friction local SQLite/DuckDB setup and direct PostgreSQL deployment.
    """

    def __init__(self, database_url: Optional[str] = None) -> None:
        self.settings = get_settings()
        self.database_url = database_url or getattr(self.settings, "resolved_database_url", self.settings.database_url)
        self._engine: Optional[Any] = None
        self._session_factory: Optional[Any] = None

    @property
    def is_connected(self) -> bool:
        """Return True if the database engine has been initialized."""
        return self._engine is not None

    def initialize(self) -> None:
        """
        Initialize database engine, connection pool, and verify connectivity.
        Will create tables based on ORM metadata in Phase 2.
        """
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            connect_args = {}
            if self.database_url.startswith("sqlite"):
                connect_args["check_same_thread"] = False

            self._engine = create_engine(
                self.database_url,
                connect_args=connect_args,
                pool_pre_ping=True
            )
            self._session_factory = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False
            )
        except ImportError:
            raise RuntimeError(
                "SQLAlchemy is required for database operations. "
                "Install dependencies via `pip install -r requirements.txt`."
            )

    @contextmanager
    def session_scope(self) -> Generator[Any, None, None]:
        """
        Provide a transactional scope around a series of database operations.
        Automatically commits on success and rolls back on exception.
        """
        if not self._session_factory:
            self.initialize()

        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @property
    def sqlite_path(self) -> str:
        """Resolve the SQLite database file path from settings."""
        if self.database_url.startswith("sqlite:///"):
            clean = self.database_url.replace("sqlite:///", "")
            return str(self.settings.project_root / clean)
        return self.database_url

    def get_raw_connection(self) -> Any:
        """
        Return an active native SQLite connection with Row factory enabled.
        Enables lightning-fast queries without ORM overhead.
        """
        import sqlite3
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def get_session(self) -> Any:
        """Return a fresh database session instance."""
        if not self._session_factory:
            self.initialize()
        return self._session_factory()

    def execute_query(self, query: str, params: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a read-only SQL query and return results as a list of dictionaries.
        Uses native SQLite connection for maximum speed and zero dependencies.
        """
        conn = self.get_raw_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def execute_query_df(self, query: str, params: Optional[dict] = None) -> Any:
        """
        Execute a read-only SQL query and return results as a Pandas DataFrame.
        """
        try:
            import pandas as pd
            if not self._engine:
                self.initialize()
            return pd.read_sql_query(query, con=self._engine, params=params)
        except ImportError:
            # Fallback to constructing DataFrame from execute_query if pandas is available
            try:
                import pandas as pd
                records = self.execute_query(query, params)
                return pd.DataFrame(records)
            except ImportError:
                raise RuntimeError("Pandas is required to return DataFrame format.")

    def close(self) -> None:
        """Dispose connection pools and release all system resources."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None
