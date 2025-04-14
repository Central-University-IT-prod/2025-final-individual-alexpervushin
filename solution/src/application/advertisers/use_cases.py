from typing import List
from uuid import UUID

from src.application.advertisers.dtos import (
    GetAdvertiserByIdSchema,
    MLScoreSchema,
)
from src.core.uow import AbstractUow
from src.domain.advertisers.exceptions import (
    AdvertiserNotFoundException,
    AdvertiserRepositoryError,
    MLScoreRepositoryError,
)
from src.domain.advertisers.interfaces import (
    AdvertisersRepositoryProtocol,
    MLScoreRepositoryProtocol,
)
from src.domain.clients.exceptions import ClientNotFoundException
from src.infrastructure.advertisers.mappers import AdvertisersMapper, MLScoreMapper


class GetAdvertiserByIdUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: AdvertisersRepositoryProtocol,
        mapper: AdvertisersMapper,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._mapper = mapper

    def get_uow(self) -> AbstractUow:
        return self._uow

    async def execute(self, advertiser_id: UUID) -> GetAdvertiserByIdSchema:
        try:
            async with self._uow:
                advertiser_entity = await self._repository.get_by_id(advertiser_id)
                return self._mapper.from_entity_to_schema(advertiser_entity)
        except AdvertiserNotFoundException as e:
            raise AdvertiserNotFoundException(str(e))
        except AdvertiserRepositoryError as e:
            raise AdvertiserRepositoryError(str(e))
        except Exception as e:
            raise AdvertiserRepositoryError(f"Unexpected error: {str(e)}")


class UpsertAdvertisersUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: AdvertisersRepositoryProtocol,
        mapper: AdvertisersMapper,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._mapper = mapper

    def get_uow(self) -> AbstractUow:
        return self._uow

    async def execute(
        self, data: List[GetAdvertiserByIdSchema]
    ) -> List[GetAdvertiserByIdSchema]:
        try:
            async with self._uow:
                advertiser_entities = [
                    self._mapper.from_schema_to_entity(advertiser)
                    for advertiser in data
                ]
                upserted_advertisers = await self._repository.bulk_upsert(
                    advertiser_entities
                )
                await self._uow.commit()

                return [
                    self._mapper.from_entity_to_schema(advertiser)
                    for advertiser in upserted_advertisers
                ]
        except AdvertiserRepositoryError as e:
            raise AdvertiserRepositoryError(str(e))
        except Exception as e:
            raise AdvertiserRepositoryError(f"Unexpected error during upsert: {str(e)}")


class UpsertMLScoreUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: MLScoreRepositoryProtocol,
        mapper: MLScoreMapper,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._mapper = mapper

    async def execute(self, data: MLScoreSchema) -> None:
        try:
            async with self._uow:
                ml_score_entity = self._mapper.from_schema_to_entity(data)
                await self._repository.upsert_ml_score(ml_score_entity)
                await self._uow.commit()
        except AdvertiserNotFoundException as e:
            raise AdvertiserNotFoundException(str(e))
        except ClientNotFoundException as e:
            raise ClientNotFoundException(str(e))
        except MLScoreRepositoryError as e:
            raise MLScoreRepositoryError(str(e))
        except Exception as e:
            raise MLScoreRepositoryError(
                f"Unexpected error upserting ML score: {str(e)}"
            )
