"""
SQLAlchemy Declarative Base and Model Meta-Configuration.

Provides the foundational DeclarativeBase subclass for all ORM entities in the system.
Includes fallback support for pre-installation development environments.
"""

try:
    from sqlalchemy.orm import DeclarativeBase

    class Base(DeclarativeBase):
        """Root declarative base class for all SQLAlchemy ORM models."""
        pass

except ImportError:
    class Base:  # type: ignore[no-redef]
        """Fallback declarative base when SQLAlchemy is not yet installed."""
        __name__: str = "Base"
