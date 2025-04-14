from dataclasses import dataclass
from uuid import UUID

from src.core.entities.base_entity import BaseEntity


@dataclass
class TelegramUser(BaseEntity):
    telegram_id: int
    advertiser_id: UUID
