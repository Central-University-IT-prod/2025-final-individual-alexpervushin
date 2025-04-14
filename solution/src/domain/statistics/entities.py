from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.core.entities.base_entity import BaseEntity


@dataclass
class StatisticsEntity(BaseEntity):
    campaign_id: UUID
    date: int
    impressions_count: int
    clicks_count: int
    conversion: float
    spent_impressions: float
    spent_clicks: float
    spent_total: float


@dataclass
class FeedbackEntity(BaseEntity):
    client_id: UUID
    campaign_id: UUID
    rating: int
    comment: Optional[str]
    created_at: datetime
