import redis.asyncio as redis
from src.domain.time.exceptions import TimeRepositoryError
from src.domain.time.interfaces import TimeRepositoryProtocol

CURRENT_DATE_KEY = "current_date"


class TimeRepository(TimeRepositoryProtocol):
    def __init__(self, redis: redis.Redis) -> None:
        self._redis = redis

    async def _ensure_current_date(self) -> int:
        try:
            current_date = await self._redis.get(CURRENT_DATE_KEY)
        except Exception as e:
            raise TimeRepositoryError(f"Не удалось получить текущую дату: {str(e)}")
        if current_date is None:
            try:
                default_day = 0
                await self._redis.set(CURRENT_DATE_KEY, default_day)
                return default_day
            except Exception as e:
                raise TimeRepositoryError(
                    f"Не удалось установить текущую дату: {str(e)}"
                )
        try:
            return int(current_date)
        except Exception as e:
            raise TimeRepositoryError(
                f"Не удалось преобразовать текущую дату в int: {str(e)}"
            )

    async def advance_day(self, current_date: int | None) -> int:
        try:
            if current_date is None:
                current_date = await self._ensure_current_date()
            await self._redis.set(CURRENT_DATE_KEY, current_date)
            return current_date
        except Exception as e:
            raise TimeRepositoryError(f"Не удалось установитьдень: {str(e)}")

    async def get_current_date(self) -> int:
        try:
            return await self._ensure_current_date()
        except Exception as e:
            raise TimeRepositoryError(f"Не удалось получить текущую дату: {str(e)}")
