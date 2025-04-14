from src.application.ads.dtos import AdsGetResponse
from src.domain.ads.entities import AdEntity
from src.domain.campaigns.entities import CampaignEntity


class AdsMapper:
    def from_model_to_entity(self, model: CampaignEntity) -> AdEntity:
        return AdEntity(
            id=model.id,
            ad_title=model.ad_title,
            ad_text=model.ad_text,
            advertiser_id=model.advertiser_id,
            image_url=model.image_url or "",
        )

    def from_entity_to_schema(self, entity: AdEntity) -> AdsGetResponse:
        return AdsGetResponse(
            ad_id=entity.id,
            ad_title=entity.ad_title,
            ad_text=entity.ad_text,
            advertiser_id=entity.advertiser_id,
            image_url=entity.image_url,
        )
