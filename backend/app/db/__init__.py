"""Database wiring (engine, session, base)."""
from app.db.base import Base, engine, SessionLocal, get_session  # noqa: F401
