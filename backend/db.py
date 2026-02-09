from sqlmodel import create_engine, Session
from sqlalchemy import Engine
from sqlmodel.main import SQLModel
import os
from typing import Generator


# Read DATABASE_URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")


# Create engine with connection pooling
engine: Engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,  # Validates connections before use (handles Neon serverless cold starts)
)


def init_db() -> None:
    """
    Initialize the database by creating all tables if they don't exist.
    This should be called on application startup.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency to get a database session.

    Yields a session that will be automatically closed when the request is completed.
    """
    with Session(engine) as session:
        yield session