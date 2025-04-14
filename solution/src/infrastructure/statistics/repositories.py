from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.statistics.dtos import ClientStatsResponse
from src.common.types import EVENT_TYPE_CLICK, EVENT_TYPE_IMPRESSION
from src.domain.campaigns.exceptions import CampaignNotFoundException
from src.domain.statistics.entities import FeedbackEntity, StatisticsEntity
from src.domain.statistics.exceptions import (
    ClicksLimitReachedError,
    DuplicateClickError,
    NoImpressionError,
    StatisticsRepositoryError,
)
from src.domain.time.interfaces import TimeRepositoryProtocol
from src.infrastructure.statistics.mappers import StatisticsMapper
from src.infrastructure.statistics.orm import UniqueEventModel


class StatisticsRepository:
    def __init__(
        self,
        session: AsyncSession,
        mapper: StatisticsMapper,
        time_repository: TimeRepositoryProtocol,
    ) -> None:
        self._session = session
        self._mapper = mapper
        self._time_repository = time_repository

    async def get_campaign_stats(self, campaign_id: UUID) -> StatisticsEntity:
        try:
            current_day = await self._time_repository.get_current_date()
            query = text(
                """
                WITH event_stats AS (
                    SELECT 
                        campaign_id,
                        SUM(CASE WHEN event_type = :impression_type THEN 1 ELSE 0 END) as impressions_count,
                        SUM(CASE WHEN event_type = :click_type THEN 1 ELSE 0 END) as clicks_count
                    FROM unique_events
                    WHERE campaign_id = :campaign_id
                    GROUP BY campaign_id
                )
                SELECT 
                    c.id as campaign_id,
                    CAST(:current_day AS INTEGER) as date,
                    COALESCE(e.impressions_count, 0) as impressions_count,
                    COALESCE(e.clicks_count, 0) as clicks_count,
                    CASE 
                        WHEN COALESCE(e.impressions_count, 0) > 0 
                        THEN CAST(COALESCE(e.clicks_count, 0) AS FLOAT) / COALESCE(e.impressions_count, 0)
                        ELSE 0 
                    END as conversion,
                    COALESCE(e.impressions_count, 0) * c.cost_per_impression as spent_impressions,
                    COALESCE(e.clicks_count, 0) * c.cost_per_click as spent_clicks,
                    (COALESCE(e.impressions_count, 0) * c.cost_per_impression) + 
                    (COALESCE(e.clicks_count, 0) * c.cost_per_click) as spent_total
                FROM campaigns c
                LEFT JOIN event_stats e ON c.id = e.campaign_id
                WHERE c.id = :campaign_id
                """
            )
            result = await self._session.execute(
                query,
                {
                    "campaign_id": campaign_id,
                    "impression_type": EVENT_TYPE_IMPRESSION,
                    "click_type": EVENT_TYPE_CLICK,
                    "current_day": current_day,
                },
            )
            model = result.mappings().first()
            if not model:
                raise CampaignNotFoundException(
                    f"Рекламная кампания с id {campaign_id} не найдена"
                )
            return StatisticsEntity(
                id=uuid4(),
                campaign_id=model["campaign_id"],
                date=model["date"],
                impressions_count=model["impressions_count"],
                clicks_count=model["clicks_count"],
                conversion=model["conversion"],
                spent_impressions=model["spent_impressions"],
                spent_clicks=model["spent_clicks"],
                spent_total=model["spent_total"],
            )
        except SQLAlchemyError as e:
            raise StatisticsRepositoryError(f"Db error: {str(e)}")
        except Exception as e:
            raise StatisticsRepositoryError(
                f"Unexpected error in get_campaign_stats: {str(e)}"
            )

    async def get_advertiser_stats(self, advertiser_id: UUID) -> StatisticsEntity:
        try:
            current_day = await self._time_repository.get_current_date()
            query = text(
                """
                WITH event_stats AS (
                    SELECT 
                        c.advertiser_id,
                        SUM(CASE WHEN ue.event_type = :impression_type THEN 1 ELSE 0 END) as impressions_count,
                        SUM(CASE WHEN ue.event_type = :click_type THEN 1 ELSE 0 END) as clicks_count
                    FROM campaigns c
                    LEFT JOIN unique_events ue ON c.id = ue.campaign_id
                    WHERE c.advertiser_id = :advertiser_id
                    GROUP BY c.advertiser_id
                )
                SELECT 
                    :advertiser_id as campaign_id,
                    CAST(:current_day AS INTEGER) as date,
                    COALESCE(e.impressions_count, 0) as impressions_count,
                    COALESCE(e.clicks_count, 0) as clicks_count,
                    CASE 
                        WHEN COALESCE(e.impressions_count, 0) > 0 
                        THEN CAST(COALESCE(e.clicks_count, 0) AS FLOAT) / COALESCE(e.impressions_count, 0)
                        ELSE 0 
                    END as conversion,
                    SUM(COALESCE(e.impressions_count, 0) * c.cost_per_impression) as spent_impressions,
                    SUM(COALESCE(e.clicks_count, 0) * c.cost_per_click) as spent_clicks,
                    SUM(
                        (COALESCE(e.impressions_count, 0) * c.cost_per_impression) + 
                        (COALESCE(e.clicks_count, 0) * c.cost_per_click)
                    ) as spent_total
                FROM campaigns c
                LEFT JOIN event_stats e ON c.advertiser_id = e.advertiser_id
                WHERE c.advertiser_id = :advertiser_id
                GROUP BY c.advertiser_id, e.impressions_count, e.clicks_count
                """
            )
            result = await self._session.execute(
                query,
                {
                    "advertiser_id": advertiser_id,
                    "impression_type": EVENT_TYPE_IMPRESSION,
                    "click_type": EVENT_TYPE_CLICK,
                    "current_day": current_day,
                },
            )
            model = result.mappings().first()
            if not model:
                return StatisticsEntity(
                    id=uuid4(),
                    campaign_id=uuid4(),
                    date=current_day,
                    impressions_count=0,
                    clicks_count=0,
                    conversion=0.0,
                    spent_impressions=0.0,
                    spent_clicks=0.0,
                    spent_total=0.0,
                )
            return StatisticsEntity(
                id=uuid4(),
                campaign_id=model["campaign_id"],
                date=model["date"],
                impressions_count=model["impressions_count"],
                clicks_count=model["clicks_count"],
                conversion=model["conversion"],
                spent_impressions=model["spent_impressions"],
                spent_clicks=model["spent_clicks"],
                spent_total=model["spent_total"],
            )
        except SQLAlchemyError as e:
            raise StatisticsRepositoryError(f"Db error: {str(e)}")
        except Exception as e:
            raise StatisticsRepositoryError(
                f"Unexpected error in get_advertiser_stats: {str(e)}"
            )

    async def get_campaign_daily_stats(
        self, campaign_id: UUID
    ) -> List[StatisticsEntity]:
        try:
            query = text(
                """
                WITH daily_stats AS (
                    SELECT 
                        campaign_id,
                        date,
                        SUM(CASE WHEN event_type = :impression_type THEN 1 ELSE 0 END) as impressions_count,
                        SUM(CASE WHEN event_type = :click_type THEN 1 ELSE 0 END) as clicks_count
                    FROM unique_events
                    WHERE campaign_id = :campaign_id
                    GROUP BY campaign_id, date
                )
                SELECT 
                    c.id as campaign_id,
                    COALESCE(d.date, c.start_date) as date,
                    COALESCE(d.impressions_count, 0) as impressions_count,
                    COALESCE(d.clicks_count, 0) as clicks_count,
                    CASE 
                        WHEN COALESCE(d.impressions_count, 0) > 0 
                        THEN CAST(COALESCE(d.clicks_count, 0) AS FLOAT) / COALESCE(d.impressions_count, 0)
                        ELSE 0 
                    END as conversion,
                    COALESCE(d.impressions_count, 0) * c.cost_per_impression as spent_impressions,
                    COALESCE(d.clicks_count, 0) * c.cost_per_click as spent_clicks,
                    (COALESCE(d.impressions_count, 0) * c.cost_per_impression) + 
                    (COALESCE(d.clicks_count, 0) * c.cost_per_click) as spent_total
                FROM campaigns c
                LEFT JOIN daily_stats d ON c.id = d.campaign_id
                WHERE c.id = :campaign_id
                ORDER BY COALESCE(d.date, c.start_date)
                """
            )
            result = await self._session.execute(
                query,
                {
                    "campaign_id": campaign_id,
                    "impression_type": EVENT_TYPE_IMPRESSION,
                    "click_type": EVENT_TYPE_CLICK,
                },
            )
            models = result.mappings().all()
            return [
                StatisticsEntity(
                    id=uuid4(),
                    campaign_id=model["campaign_id"],
                    date=model["date"],
                    impressions_count=model["impressions_count"],
                    clicks_count=model["clicks_count"],
                    conversion=model["conversion"],
                    spent_impressions=model["spent_impressions"],
                    spent_clicks=model["spent_clicks"],
                    spent_total=model["spent_total"],
                )
                for model in models
            ]
        except SQLAlchemyError as e:
            raise StatisticsRepositoryError(f"Db error: {str(e)}")
        except Exception as e:
            raise StatisticsRepositoryError(
                f"Unexpected error in get_campaign_daily_stats: {str(e)}"
            )

    async def get_advertiser_daily_stats(
        self, advertiser_id: UUID
    ) -> List[StatisticsEntity]:
        try:
            query = text(
                """
                WITH daily_stats AS (
                    SELECT 
                        c.advertiser_id,
                        ue.date,
                        SUM(CASE WHEN ue.event_type = :impression_type THEN 1 ELSE 0 END) as impressions_count,
                        SUM(CASE WHEN ue.event_type = :click_type THEN 1 ELSE 0 END) as clicks_count
                    FROM campaigns c
                    LEFT JOIN unique_events ue ON c.id = ue.campaign_id
                    WHERE c.advertiser_id = :advertiser_id
                    GROUP BY c.advertiser_id, ue.date
                )
                SELECT 
                    :advertiser_id as campaign_id,
                    COALESCE(d.date, (SELECT MIN(start_date) FROM campaigns WHERE advertiser_id = :advertiser_id)) as date,
                    COALESCE(d.impressions_count, 0) as impressions_count,
                    COALESCE(d.clicks_count, 0) as clicks_count,
                    CASE 
                        WHEN COALESCE(d.impressions_count, 0) > 0 
                        THEN CAST(COALESCE(d.clicks_count, 0) AS FLOAT) / COALESCE(d.impressions_count, 0)
                        ELSE 0 
                    END as conversion,
                    SUM(COALESCE(d.impressions_count, 0) * c.cost_per_impression) as spent_impressions,
                    SUM(COALESCE(d.clicks_count, 0) * c.cost_per_click) as spent_clicks,
                    SUM(
                        (COALESCE(d.impressions_count, 0) * c.cost_per_impression) + 
                        (COALESCE(d.clicks_count, 0) * c.cost_per_click)
                    ) as spent_total
                FROM campaigns c
                LEFT JOIN daily_stats d ON c.advertiser_id = d.advertiser_id
                WHERE c.advertiser_id = :advertiser_id
                GROUP BY c.advertiser_id, d.date, d.impressions_count, d.clicks_count
                ORDER BY COALESCE(d.date, (SELECT MIN(start_date) FROM campaigns WHERE advertiser_id = :advertiser_id))
                """
            )
            result = await self._session.execute(
                query,
                {
                    "advertiser_id": advertiser_id,
                    "impression_type": EVENT_TYPE_IMPRESSION,
                    "click_type": EVENT_TYPE_CLICK,
                },
            )
            models = result.mappings().all()
            return [
                StatisticsEntity(
                    id=uuid4(),
                    campaign_id=model["campaign_id"],
                    date=model["date"],
                    impressions_count=model["impressions_count"],
                    clicks_count=model["clicks_count"],
                    conversion=model["conversion"],
                    spent_impressions=model["spent_impressions"],
                    spent_clicks=model["spent_clicks"],
                    spent_total=model["spent_total"],
                )
                for model in models
            ]
        except SQLAlchemyError as e:
            raise StatisticsRepositoryError(f"Db error: {str(e)}")
        except Exception as e:
            raise StatisticsRepositoryError(
                f"Unexpected error in get_advertiser_daily_stats: {str(e)}"
            )

    async def register_impression(self, client_id: UUID, campaign_id: UUID):
        try:
            current_day = await self._time_repository.get_current_date()

            result = await self._session.execute(
                text("""
                    WITH campaign_stats AS (
                        SELECT 
                            c.impressions_limit,
                            COUNT(*) FILTER (WHERE ue.event_type = :impression_type) as current_impressions,
                            EXISTS (
                                SELECT 1 
                                FROM unique_events 
                                WHERE campaign_id = :campaign_id 
                                AND client_id = :client_id 
                                AND event_type = :impression_type
                            ) as has_impression
                        FROM campaigns c
                        LEFT JOIN unique_events ue ON c.id = ue.campaign_id AND ue.event_type = :impression_type
                        WHERE c.id = :campaign_id
                        GROUP BY c.id, c.impressions_limit
                    )
                    INSERT INTO unique_events (id, campaign_id, client_id, event_type, date, created_at, updated_at)
                    SELECT 
                        :event_id, 
                        :campaign_id, 
                        :client_id, 
                        :impression_type, 
                        :current_day,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    FROM campaign_stats
                    WHERE 
                        has_impression = false AND
                        (
                            impressions_limit IS NULL OR
                            current_impressions < impressions_limit
                        )
                    RETURNING id
                """),
                {
                    "event_id": uuid4(),
                    "campaign_id": campaign_id,
                    "client_id": client_id,
                    "impression_type": EVENT_TYPE_IMPRESSION,
                    "current_day": current_day,
                },
            )

            if result.scalar_one_or_none() is None:
                check = await self._session.execute(
                    text("""
                        SELECT 
                            EXISTS (SELECT 1 FROM campaigns WHERE id = :campaign_id) as campaign_exists,
                            EXISTS (
                                SELECT 1 FROM unique_events 
                                WHERE campaign_id = :campaign_id 
                                AND client_id = :client_id 
                                AND event_type = :impression_type
                            ) as has_impression,
                            (
                                SELECT impressions_limit 
                                FROM campaigns 
                                WHERE id = :campaign_id
                            ) as impressions_limit,
                            (
                                SELECT COUNT(*) 
                                FROM unique_events 
                                WHERE campaign_id = :campaign_id 
                                AND event_type = :impression_type
                            ) as current_impressions
                    """),
                    {
                        "campaign_id": campaign_id,
                        "client_id": client_id,
                        "impression_type": EVENT_TYPE_IMPRESSION,
                    },
                )
                check_data = check.mappings().first()
                if check_data is None:
                    raise StatisticsRepositoryError(
                        "Failed to check impression registration status"
                    )

                if not check_data.get("campaign_exists", False):
                    raise CampaignNotFoundException("Campaign not found")
                elif check_data.get("has_impression", False) or (
                    check_data.get("impressions_limit") is not None
                    and check_data.get("current_impressions", 0)
                    >= check_data.get("impressions_limit", 0)
                ):
                    return
                else:
                    raise StatisticsRepositoryError(
                        "Failed to register impression for unknown reason"
                    )

            await self._session.flush()
        except SQLAlchemyError as e:
            raise StatisticsRepositoryError(f"Db error: {str(e)}")
        except Exception as e:
            raise StatisticsRepositoryError(
                f"Unexpected error in register_impression: {str(e)}"
            )

    async def register_click(self, client_id: UUID, campaign_id: UUID):
        try:
            current_day = await self._time_repository.get_current_date()

            result = await self._session.execute(
                text("""
                    WITH campaign_stats AS (
                        SELECT 
                            c.clicks_limit,
                            COUNT(*) FILTER (WHERE ue.event_type = :click_type) as current_clicks,
                            EXISTS (
                                SELECT 1 
                                FROM unique_events 
                                WHERE campaign_id = :campaign_id 
                                AND client_id = :client_id 
                                AND event_type = :impression_type
                            ) as has_impression,
                            EXISTS (
                                SELECT 1 
                                FROM unique_events 
                                WHERE campaign_id = :campaign_id 
                                AND client_id = :client_id 
                                AND event_type = :click_type
                            ) as has_click
                        FROM campaigns c
                        LEFT JOIN unique_events ue ON c.id = ue.campaign_id AND ue.event_type = :click_type
                        WHERE c.id = :campaign_id
                        GROUP BY c.id, c.clicks_limit
                    )
                    INSERT INTO unique_events (id, campaign_id, client_id, event_type, date, created_at, updated_at)
                    SELECT 
                        :event_id, 
                        :campaign_id, 
                        :client_id, 
                        :click_type, 
                        :current_day,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    FROM campaign_stats
                    WHERE 
                        has_impression = true AND
                        has_click = false AND
                        (
                            clicks_limit IS NULL OR
                            current_clicks < clicks_limit
                        )
                    RETURNING id
                """),
                {
                    "event_id": uuid4(),
                    "campaign_id": campaign_id,
                    "client_id": client_id,
                    "click_type": EVENT_TYPE_CLICK,
                    "impression_type": EVENT_TYPE_IMPRESSION,
                    "current_day": current_day,
                },
            )

            if result.scalar_one_or_none() is None:
                check = await self._session.execute(
                    text("""
                        SELECT 
                            EXISTS (SELECT 1 FROM campaigns WHERE id = :campaign_id) as campaign_exists,
                            EXISTS (
                                SELECT 1 FROM unique_events 
                                WHERE campaign_id = :campaign_id 
                                AND client_id = :client_id 
                                AND event_type = :impression_type
                            ) as has_impression,
                            EXISTS (
                                SELECT 1 FROM unique_events 
                                WHERE campaign_id = :campaign_id 
                                AND client_id = :client_id 
                                AND event_type = :click_type
                            ) as has_click,
                            (
                                SELECT clicks_limit 
                                FROM campaigns 
                                WHERE id = :campaign_id
                            ) as clicks_limit,
                            (
                                SELECT COUNT(*) 
                                FROM unique_events 
                                WHERE campaign_id = :campaign_id 
                                AND event_type = :click_type
                            ) as current_clicks
                    """),
                    {
                        "campaign_id": campaign_id,
                        "client_id": client_id,
                        "impression_type": EVENT_TYPE_IMPRESSION,
                        "click_type": EVENT_TYPE_CLICK,
                    },
                )
                check_data = check.mappings().first()
                if check_data is None:
                    raise StatisticsRepositoryError(
                        "Failed to check click registration status"
                    )

                if not check_data.get("campaign_exists", False):
                    raise CampaignNotFoundException(
                        f"Campaign with id {campaign_id} not found"
                    )
                elif not check_data.get("has_impression", False):
                    raise NoImpressionError(
                        "Cannot register click without prior impression"
                    )
                elif check_data.get("has_click", False):
                    raise DuplicateClickError(
                        "Click already registered for this client and campaign"
                    )
                elif check_data.get("clicks_limit") is not None and check_data.get(
                    "current_clicks", 0
                ) >= check_data.get("clicks_limit", 0):
                    raise ClicksLimitReachedError(
                        "Clicks limit has been reached for this campaign"
                    )
                else:
                    raise StatisticsRepositoryError(
                        "Failed to register click for unknown reason"
                    )

            await self._session.flush()
        except SQLAlchemyError as e:
            raise StatisticsRepositoryError(f"Database error: {str(e)}")
        except (
            CampaignNotFoundException,
            NoImpressionError,
            DuplicateClickError,
            ClicksLimitReachedError,
        ) as e:
            raise e
        except Exception as e:
            raise StatisticsRepositoryError(
                f"Unexpected error in register_click: {str(e)}"
            )

    async def get_clients_stats(self) -> ClientStatsResponse:
        try:
            total_clients_query = text("SELECT COUNT(*) FROM clients")
            total_clients_result = await self._session.execute(total_clients_query)
            total_clients = total_clients_result.scalar() or 0

            demographics_query = text("""
                SELECT 
                    gender,
                    CASE 
                        WHEN age < 18 THEN '<18'
                        WHEN age BETWEEN 18 AND 24 THEN '18-24'
                        WHEN age BETWEEN 25 AND 34 THEN '25-34'
                        WHEN age BETWEEN 35 AND 44 THEN '35-44'
                        WHEN age BETWEEN 45 AND 54 THEN '45-54'
                        ELSE '55+'
                    END as age_group,
                    COUNT(*) as count
                FROM clients
                GROUP BY gender, age_group
                ORDER BY gender, age_group
            """)
            demographics_result = await self._session.execute(demographics_query)
            demographics_data = demographics_result.mappings().all()

            demographics_distribution: Dict[str, Dict[str, int]] = {}
            for row in demographics_data:
                gender = row["gender"]
                age_group = row["age_group"]
                count = row["count"]
                if gender not in demographics_distribution:
                    demographics_distribution[gender] = {}
                demographics_distribution[gender][age_group] = count

            locations_query = text("""
                SELECT location, COUNT(*) as count
                FROM clients
                GROUP BY location
                ORDER BY count DESC
                LIMIT 10
            """)
            locations_result = await self._session.execute(locations_query)
            top_locations = [
                {"location": row["location"], "count": row["count"]}
                for row in locations_result.mappings().all()
            ]

            avg_age_query = text("SELECT AVG(age) FROM clients")
            avg_age_result = await self._session.execute(avg_age_query)
            average_age = avg_age_result.scalar() or 0.0

            return ClientStatsResponse(
                total_clients=total_clients,
                demographics_distribution=demographics_distribution,
                top_locations=top_locations,
                average_age=float(average_age),
            )
        except SQLAlchemyError as e:
            raise StatisticsRepositoryError(f"Db error: {str(e)}")
        except Exception as e:
            raise StatisticsRepositoryError(
                f"Unexpected error in get_clients_stats: {str(e)}"
            )

    async def register_feedback(
        self, client_id: UUID, campaign_id: UUID, rating: int, comment: Optional[str]
    ) -> None:
        try:
            current_day = await self._time_repository.get_current_date()
            feedback = UniqueEventModel(
                id=uuid4(),
                campaign_id=campaign_id,
                client_id=client_id,
                event_type="feedback",
                date=current_day,
                rating=rating,
                comment=comment,
            )
            self._session.add(feedback)
        except SQLAlchemyError as e:
            raise StatisticsRepositoryError(f"Db error: {str(e)}")
        except Exception as e:
            raise StatisticsRepositoryError(
                f"Unexpected error in register_feedback: {str(e)}"
            )

    async def get_campaign_feedbacks(self, campaign_id: UUID) -> List[FeedbackEntity]:
        try:
            query = text("""
                SELECT id, campaign_id, client_id, rating, comment, created_at 
                FROM unique_events
                WHERE campaign_id = :campaign_id AND event_type = 'feedback'
                ORDER BY created_at DESC
                LIMIT 10
            """)
            result = await self._session.execute(query, {"campaign_id": campaign_id})
            return [FeedbackEntity(**row) for row in result.mappings().all()]
        except SQLAlchemyError as e:
            raise StatisticsRepositoryError(f"Db error: {str(e)}")
        except Exception as e:
            raise StatisticsRepositoryError(
                f"Unexpected error in get_campaign_feedbacks: {str(e)}"
            )
