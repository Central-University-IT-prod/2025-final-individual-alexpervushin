from typing import List, Optional, Protocol
from uuid import UUID

from fastapi import UploadFile
from src.application.campaigns.dtos import (
    CampaignCreateRequest,
    CampaignResponse,
    CampaignUpdateRequest,
    ImageUploadResponse,
)
from src.domain.campaigns.entities import CampaignEntity, CampaignUpdateEntity


class CampaignsRepositoryProtocol(Protocol):
    async def create(self, campaign: CampaignEntity) -> CampaignEntity: ...

    async def get_all(
        self, advertiser_id: UUID, size: Optional[int], page: Optional[int]
    ) -> List[CampaignEntity]: ...

    async def get_by_id(self, campaign_id: UUID) -> CampaignEntity: ...

    async def update(self, campaign: CampaignUpdateEntity) -> CampaignEntity: ...

    async def update_image_url(
        self, campaign_id: UUID, image_url: Optional[str]
    ) -> CampaignEntity: ...

    async def delete(self, advertiser_id: UUID, campaign_id: UUID) -> None: ...

    async def get_targeted_campaigns(self, client_id: UUID) -> List[CampaignEntity]: ...


class CreateCampaignUseCaseProtocol(Protocol):
    async def execute(
        self, advertiser_id: UUID, data: CampaignCreateRequest
    ) -> Optional[CampaignResponse]: ...


class GetCampaignsUseCaseProtocol(Protocol):
    async def execute(
        self, advertiser_id: UUID, size: Optional[int], page: Optional[int]
    ) -> List[CampaignResponse]: ...


class GetCampaignByIdUseCaseProtocol(Protocol):
    async def execute(
        self, advertiser_id: UUID, campaign_id: UUID
    ) -> CampaignResponse: ...


class UpdateCampaignUseCaseProtocol(Protocol):
    async def execute(
        self,
        advertiser_id: UUID,
        campaign_id: UUID,
        data: CampaignUpdateRequest,
    ) -> CampaignResponse: ...


class DeleteCampaignUseCaseProtocol(Protocol):
    async def execute(self, advertiser_id: UUID, campaign_id: UUID) -> None: ...


class UploadCampaignImageUseCaseProtocol(Protocol):
    async def execute(
        self, advertiser_id: UUID, campaign_id: UUID, image: UploadFile
    ) -> ImageUploadResponse: ...


class DeleteCampaignImageUseCaseProtocol(Protocol):
    async def execute(self, advertiser_id: UUID, campaign_id: UUID) -> None: ...


class GetCampaignsFromYandexUseCaseProtocol(Protocol):
    async def execute(
        self, advertiser_id: UUID, token: Optional[str] = None
    ) -> List[CampaignResponse]: ...


class CreateCampaignFromYandexUseCaseProtocol(Protocol):
    async def execute(
        self, advertiser_id: UUID, token: Optional[str] = None
    ) -> List[CampaignResponse]: ...


class YandexDirectServiceProtocol(Protocol):
    async def get_campaign_entities(
        self, token: Optional[str], advertiser_id: UUID
    ) -> List[CampaignEntity]: ...
