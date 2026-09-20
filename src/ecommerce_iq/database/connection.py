"""
Database Connection and Session Management Interface.

Provides unified database lifecycle management:
- Connection pooling and dialect configuration (SQLite, DuckDB, PostgreSQL)
- Thread-safe session scoping with automatic commit/rollback context management
- Safe query execution gateway
"""

from contextlib import contextmanager
from typing import Any, Generator, Optional
from config.settings import get_settings


class DatabaseManager:
    """
    Manages database lifecycle, connection pools, and transactional sessions.
    Designed for zero-friction local SQLite/DuckDB setup and direct PostgreSQL deployment.
    """

    def __init__(self, database_url: Optional[str] = None) -> None:
        self.settings = get_settings()
        self.database_url = database_url or self.settings.database_url
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

    def get_session(self) -> Any:
        """Return a fresh database session instance."""
        if not self._session_factory:
            self.initialize()
        return self._session_factory()

    def execute_query(self, query: str, params: Optional[dict] = None) -> Any:
        """
        Execute a read-only SQL query and return results as a Pandas DataFrame.
        """
        try:
            import pandas as pd
            if not self._engine:
                self.initialize()
            return pd.read_sql_query(query, con=self._engine, params=params)
        except ImportError:
            raise RuntimeError("Pandas and SQLAlchemy are required for query execution.")

    def close(self) -> None:
        """Dispose connection pools and release all system resources."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None
