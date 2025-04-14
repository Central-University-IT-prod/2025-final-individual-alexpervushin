from dataclasses import dataclass
from uuid import UUID

from src.core.entities.base_entity import BaseEntity


@dataclass
class AdvertiserEntity(BaseEntity):
    name: str


@dataclass
class MLScoreEntity(BaseEntity):
    client_id: UUID
    advertiser_id: UUID
    score: int
