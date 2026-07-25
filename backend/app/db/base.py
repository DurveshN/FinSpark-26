"""SQLAlchemy engine, session factory, and declarative base.

Single DB wiring point. Uses settings.database_url (SQLite locally, Postgres in
prod). Other modules import Base for models and get_session for request scope.
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=_connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_session():
    """FastAPI dependency: yield a DB session, always closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
