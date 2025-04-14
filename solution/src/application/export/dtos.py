from uuid import UUID

from pydantic import BaseModel, Field


class BaseExportSchema(BaseModel):
    created_at: int = Field(..., description="Дата создания записи (timestamp)")
    updated_at: int = Field(
        ..., description="Дата последнего обновления записи (timestamp)"
    )


class UniqueEventExportSchema(BaseExportSchema):
    client_id: UUID = Field(..., description="UUID клиента")
    event_type: str = Field(..., description="Тип события")
    rating: int | None = Field(None, description="Оценка")
    comment: str | None = Field(None, description="Комментарий")


class StatisticsExportSchema(BaseExportSchema):
    date: int = Field(..., description="Дата статистики (timestamp)")
    impressions_count: int = Field(..., description="Количество показов")
    clicks_count: int = Field(..., description="Количество кликов")
    conversion: float = Field(..., description="Конверсия")
    spent_impressions: float = Field(..., description="Затраты на показы")
    spent_clicks: float = Field(..., description="Затраты на клики")
    spent_total: float = Field(..., description="Общие затраты")


class CampaignExportSchema(BaseExportSchema):
    campaign_id: UUID = Field(..., description="UUID кампании")
    image_url: str | None = Field(None, description="URL изображения кампании")
    impressions_limit: int = Field(..., description="Лимит показов")
    clicks_limit: int = Field(..., description="Лимит кликов")
    cost_per_impression: float = Field(..., description="Стоимость за показ")
    cost_per_click: float = Field(..., description="Стоимость за клик")
    ad_title: str = Field(..., description="Заголовок объявления")
    ad_text: str = Field(..., description="Текст объявления")
    start_date: int = Field(..., description="Дата начала кампании (timestamp)")
    end_date: int = Field(..., description="Дата окончания кампании (timestamp)")
    gender: str | None = Field(None, description="Целевой пол")
    age_from: int | None = Field(None, description="Минимальный возраст")
    age_to: int | None = Field(None, description="Максимальный возраст")
    location: str | None = Field(None, description="Целевая локация")
    statistics: list[StatisticsExportSchema] = Field(
        default_factory=list, description="Статистика кампании"
    )
    unique_events: list[UniqueEventExportSchema] = Field(
        default_factory=list, description="Уникальные события кампании"
    )


class MLScoreExportSchema(BaseExportSchema):
    client_id: UUID = Field(..., description="UUID клиента")
    score: int = Field(..., description="ML скор")


class TelegramUserExportSchema(BaseExportSchema):
    telegram_id: int = Field(..., description="Telegram ID пользователя")


class AdvertiserExportSchema(BaseExportSchema):
    advertiser_id: UUID = Field(..., description="UUID рекламодателя")
    name: str = Field(..., description="Название рекламодателя")
    campaigns: list[CampaignExportSchema] = Field(
        default_factory=list, description="Список кампаний"
    )
    ml_scores: list[MLScoreExportSchema] = Field(
        default_factory=list, description="Список ML скоров"
    )
    telegram_users: list[TelegramUserExportSchema] = Field(
        default_factory=list, description="Список привязанных Telegram аккаунтов"
    )
