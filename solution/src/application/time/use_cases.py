import redis.asyncio as redis
from src.application.time.dtos import GetCurrentDateResponse, TimeAdvancePostResponse
from src.domain.time.exceptions import TimeRepositoryError
from src.domain.time.interfaces import (
    GetCurrentDateUseCaseProtocol,
    TimeRepositoryProtocol,
    TimeUseCaseProtocol,
)


class TimeUseCase(TimeUseCaseProtocol):
    def __init__(
        self,
        repository: TimeRepositoryProtocol,
        redis: redis.Redis,
    ) -> None:
        self._repository = repository
        self._redis = redis

    async def execute(self, current_date: int | None) -> TimeAdvancePostResponse:
        try:
            current_date = await self._repository.advance_day(current_date=current_date)
            return TimeAdvancePostResponse(current_date=current_date)
        except TimeRepositoryError as e:
            raise TimeRepositoryError(str(e))
        except Exception as e:
            raise TimeRepositoryError(f"Unexpected error while advancing day: {str(e)}")


class GetCurrentDateUseCase(GetCurrentDateUseCaseProtocol):
    def __init__(self, repository: TimeRepositoryProtocol) -> None:
        self._repository = repository

    async def execute(self) -> GetCurrentDateResponse:
        try:
            current_date = await self._repository.get_current_date()
            return GetCurrentDateResponse(current_date=current_date)
        except TimeRepositoryError as e:
            raise TimeRepositoryError(str(e))
        except Exception as e:
            raise TimeRepositoryError(
                f"Unexpected error while getting current date: {str(e)}"
            )
