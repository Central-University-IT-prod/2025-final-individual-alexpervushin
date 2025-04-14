from typing import List, Protocol
from uuid import UUID

from src.application.clients.dtos import ClientSchema, ClientUpsertSchema
from src.common.types import ClientId
from src.domain.clients.entities import ClientEntity


class ClientsRepositoryProtocol(Protocol):
    async def get_by_id(self, id: UUID) -> ClientEntity: ...

    async def bulk_upsert(self, entities: List[ClientEntity]) -> List[ClientEntity]: ...


class GetClientByIdUseCaseProtocol(Protocol):
    async def execute(self, client_id: ClientId) -> ClientSchema: ...


class UpsertClientUseCaseProtocol(Protocol):
    async def execute(
        self, clients: List[ClientUpsertSchema]
    ) -> List[ClientSchema]: ...
