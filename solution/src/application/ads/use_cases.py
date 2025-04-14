from typing import List, Optional
from uuid import UUID

from src.application.ads.dtos import AdsGetResponse
from src.core.uow import AbstractUow
from src.domain.ads.entities import AdEntity
from src.domain.ads.exceptions import AdsNotFoundException
from src.domain.ads.interfaces import (
    SubmitAdFeedbackUseCaseProtocol,
)
from src.domain.advertisers.interfaces import (
    MLScoreRepositoryProtocol,
)
from src.domain.campaigns.entities import CampaignEntity
from src.domain.campaigns.exceptions import CampaignNotFoundException
from src.domain.campaigns.interfaces import (
    CampaignsRepositoryProtocol,
)
from src.domain.clients.entities import ClientEntity
from src.domain.clients.exceptions import ClientNotFoundException
from src.domain.clients.interfaces import (
    ClientsRepositoryProtocol,
)
from src.domain.statistics.entities import StatisticsEntity
from src.domain.statistics.exceptions import (
    ClicksLimitReachedError,
    DuplicateClickError,
    NoImpressionError,
    StatisticsRepositoryError,
)
from src.domain.statistics.interfaces import (
    StatisticsRepositoryProtocol,
)
from src.domain.time.interfaces import TimeRepositoryProtocol
from src.infrastructure.ads.mappers import AdsMapper


class GetAdForClientUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        mapper: AdsMapper,
        time_repository: TimeRepositoryProtocol,
        clients_repository: ClientsRepositoryProtocol,
        campaigns_repository: CampaignsRepositoryProtocol,
        ml_score_repository: MLScoreRepositoryProtocol,
        statistics_repository: StatisticsRepositoryProtocol,
    ):
        self._uow = uow
        self._mapper = mapper
        self._time_repository = time_repository
        self._clients_repository = clients_repository
        self._campaigns_repository = campaigns_repository
        self._ml_score_repository = ml_score_repository
        self._statistics_repository = statistics_repository

    async def execute(self, client_id: UUID) -> AdsGetResponse:
        async with self._uow:
            try:
                client = await self._clients_repository.get_by_id(client_id)
            except ClientNotFoundException:
                raise ClientNotFoundException(f"Клиент с id {client_id} не найден")

            targeted_campaigns = (
                await self._campaigns_repository.get_targeted_campaigns(client_id)
            )

            if not targeted_campaigns:
                raise AdsNotFoundException(
                    "Не найдены подходящие объявления по таргетингу"
                )

            best_campaign = await self._get_best_matching_campaign(
                targeted_campaigns, client
            )
            if not best_campaign:
                raise AdsNotFoundException("Не найдены подходящие объявления")

            async with self._uow.impression_lock:
                await self._statistics_repository.register_impression(
                    client_id=client.id, campaign_id=best_campaign.id
                )
                ad_entity: AdEntity = self._mapper.from_model_to_entity(best_campaign)
                await self._uow.commit()
            return self._mapper.from_entity_to_schema(ad_entity)

    async def _get_best_matching_campaign(
        self, campaigns: List[CampaignEntity], client: ClientEntity
    ) -> CampaignEntity | None:
        best_campaign = None
        best_score = float("-inf")

        for campaign in campaigns:
            ml_score = (
                await self._ml_score_repository.get_ml_score(
                    client.id, campaign.advertiser_id
                )
                or 0
            )

            stats: StatisticsEntity = (
                await self._statistics_repository.get_campaign_stats(
                    campaign_id=campaign.id
                )
            )

            remaining_impressions = max(
                0, campaign.impressions_limit - stats.impressions_count
            )
            remaining_clicks = max(0, campaign.clicks_limit - stats.clicks_count)

            expected_profit = (remaining_impressions * campaign.cost_per_impression) + (
                remaining_clicks * campaign.cost_per_click
            )

            impressions_fulfillment = (
                stats.impressions_count / campaign.impressions_limit
                if campaign.impressions_limit > 0
                else 1
            )
            clicks_fulfillment = (
                stats.clicks_count / campaign.clicks_limit
                if campaign.clicks_limit > 0
                else 1
            )
            fulfillment_ratio = min(1, impressions_fulfillment) * min(
                1, clicks_fulfillment
            )

            score = (
                (ml_score * 0.25) + (expected_profit * 0.3) + (fulfillment_ratio * 0.35)
            )

            if score > best_score:
                best_score = score
                best_campaign = campaign

        return best_campaign


class RecordAdClickUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        mapper: AdsMapper,
        statistics_repository: StatisticsRepositoryProtocol,
        time_repository: TimeRepositoryProtocol,
        campaigns_repository: CampaignsRepositoryProtocol,
        clients_repository: ClientsRepositoryProtocol,
    ):
        self._uow = uow
        self._mapper = mapper
        self._statistics_repository = statistics_repository
        self._time_repository = time_repository
        self._campaigns_repository = campaigns_repository
        self._clients_repository = clients_repository

    async def execute(self, ad_id: UUID, client_id: UUID) -> None:
        try:
            async with self._uow:
                async with self._uow.click_lock:
                    try:
                        await self._campaigns_repository.get_by_id(ad_id)
                    except CampaignNotFoundException as e:
                        raise CampaignNotFoundException(str(e))

                    try:
                        await self._clients_repository.get_by_id(client_id)
                    except ClientNotFoundException as e:
                        raise ClientNotFoundException(str(e))

                    try:
                        await self._statistics_repository.register_click(
                            client_id=client_id, campaign_id=ad_id
                        )
                        await self._uow.commit()
                    except (
                        DuplicateClickError,
                        NoImpressionError,
                        ClicksLimitReachedError,
                    ) as e:
                        await self._uow.rollback()
                        raise e
                    except StatisticsRepositoryError as e:
                        await self._uow.rollback()
                        raise StatisticsRepositoryError(str(e))
        except (
            CampaignNotFoundException,
            ClientNotFoundException,
            DuplicateClickError,
            NoImpressionError,
            ClicksLimitReachedError,
        ) as e:
            raise e
        except Exception as e:
            await self._uow.rollback()
            raise StatisticsRepositoryError(
                f"Unexpected error recording click: {str(e)}"
            )


class SubmitAdFeedbackUseCase(SubmitAdFeedbackUseCaseProtocol):
    def __init__(
        self,
        uow: AbstractUow,
        statistics_repository: StatisticsRepositoryProtocol,
        clients_repository: ClientsRepositoryProtocol,
        campaigns_repository: CampaignsRepositoryProtocol,
    ) -> None:
        self._uow = uow
        self._statistics_repository = statistics_repository
        self._clients_repository = clients_repository
        self._campaigns_repository = campaigns_repository

    async def execute(
        self, ad_id: UUID, client_id: UUID, rating: int, comment: Optional[str]
    ) -> None:
        async with self._uow:
            try:
                await self._clients_repository.get_by_id(client_id)
            except ClientNotFoundException:
                raise ClientNotFoundException(f"Клиент с id {client_id} не найден")

            try:
                await self._campaigns_repository.get_by_id(ad_id)
            except CampaignNotFoundException:
                raise CampaignNotFoundException(
                    f"Рекламная кампания с id {ad_id} не найдена"
                )

            await self._statistics_repository.register_feedback(
                client_id=client_id,
                campaign_id=ad_id,
                rating=rating,
                comment=comment,
            )
            await self._uow.commit()
