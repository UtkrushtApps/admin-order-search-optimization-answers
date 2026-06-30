import os
from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.metrics import increment_query_count

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@postgres:5432/orders_db",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
_query_counter_installed = False


def install_query_counter() -> None:
    global _query_counter_installed
    if _query_counter_installed:
        return

    @event.listens_for(Engine, "before_cursor_execute")
    def count_sql_statements(conn, cursor, statement, parameters, context, executemany):
        increment_query_count()

    _query_counter_installed = True


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
