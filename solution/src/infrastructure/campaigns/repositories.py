from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import case, func, or_, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.enums import TargetingGender
from src.domain.campaigns.entities import (
    CampaignEntity,
    CampaignUpdateEntity,
)
from src.domain.campaigns.exceptions import (
    CampaignNotFoundException,
    CampaignRepositoryError,
)
from src.domain.time.interfaces import TimeRepositoryProtocol
from src.infrastructure.campaigns.mappers import CampaignsMapper
from src.infrastructure.campaigns.orm import CampaignModel
from src.infrastructure.clients.orm import ClientModel
from src.infrastructure.statistics.orm import UniqueEventModel


class CampaignsRepository:
    def __init__(
        self,
        session: AsyncSession,
        mapper: CampaignsMapper,
        time_repository: TimeRepositoryProtocol,
    ) -> None:
        self._session = session
        self._mapper = mapper
        self._time_repository = time_repository

    async def create(self, campaign: CampaignEntity) -> CampaignEntity:
        try:
            query = text("""
                INSERT INTO campaigns (
                    id, advertiser_id, impressions_limit, clicks_limit,
                    cost_per_impression, cost_per_click, ad_title, ad_text,
                    start_date, end_date, gender, age_from, age_to, location,
                    image_url, created_at, updated_at
                ) VALUES (
                    :id, :advertiser_id, :impressions_limit, :clicks_limit,
                    :cost_per_impression, :cost_per_click, :ad_title, :ad_text,
                    :start_date, :end_date, :gender, :age_from, :age_to, :location,
                    :image_url,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                ) RETURNING *;
            """)
            result = await self._session.execute(
                query,
                {
                    "id": campaign.id,
                    "advertiser_id": campaign.advertiser_id,
                    "impressions_limit": campaign.impressions_limit,
                    "clicks_limit": campaign.clicks_limit,
                    "cost_per_impression": campaign.cost_per_impression,
                    "cost_per_click": campaign.cost_per_click,
                    "ad_title": campaign.ad_title,
                    "ad_text": campaign.ad_text,
                    "start_date": campaign.start_date,
                    "end_date": campaign.end_date,
                    "gender": campaign.gender.value if campaign.gender else None,
                    "age_from": campaign.age_from,
                    "age_to": campaign.age_to,
                    "location": campaign.location,
                    "image_url": campaign.image_url,
                },
            )
            row = result.mappings().first()
            if not row:
                raise CampaignRepositoryError("Не удалось создать рекламную кампанию")
            await self._session.flush()
            return self._mapper.from_model_to_entity(CampaignModel(**row))
        except SQLAlchemyError as e:
            raise CampaignRepositoryError(f"Db error: {str(e)}")

    async def get_all(
        self, advertiser_id: UUID, size: Optional[int], page: Optional[int]
    ) -> List[CampaignEntity]:
        try:
            query = text("""
                SELECT * FROM campaigns 
                WHERE advertiser_id = :advertiser_id
            """)
            params: Dict[str, Any] = {"advertiser_id": advertiser_id}

            if size is not None and page is not None:
                query = text(query.text + " LIMIT :size OFFSET :offset")
                params.update({"size": size, "offset": size * (page - 1)})

            result = await self._session.execute(query, params)
            rows = result.mappings().all()

            return [
                self._mapper.from_model_to_entity(CampaignModel(**row)) for row in rows
            ]
        except SQLAlchemyError as e:
            raise CampaignRepositoryError(f"Db error: {str(e)}")

    async def get_by_id(self, campaign_id: UUID) -> CampaignEntity:
        try:
            query = text("""
                SELECT * FROM campaigns 
                WHERE id = :campaign_id
            """)
            result = await self._session.execute(query, {"campaign_id": campaign_id})
            row = result.mappings().first()
            if not row:
                raise CampaignNotFoundException(
                    f"Рекламодатель с id {campaign_id} не найден"
                )

            return self._mapper.from_model_to_entity(CampaignModel(**row))
        except SQLAlchemyError as e:
            raise CampaignRepositoryError(f"Db error: {str(e)}")

    async def update(self, campaign: CampaignUpdateEntity) -> CampaignEntity:
        try:
            update_fields: List[str] = []
            params: Dict[str, Any] = {
                "id": campaign.id,
                "advertiser_id": campaign.advertiser_id,
                "cost_per_impression": campaign.cost_per_impression,
                "cost_per_click": campaign.cost_per_click,
                "ad_title": campaign.ad_title,
                "ad_text": campaign.ad_text,
            }

            update_fields.extend(
                [
                    "cost_per_impression = :cost_per_impression",
                    "cost_per_click = :cost_per_click",
                    "ad_title = :ad_title",
                    "ad_text = :ad_text",
                ]
            )

            if hasattr(campaign, "gender"):
                update_fields.append("gender = :gender")
                params["gender"] = campaign.gender.value if campaign.gender else None

            if hasattr(campaign, "age_from"):
                update_fields.append("age_from = :age_from")
                params["age_from"] = campaign.age_from

            if hasattr(campaign, "age_to"):
                update_fields.append("age_to = :age_to")
                params["age_to"] = campaign.age_to

            if hasattr(campaign, "location"):
                update_fields.append("location = :location")
                params["location"] = campaign.location

            update_fields.append("updated_at = CURRENT_TIMESTAMP")

            query = text(f"""
                UPDATE campaigns 
                SET {", ".join(update_fields)}
                WHERE id = :id AND advertiser_id = :advertiser_id
                RETURNING *;
            """)
            result = await self._session.execute(query, params)
            row = result.mappings().first()
            if not row:
                raise CampaignNotFoundException(
                    f"Рекламодатель с id {campaign.id} не найден"
                )
            await self._session.flush()
            return self._mapper.from_model_to_entity(CampaignModel(**row))
        except SQLAlchemyError as e:
            raise CampaignRepositoryError(f"Db error: {str(e)}")

    async def delete(self, advertiser_id: UUID, campaign_id: UUID) -> None:
        try:
            query = text("""
                DELETE FROM campaigns 
                WHERE id = :campaign_id AND advertiser_id = :advertiser_id;
            """)
            await self._session.execute(
                query,
                {
                    "campaign_id": campaign_id,
                    "advertiser_id": advertiser_id,
                },
            )
        except SQLAlchemyError as e:
            raise CampaignRepositoryError(f"Db error: {str(e)}")

    async def update_image_url(
        self, campaign_id: UUID, image_url: Optional[str]
    ) -> CampaignEntity:
        try:
            query = text("""
                UPDATE campaigns 
                SET image_url = :image_url,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
                RETURNING *;
            """)
            result = await self._session.execute(
                query,
                {
                    "id": campaign_id,
                    "image_url": image_url,
                },
            )
            row = result.mappings().first()
            if not row:
                raise CampaignNotFoundException(
                    f"Рекламодатель с id {campaign_id} не найден"
                )
            await self._session.flush()
            return self._mapper.from_model_to_entity(CampaignModel(**row))
        except SQLAlchemyError as e:
            raise CampaignRepositoryError(f"Db error: {str(e)}")

    async def get_targeted_campaigns(self, client_id: UUID) -> List[CampaignEntity]:
        try:
            current_day = await self._time_repository.get_current_date()

            client_query = select(ClientModel).where(ClientModel.id == client_id)
            result_client = await self._session.execute(client_query)
            client = result_client.scalar_one_or_none()
            if not client:
                raise CampaignRepositoryError(f"Client with id {client_id} not found")

            client_age = client.age
            client_location = client.location
            client_gender = client.gender

            events_subq = (
                select(
                    UniqueEventModel.campaign_id.label("campaign_id"),
                    func.count(
                        case((UniqueEventModel.event_type == "impression", 1))
                    ).label("impressions_count"),
                    func.count(case((UniqueEventModel.event_type == "click", 1))).label(
                        "clicks_count"
                    ),
                )
                .group_by(UniqueEventModel.campaign_id)
                .subquery()
            )

            query = (
                select(CampaignModel)
                .outerjoin(events_subq, events_subq.c.campaign_id == CampaignModel.id)
                .where(
                    CampaignModel.start_date <= current_day,
                    CampaignModel.end_date >= current_day,
                    or_(
                        CampaignModel.location.is_(None),
                        CampaignModel.location == client_location,
                    ),
                    or_(
                        CampaignModel.age_from.is_(None),
                        CampaignModel.age_from <= client_age,
                    ),
                    or_(
                        CampaignModel.age_to.is_(None),
                        CampaignModel.age_to >= client_age,
                    ),
                    or_(
                        CampaignModel.gender.is_(None),
                        CampaignModel.gender == client_gender,
                        CampaignModel.gender == TargetingGender.ALL.value,
                    ),
                    func.coalesce(events_subq.c.impressions_count, 0)
                    < CampaignModel.impressions_limit,
                    func.coalesce(events_subq.c.clicks_count, 0)
                    < CampaignModel.clicks_limit,
                )
            )

            result = await self._session.execute(query)
            campaigns = result.scalars().all()
            return [
                self._mapper.from_model_to_entity(campaign) for campaign in campaigns
            ]
        except SQLAlchemyError as e:
            raise CampaignRepositoryError(f"Db error: {str(e)}")
