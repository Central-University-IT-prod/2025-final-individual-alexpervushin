from typing import List

from src.application.clients.dtos import (
    ClientSchema,
    ClientUpsertSchema,
)
from src.common.types import ClientId
from src.core.uow import AbstractUow
from src.domain.clients.exceptions import ClientNotFoundException, ClientRepositoryError
from src.domain.clients.interfaces import (
    ClientsRepositoryProtocol,
)
from src.infrastructure.clients.mappers import ClientsMapper


class GetClientByIdUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: ClientsRepositoryProtocol,
        mapper: ClientsMapper,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._mapper = mapper

    async def execute(self, client_id: ClientId) -> ClientSchema:
        try:
            async with self._uow:
                client_entity = await self._repository.get_by_id(client_id)
                return self._mapper.from_entity_to_schema(client_entity)
        except ClientNotFoundException as e:
            raise ClientNotFoundException(str(e))
        except ClientRepositoryError as e:
            raise ClientRepositoryError(str(e))
        except Exception as e:
            raise ClientRepositoryError(f"Unexpected error: {str(e)}")


class UpsertClientUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: ClientsRepositoryProtocol,
        mapper: ClientsMapper,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._mapper = mapper

    async def execute(self, clients: List[ClientUpsertSchema]) -> List[ClientSchema]:
        try:
            async with self._uow:
                client_entities = [
                    self._mapper.from_schema_to_entity(client) for client in clients
                ]
                upserted_clients = await self._repository.bulk_upsert(client_entities)
                await self._uow.commit()

                return [
                    self._mapper.from_entity_to_schema(client)
                    for client in upserted_clients
                ]
        except ClientRepositoryError as e:
            raise ClientRepositoryError(str(e))
        except Exception as e:
            raise ClientRepositoryError(f"Unexpected error during upsert: {str(e)}")
