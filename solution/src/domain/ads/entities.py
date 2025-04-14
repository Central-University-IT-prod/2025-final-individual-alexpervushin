from dataclasses import dataclass
from uuid import UUID

from src.core.entities.base_entity import BaseEntity


@dataclass
class AdEntity(BaseEntity):
    ad_title: str
    ad_text: str
    advertiser_id: UUID
    image_url: str
