from typing import List, Protocol
from uuid import UUID

from src.application.advertisers.dtos import GetAdvertiserByIdSchema, MLScoreSchema
from src.core.uow import AbstractUow
from src.domain.advertisers.entities import AdvertiserEntity, MLScoreEntity


class AdvertisersRepositoryProtocol(Protocol):
    async def get_by_id(self, id: UUID) -> AdvertiserEntity: ...

    async def bulk_upsert(
        self, entities: List[AdvertiserEntity]
    ) -> List[AdvertiserEntity]: ...


class MLScoreRepositoryProtocol(Protocol):
    async def upsert_ml_score(self, entity: MLScoreEntity) -> None: ...

    async def get_ml_score(
        self, client_id: UUID, advertiser_id: UUID
    ) -> int | None: ...


class GetAdvertiserByIdUseCaseProtocol(Protocol):
    async def execute(self, advertiser_id: UUID) -> GetAdvertiserByIdSchema: ...
    def get_uow(self) -> AbstractUow: ...


class UpsertAdvertisersUseCaseProtocol(Protocol):
    async def execute(
        self, data: List[GetAdvertiserByIdSchema]
    ) -> List[GetAdvertiserByIdSchema]: ...
    def get_uow(self) -> AbstractUow: ...


class UpsertMLScoreUseCaseProtocol(Protocol):
    async def execute(self, data: MLScoreSchema) -> None: ...
