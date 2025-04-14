from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable, Optional, TypeVar

from aiogram import F
from aiogram.types import Message, User
from src.core.db import async_session_maker
from src.infrastructure.advertisers.mappers import AdvertisersMapper
from src.infrastructure.advertisers.repositories import AdvertisersRepository

T = TypeVar("T")


def text_equals(text: str) -> Any:
    return F.text == text


async def check_user(message: Message) -> Optional[User]:
    return message.from_user if message.from_user else None


@asynccontextmanager
async def get_session_with_advertiser(telegram_id: int):
    async with async_session_maker() as session:
        mapper = AdvertisersMapper()
        repository = AdvertisersRepository(session, mapper)
        advertiser = await repository.get_advertiser_by_telegram_id(telegram_id)
        yield session, mapper, repository, advertiser


async def handle_db_operation(
    operation: Callable[..., Awaitable[T]],
    error_message: str,
    message: Message,
    **kwargs: Any,
) -> Optional[T]:
    try:
        return await operation(**kwargs)
    except Exception as e:
        if error_message:
            await message.answer(f"❌ {error_message}: {str(e)}")
        return None
