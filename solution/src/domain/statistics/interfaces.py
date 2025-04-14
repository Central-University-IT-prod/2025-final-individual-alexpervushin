from typing import List, Optional, Protocol
from uuid import UUID

from src.application.statistics.dtos import (
    CampaignFeedbackResponse,
    ClientStatsResponse,
    DailyStatsResponse,
    StatsResponse,
)
from src.domain.statistics.entities import FeedbackEntity, StatisticsEntity


class StatisticsRepositoryProtocol(Protocol):
    async def get_campaign_stats(self, campaign_id: UUID) -> StatisticsEntity: ...

    async def get_advertiser_stats(self, advertiser_id: UUID) -> StatisticsEntity: ...

    async def get_campaign_daily_stats(
        self, campaign_id: UUID
    ) -> List[StatisticsEntity]: ...

    async def get_advertiser_daily_stats(
        self, advertiser_id: UUID
    ) -> List[StatisticsEntity]: ...

    async def register_impression(self, client_id: UUID, campaign_id: UUID): ...

    async def register_click(self, client_id: UUID, campaign_id: UUID): ...

    async def register_feedback(
        self, client_id: UUID, campaign_id: UUID, rating: int, comment: Optional[str]
    ) -> None: ...

    async def get_clients_stats(self) -> ClientStatsResponse: ...

    async def get_campaign_feedbacks(
        self, campaign_id: UUID
    ) -> List[FeedbackEntity]: ...


class GetCampaignStatsUseCaseProtocol(Protocol):
    async def execute(self, campaign_id: UUID) -> StatsResponse: ...


class GetAdvertiserCampaignsStatsUseCaseProtocol(Protocol):
    async def execute(self, advertiser_id: UUID) -> StatsResponse: ...


class GetCampaignDailyStatsUseCaseProtocol(Protocol):
    async def execute(self, campaign_id: UUID) -> List[DailyStatsResponse]: ...


class GetAdvertiserDailyStatsUseCaseProtocol(Protocol):
    async def execute(self, advertiser_id: UUID) -> List[DailyStatsResponse]: ...


class GetClientsStatsUseCaseProtocol(Protocol):
    async def execute(self) -> ClientStatsResponse: ...


class GetCampaignFeedbackStatsUseCaseProtocol(Protocol):
    async def execute(self, campaign_id: UUID) -> CampaignFeedbackResponse: ...
