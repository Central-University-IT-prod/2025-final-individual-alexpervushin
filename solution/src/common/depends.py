from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import async_session_maker
from src.core.uow import AbstractUow, SQLAlchemyUow


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


def get_uow(
    session: AsyncSession = Depends(get_session),
) -> AbstractUow:
    return SQLAlchemyUow(session)
