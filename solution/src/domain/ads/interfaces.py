from typing import Optional, Protocol
from uuid import UUID

from src.application.ads.dtos import AdsGetResponse


class GetAdForClientUseCaseProtocol(Protocol):
    async def execute(self, client_id: UUID) -> AdsGetResponse: ...


class RecordAdClickUseCaseProtocol(Protocol):
    async def execute(self, ad_id: UUID, client_id: UUID) -> None: ...


class SubmitAdFeedbackUseCaseProtocol(Protocol):
    async def execute(
        self, ad_id: UUID, client_id: UUID, rating: int, comment: Optional[str]
    ) -> None: ...
