"""Database connection management with lazy initialization."""
from functools import lru_cache
from sqlalchemy.orm import DeclarativeBase
from app.config import settings
from app.utils.logger import logger


class Base(DeclarativeBase):
    pass


@lru_cache()
def _get_engine():
    """Lazily create the async engine."""
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_size=10,
            max_overflow=20,
        )
        logger.info("Database engine created")
        return engine
    except Exception as e:
        logger.warning(f"Could not create async engine (mock mode): {e}")
        return None


@lru_cache()
def _get_session_factory():
    """Lazily create the session factory."""
    engine = _get_engine()
    if engine is None:
        return None
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def get_sync_engine():
    """Get a synchronous engine for Alembic/offline use."""
    try:
        from sqlalchemy import create_engine
        return create_engine(settings.DATABASE_URL_SYNC, echo=settings.DEBUG)
    except Exception as e:
        logger.warning(f"Could not create sync engine: {e}")
        return None


def get_session_factory():
    """Get the async session factory."""
    return _get_session_factory()


async def get_db():
    """Get database session dependency."""
    factory = _get_session_factory()
    if factory is None:
        raise RuntimeError("Database not available (mock mode should be used)")
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    import sqlalchemy.ext.asyncio  # noqa
    engine = _get_engine()
    if engine is None:
        logger.warning("Database engine not available, skipping init")
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def close_db():
    """Close database connections."""
    engine = _get_engine()
    if engine is not None:
        await engine.dispose()
        logger.info("Database engine disposed")
