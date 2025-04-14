import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import AsyncAdaptedQueuePool
from src.core.settings import settings


class Base(DeclarativeBase):
    pass


click_lock = asyncio.Lock()
impression_lock = asyncio.Lock()

async_engine = create_async_engine(
    settings.database_url,
    echo=settings.database_debug,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=90,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_use_lifo=True,
)

async_session_maker = async_sessionmaker(
    async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)

Session = AsyncSession


async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
