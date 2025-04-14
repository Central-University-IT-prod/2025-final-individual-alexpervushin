from typing import List

from src.application.statistics.dtos import (
    CampaignFeedbackItem,
    CampaignFeedbackResponse,
    DailyStatsResponse,
    StatsResponse,
)
from src.domain.statistics.entities import FeedbackEntity, StatisticsEntity


class StatisticsMapper:
    def from_entity_to_statistics_schema(
        self, entity: StatisticsEntity
    ) -> StatsResponse:
        return StatsResponse(
            impressions_count=entity.impressions_count,
            clicks_count=entity.clicks_count,
            conversion=entity.conversion,
            spent_impressions=entity.spent_impressions,
            spent_clicks=entity.spent_clicks,
            spent_total=entity.spent_total,
        )

    def from_entity_to_schema_daily_stats(
        self, entity: StatisticsEntity
    ) -> DailyStatsResponse:
        return DailyStatsResponse(
            impressions_count=entity.impressions_count,
            clicks_count=entity.clicks_count,
            conversion=entity.conversion,
            spent_impressions=entity.spent_impressions,
            spent_clicks=entity.spent_clicks,
            spent_total=entity.spent_total,
            date=entity.date,
        )

    def from_entity_to_schema_campaign_feedback(
        self, entities: List[FeedbackEntity]
    ) -> CampaignFeedbackResponse:
        if not entities:
            return CampaignFeedbackResponse(
                average_rating=0.0, total_ratings=0, feedbacks=[]
            )

        return CampaignFeedbackResponse(
            average_rating=sum(entity.rating for entity in entities) / len(entities),
            total_ratings=len(entities),
            feedbacks=[
                CampaignFeedbackItem(
                    client_id=entity.client_id,
                    rating=entity.rating,
                    comment=entity.comment,
                    created_at=entity.created_at,
                )
                for entity in entities
            ],
        )
