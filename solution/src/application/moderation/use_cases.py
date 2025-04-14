from typing import List

from src.application.moderation.dtos import ModerationResponse
from src.core.uow import AbstractUow
from src.domain.moderation.interfaces import (
    ForbiddenWordsRepositoryProtocol,
    ModerationServiceProtocol,
)
from src.infrastructure.moderation.mappers import ModerationMapper


class GetForbiddenWordsUseCase:
    def __init__(self, uow: AbstractUow, repository: ForbiddenWordsRepositoryProtocol):
        self.uow = uow
        self.repository = repository

    async def execute(self) -> List[str]:
        async with self.uow:
            words = await self.repository.get_all()
            return words


class UpdateForbiddenWordsUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: ForbiddenWordsRepositoryProtocol,
    ):
        self.uow = uow
        self.repository = repository

    async def execute(self, data: List[str]) -> None:
        async with self.uow:
            await self.repository.update(data)
            await self.uow.commit()


class CheckForbiddenWordsUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: ForbiddenWordsRepositoryProtocol,
        moderation_service: ModerationServiceProtocol,
        mapper: ModerationMapper,
    ):
        self.uow = uow
        self.repository = repository
        self.moderation_service = moderation_service
        self.mapper = mapper

    async def execute(
        self,
        text: str,
        check_database: bool = True,
        check_ai: bool = True,
    ) -> ModerationResponse:
        async with self.uow:
            moderation_result = await self.moderation_service.check_forbidden_words(
                text,
                check_database=check_database,
                check_ai=check_ai,
            )
            moderation_entity = self.mapper.from_moderation_result_to_entity(
                moderation_result
            )
            return self.mapper.from_entity_to_response(moderation_entity)
