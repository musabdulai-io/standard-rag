# backend/app/core/database.py
"""
Database connection management using async SQLAlchemy.
Compatible with Cloud Run / Cloud SQL.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import AsyncAdaptedQueuePool

from app.core.config import settings
from app.core.observability import logs


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def get_database_url() -> str:
    """Get database URL with asyncpg driver."""
    base_url: str = settings.DATABASE_URL
    if base_url.startswith("postgresql://"):
        return base_url.replace("postgresql://", "postgresql+asyncpg://")
    elif base_url.startswith("postgresql+asyncpg://"):
        return base_url
    else:
        raise ValueError(f"Unsupported database URL format: {base_url}")


def create_db_engine() -> AsyncEngine:
    """Create async engine with environment-based configuration."""
    engine_args = {
        "poolclass": AsyncAdaptedQueuePool,
        "pool_size": 20 if settings.ENVIRONMENT == "production" else 5,
        "max_overflow": 10 if settings.ENVIRONMENT == "production" else 2,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
        "echo": settings.DEBUG,
    }

    if settings.ENVIRONMENT == "development":
        engine_args.update({
            "pool_size": 5,
            "max_overflow": 0,
            "pool_timeout": 10,
        })

    return create_async_engine(get_database_url(), **engine_args)


engine = create_db_engine()

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize database tables."""
    logs.info("Initializing database schema", "database")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logs.error("Database session error", "database", exception=e)
            raise


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
    logs.info("Database connections closed", "database")
