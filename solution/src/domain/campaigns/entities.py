from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.common.enums import TargetingGender
from src.core.entities.base_entity import BaseEntity


@dataclass
class CampaignEntity(BaseEntity):
    advertiser_id: UUID
    impressions_limit: int
    clicks_limit: int
    cost_per_impression: float
    cost_per_click: float
    ad_title: str
    ad_text: str
    start_date: int
    end_date: int
    image_url: Optional[str] = None
    gender: Optional[TargetingGender] = None
    age_from: Optional[int] = None
    age_to: Optional[int] = None
    location: Optional[str] = None


@dataclass
class CampaignUpdateEntity(BaseEntity):
    advertiser_id: UUID
    cost_per_impression: float
    cost_per_click: float
    ad_title: str
    ad_text: str
    gender: Optional[TargetingGender] = None
    age_from: Optional[int] = None
    age_to: Optional[int] = None
    location: Optional[str] = None
    image_url: Optional[str] = None
