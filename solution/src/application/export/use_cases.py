from typing import List
from uuid import UUID

from src.application.export.dtos import (
    AdvertiserExportSchema,
    CampaignExportSchema,
    MLScoreExportSchema,
    StatisticsExportSchema,
    UniqueEventExportSchema,
)
from src.core.uow import AbstractUow
from src.domain.advertisers.exceptions import AdvertiserNotFoundException
from src.domain.advertisers.interfaces import (
    AdvertisersRepositoryProtocol,
    MLScoreRepositoryProtocol,
)
from src.domain.campaigns.entities import CampaignEntity
from src.domain.campaigns.interfaces import CampaignsRepositoryProtocol
from src.domain.export.interfaces import ExportServiceProtocol
from src.domain.statistics.entities import FeedbackEntity, StatisticsEntity
from src.domain.statistics.interfaces import StatisticsRepositoryProtocol


class ExportAdvertiserDataUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        advertisers_repository: AdvertisersRepositoryProtocol,
        campaigns_repository: CampaignsRepositoryProtocol,
        statistics_repository: StatisticsRepositoryProtocol,
        ml_score_repository: MLScoreRepositoryProtocol,
        export_service: ExportServiceProtocol,
    ):
        self.uow = uow
        self.advertisers_repository = advertisers_repository
        self.campaigns_repository = campaigns_repository
        self.statistics_repository = statistics_repository
        self.ml_score_repository = ml_score_repository
        self.export_service = export_service

    async def execute(self, advertiser_id: UUID) -> bytes:
        async with self.uow:
            try:
                advertiser = await self.advertisers_repository.get_by_id(advertiser_id)
            except AdvertiserNotFoundException:
                raise ValueError(f"Рекламодатель {advertiser_id} не найден")

            campaigns: List[CampaignEntity] = []
            page = 1
            page_size = 100

            while True:
                page_campaigns = await self.campaigns_repository.get_all(
                    advertiser_id=advertiser_id,
                    size=page_size,
                    page=page,
                )
                if not page_campaigns:
                    break

                campaigns.extend(page_campaigns)
                page += 1

            campaign_exports: List[CampaignExportSchema] = []
            for campaign in campaigns:
                stats: StatisticsEntity = (
                    await self.statistics_repository.get_campaign_stats(campaign.id)
                )

                stats_export = []
                if stats:
                    stats_export = [
                        StatisticsExportSchema(
                            date=stats.date or 0,
                            impressions_count=stats.impressions_count or 0,
                            clicks_count=stats.clicks_count or 0,
                            conversion=stats.conversion or 0.0,
                            spent_impressions=stats.spent_impressions or 0.0,
                            spent_clicks=stats.spent_clicks or 0.0,
                            spent_total=stats.spent_total or 0.0,
                            created_at=0,
                            updated_at=0,
                        )
                    ]

                feedbacks: List[
                    FeedbackEntity
                ] = await self.statistics_repository.get_campaign_feedbacks(campaign.id)

                campaign_exports.append(
                    CampaignExportSchema(
                        campaign_id=campaign.id,
                        image_url=campaign.image_url,
                        impressions_limit=campaign.impressions_limit,
                        clicks_limit=campaign.clicks_limit,
                        cost_per_impression=campaign.cost_per_impression,
                        cost_per_click=campaign.cost_per_click,
                        ad_title=campaign.ad_title,
                        ad_text=campaign.ad_text,
                        start_date=campaign.start_date,
                        end_date=campaign.end_date,
                        gender=str(campaign.gender) if campaign.gender else None,
                        age_from=campaign.age_from,
                        age_to=campaign.age_to,
                        location=campaign.location,
                        created_at=0,
                        updated_at=0,
                        statistics=stats_export,
                        unique_events=[
                            UniqueEventExportSchema(
                                client_id=feedback.client_id,
                                event_type="feedback",
                                rating=feedback.rating,
                                comment=feedback.comment,
                                created_at=int(feedback.created_at.timestamp()),
                                updated_at=0,
                            )
                            for feedback in feedbacks
                        ],
                    )
                )

            unique_client_ids = {
                feedback.client_id
                for campaign in campaigns
                for feedback in await self.statistics_repository.get_campaign_feedbacks(
                    campaign.id
                )
            }

            ml_score_exports = [
                MLScoreExportSchema(
                    client_id=client_id,
                    score=await self.ml_score_repository.get_ml_score(
                        client_id, advertiser_id
                    )
                    or 0,
                    created_at=0,
                    updated_at=0,
                )
                for client_id in unique_client_ids
            ]

            export_data = AdvertiserExportSchema(
                advertiser_id=advertiser.id,
                name=advertiser.name,
                created_at=0,
                updated_at=0,
                campaigns=campaign_exports,
                ml_scores=ml_score_exports,
                telegram_users=[],
            )

            return self.export_service.create_export_archive(export_data)
