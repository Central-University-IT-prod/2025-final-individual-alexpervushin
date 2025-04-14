from typing import List
from uuid import UUID

from src.application.statistics.dtos import (
    CampaignFeedbackResponse,
    ClientStatsResponse,
    DailyStatsResponse,
    StatsResponse,
)
from src.core.uow import AbstractUow
from src.domain.advertisers.exceptions import AdvertiserNotFoundException
from src.domain.advertisers.interfaces import AdvertisersRepositoryProtocol
from src.domain.campaigns.exceptions import CampaignNotFoundException
from src.domain.campaigns.interfaces import CampaignsRepositoryProtocol
from src.domain.statistics.exceptions import StatisticsRepositoryError
from src.domain.statistics.interfaces import (
    StatisticsRepositoryProtocol,
)
from src.infrastructure.statistics.mappers import StatisticsMapper


class GetCampaignStatsUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: StatisticsRepositoryProtocol,
        campaigns_repository: CampaignsRepositoryProtocol,
        mapper: StatisticsMapper,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._campaigns_repository = campaigns_repository
        self._mapper = mapper

    async def execute(self, campaign_id: UUID) -> StatsResponse:
        try:
            async with self._uow:
                await self._campaigns_repository.get_by_id(campaign_id)

                statistics = await self._repository.get_campaign_stats(campaign_id)
                return self._mapper.from_entity_to_statistics_schema(statistics)
        except CampaignNotFoundException as e:
            raise CampaignNotFoundException(str(e))
        except StatisticsRepositoryError as e:
            raise StatisticsRepositoryError(str(e))
        except Exception as e:
            raise StatisticsRepositoryError(f"Unexpected error: {str(e)}")


class GetAdvertiserCampaignsStatsUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: StatisticsRepositoryProtocol,
        advertisers_repository: AdvertisersRepositoryProtocol,
        mapper: StatisticsMapper,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._advertisers_repository = advertisers_repository
        self._mapper = mapper

    async def execute(self, advertiser_id: UUID) -> StatsResponse:
        try:
            async with self._uow:
                await self._advertisers_repository.get_by_id(advertiser_id)

                statistics = await self._repository.get_advertiser_stats(advertiser_id)
                return self._mapper.from_entity_to_statistics_schema(statistics)
        except AdvertiserNotFoundException as e:
            raise AdvertiserNotFoundException(str(e))
        except StatisticsRepositoryError as e:
            raise StatisticsRepositoryError(str(e))
        except Exception as e:
            raise StatisticsRepositoryError(f"Unexpected error: {str(e)}")


class GetCampaignDailyStatsUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: StatisticsRepositoryProtocol,
        campaigns_repository: CampaignsRepositoryProtocol,
        mapper: StatisticsMapper,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._campaigns_repository = campaigns_repository
        self._mapper = mapper

    async def execute(self, campaign_id: UUID) -> List[DailyStatsResponse]:
        try:
            async with self._uow:
                await self._campaigns_repository.get_by_id(campaign_id)

                statistics = await self._repository.get_campaign_daily_stats(
                    campaign_id
                )
                return [
                    self._mapper.from_entity_to_schema_daily_stats(statistic)
                    for statistic in statistics
                ]
        except CampaignNotFoundException as e:
            raise CampaignNotFoundException(str(e))
        except StatisticsRepositoryError as e:
            raise StatisticsRepositoryError(str(e))
        except Exception as e:
            raise StatisticsRepositoryError(f"Unexpected error: {str(e)}")


class GetAdvertiserDailyStatsUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: StatisticsRepositoryProtocol,
        advertisers_repository: AdvertisersRepositoryProtocol,
        mapper: StatisticsMapper,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._advertisers_repository = advertisers_repository
        self._mapper = mapper

    async def execute(self, advertiser_id: UUID) -> List[DailyStatsResponse]:
        try:
            async with self._uow:
                await self._advertisers_repository.get_by_id(advertiser_id)

                statistics = await self._repository.get_advertiser_daily_stats(
                    advertiser_id
                )
                return [
                    self._mapper.from_entity_to_schema_daily_stats(statistic)
                    for statistic in statistics
                ]
        except AdvertiserNotFoundException as e:
            raise AdvertiserNotFoundException(str(e))
        except StatisticsRepositoryError as e:
            raise StatisticsRepositoryError(str(e))
        except Exception as e:
            raise StatisticsRepositoryError(f"Unexpected error: {str(e)}")


class GetClientsStatsUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: StatisticsRepositoryProtocol,
    ) -> None:
        self._uow = uow
        self._repository = repository

    async def execute(self) -> ClientStatsResponse:
        try:
            async with self._uow:
                statistics = await self._repository.get_clients_stats()
                return statistics
        except StatisticsRepositoryError as e:
            raise StatisticsRepositoryError(str(e))
        except Exception as e:
            raise StatisticsRepositoryError(f"Unexpected error: {str(e)}")


class GetCampaignFeedbackStatsUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: StatisticsRepositoryProtocol,
        campaigns_repository: CampaignsRepositoryProtocol,
        mapper: StatisticsMapper,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._campaigns_repository = campaigns_repository
        self._mapper = mapper

    async def execute(self, campaign_id: UUID) -> CampaignFeedbackResponse:
        try:
            async with self._uow:
                await self._campaigns_repository.get_by_id(campaign_id)

                feedbacks = await self._repository.get_campaign_feedbacks(campaign_id)
                return self._mapper.from_entity_to_schema_campaign_feedback(feedbacks)
        except CampaignNotFoundException as e:
            raise CampaignNotFoundException(str(e))
        except StatisticsRepositoryError as e:
            raise StatisticsRepositoryError(str(e))
        except Exception as e:
            raise StatisticsRepositoryError(f"Unexpected error: {str(e)}")
