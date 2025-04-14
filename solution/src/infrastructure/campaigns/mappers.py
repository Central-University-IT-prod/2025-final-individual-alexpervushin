import uuid

from src.application.campaigns.dtos import (
    CampaignCreateRequest,
    CampaignResponse,
    CampaignUpdateRequest,
    TargetingSchema,
)
from src.common.enums import TargetingGender
from src.domain.campaigns.entities import (
    CampaignEntity,
    CampaignUpdateEntity,
)
from src.infrastructure.campaigns.orm import CampaignModel


class CampaignsMapper:
    def from_create_schema_to_entity(
        self, schema: CampaignCreateRequest
    ) -> CampaignEntity:
        targeting = schema.targeting or TargetingSchema(
            gender=None, age_from=None, age_to=None, location=None
        )
        return CampaignEntity(
            id=uuid.uuid4(),
            advertiser_id=uuid.uuid4(),
            impressions_limit=schema.impressions_limit,
            clicks_limit=schema.clicks_limit,
            cost_per_impression=schema.cost_per_impression,
            cost_per_click=schema.cost_per_click,
            ad_title=schema.ad_title,
            ad_text=schema.ad_text,
            start_date=schema.start_date,
            end_date=schema.end_date,
            image_url=None,
            gender=targeting.gender,
            age_from=targeting.age_from,
            age_to=targeting.age_to,
            location=targeting.location,
        )

    def from_update_schema_to_entity(
        self, schema: CampaignUpdateRequest
    ) -> CampaignUpdateEntity:
        targeting = schema.targeting or TargetingSchema(
            gender=None, age_from=None, age_to=None, location=None
        )
        return CampaignUpdateEntity(
            id=uuid.uuid4(),
            advertiser_id=uuid.uuid4(),
            image_url=None,
            cost_per_impression=schema.cost_per_impression,
            cost_per_click=schema.cost_per_click,
            ad_title=schema.ad_title,
            ad_text=schema.ad_text,
            gender=targeting.gender,
            age_from=targeting.age_from,
            age_to=targeting.age_to,
            location=targeting.location,
        )

    def from_entity_to_schema(self, entity: CampaignEntity) -> CampaignResponse:
        return CampaignResponse(
            campaign_id=entity.id,
            advertiser_id=entity.advertiser_id,
            impressions_limit=entity.impressions_limit,
            clicks_limit=entity.clicks_limit,
            cost_per_impression=entity.cost_per_impression,
            cost_per_click=entity.cost_per_click,
            ad_title=entity.ad_title,
            ad_text=entity.ad_text,
            start_date=entity.start_date,
            end_date=entity.end_date,
            image_url=entity.image_url,
            targeting=TargetingSchema(
                gender=entity.gender,
                age_from=entity.age_from,
                age_to=entity.age_to,
                location=entity.location,
            ),
        )

    def from_entity_to_model(self, entity: CampaignEntity) -> CampaignModel:
        return CampaignModel(
            id=entity.id,
            advertiser_id=entity.advertiser_id,
            impressions_limit=entity.impressions_limit,
            clicks_limit=entity.clicks_limit,
            cost_per_impression=entity.cost_per_impression,
            cost_per_click=entity.cost_per_click,
            ad_title=entity.ad_title,
            ad_text=entity.ad_text,
            start_date=entity.start_date,
            end_date=entity.end_date,
            gender=entity.gender,
            age_from=entity.age_from,
            age_to=entity.age_to,
            location=entity.location,
            image_url=entity.image_url,
        )

    def from_model_to_entity(self, model: CampaignModel) -> CampaignEntity:
        return CampaignEntity(
            id=model.id,
            advertiser_id=model.advertiser_id,
            impressions_limit=model.impressions_limit,
            clicks_limit=model.clicks_limit,
            cost_per_impression=model.cost_per_impression,
            cost_per_click=model.cost_per_click,
            ad_title=model.ad_title,
            ad_text=model.ad_text,
            start_date=model.start_date,
            end_date=model.end_date,
            gender=TargetingGender(model.gender) if model.gender else None,
            age_from=model.age_from,
            age_to=model.age_to,
            location=model.location,
            image_url=model.image_url,
        )
