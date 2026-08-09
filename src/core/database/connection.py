from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from core.config import getSettings


class Base(DeclarativeBase):
    """Base declarative class for the relational models."""


settings = getSettings()
engine = create_engine(
    settings.databaseUrl,
    future=True,
    echo=False,
    connect_args={"check_same_thread": False} if settings.databaseUrl.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def getDbSession() -> Generator[Session, None, None]:
    """Yield a database session with guaranteed cleanup."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
