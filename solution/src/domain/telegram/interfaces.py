from typing import Protocol
from uuid import UUID

from src.domain.telegram.entities import TelegramUser


class TelegramUserRepositoryProtocol(Protocol):
    def get_user(self, telegram_id: int) -> TelegramUser: ...

    def create_user(self, telegram_id: int, advertiser_id: UUID) -> TelegramUser: ...
