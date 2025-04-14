from typing import Protocol

from src.application.time.dtos import GetCurrentDateResponse, TimeAdvancePostResponse


class TimeRepositoryProtocol(Protocol):
    async def advance_day(self, current_date: int | None) -> int: ...

    async def get_current_date(self) -> int: ...


class TimeUseCaseProtocol(Protocol):
    async def execute(self, current_date: int | None) -> TimeAdvancePostResponse: ...


class GetCurrentDateUseCaseProtocol(Protocol):
    async def execute(self) -> GetCurrentDateResponse: ...
