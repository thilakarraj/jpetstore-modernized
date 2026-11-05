"""Shared SQLAlchemy declarative base (entities added in Phase 2)."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """ORM base class for all entities."""
