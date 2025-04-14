from typing import Protocol
from uuid import UUID

from fastapi.responses import FileResponse
from src.application.ai.dtos import (
    AdvertisementGenerationResponse,
    GeneratedAdResponse,
    ModerationResponse,
)


class GenerateAdUseCaseProtocol(Protocol):
    async def execute(
        self, advertiser_id: UUID, ad_title: str
    ) -> AdvertisementGenerationResponse: ...


class AIServiceProtocol(Protocol):
    async def generate_ad(
        self, advertiser_name: str, ad_title: str
    ) -> GeneratedAdResponse: ...

    async def check_forbidden_words(self, text: str) -> ModerationResponse: ...

    async def generate_image(self, ad_title: str, ad_text: str) -> FileResponse: ...


class GenerateImageUseCaseProtocol(Protocol):
    async def execute(self, campaign_id: UUID) -> FileResponse: ...
