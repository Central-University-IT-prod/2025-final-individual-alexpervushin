import asyncio
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from src.adapters.telegram.handlers.advertisers.router import (
    router as advertisers_router,
)
from src.adapters.telegram.handlers.campaigns.router import (
    router as campaigns_router,
)
from src.adapters.telegram.handlers.main import router as main_router
from src.core.db import init_db
from src.core.redis import init_redis
from src.core.settings import settings
from src.infrastructure.advertisers.orm import AdvertiserModel as AdvertiserModel
from src.infrastructure.campaigns.orm import CampaignModel as CampaignModel
from src.infrastructure.clients.orm import ClientModel as ClientModel
from src.infrastructure.moderation.orm import ForbiddenWordsModel as ForbiddenWordsModel
from src.infrastructure.statistics.orm import UniqueEventModel as UniqueEventModel


@asynccontextmanager
async def lifespan():
    await init_db()
    global redis_client
    redis_client = await init_redis()
    try:
        yield
    finally:
        if redis_client:
            await redis_client.close()
            redis_client = None


async def main():
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    dp.include_router(main_router)
    dp.include_router(advertisers_router)
    dp.include_router(campaigns_router)

    async with lifespan():
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
