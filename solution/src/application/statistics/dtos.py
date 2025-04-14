from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class StatsResponse(BaseModel):
    impressions_count: int = Field(
        ..., description="Общее количество уникальных показов рекламного объявления."
    )
    clicks_count: int = Field(
        ...,
        description="Общее количество уникальных переходов (кликов) по рекламному объявлению.",
    )
    conversion: float = Field(
        ...,
        description="Коэффициент конверсии, вычисляемый как (clicks_count / impressions_count * 100) в процентах.",
    )
    spent_impressions: float = Field(
        ..., description="Сумма денег, потраченная на показы рекламного объявления."
    )
    spent_clicks: float = Field(
        ...,
        description="Сумма денег, потраченная на переходы (клики) по рекламному объявлению.",
    )
    spent_total: float = Field(
        ..., description="Общая сумма денег, потраченная на кампанию (показы и клики)."
    )


class DailyStatsResponse(BaseModel):
    impressions_count: int = Field(
        ..., description="Общее количество уникальных показов рекламного объявления."
    )
    clicks_count: int = Field(
        ...,
        description="Общее количество уникальных переходов (кликов) по рекламному объявлению.",
    )
    conversion: float = Field(
        ...,
        description="Коэффициент конверсии, вычисляемый как (clicks_count / impressions_count * 100) в процентах.",
    )
    spent_impressions: float = Field(
        ..., description="Сумма денег, потраченная на показы рекламного объявления."
    )
    spent_clicks: float = Field(
        ...,
        description="Сумма денег, потраченная на переходы (клики) по рекламному объявлению.",
    )
    spent_total: float = Field(
        ..., description="Общая сумма денег, потраченная на кампанию (показы и клики)."
    )
    date: int = Field(..., description="День, за который была собрана статистика.")


class ClientStatsResponse(BaseModel):
    total_clients: int = Field(..., description="Общее количество клиентов.")
    demographics_distribution: dict[str, dict[str, int]] = Field(
        ...,
        description="Распределение клиентов по полу и возрастным группам. "
        "Пример: {'male': {'18-24': 50, '25-34': 100}, 'female': {'18-24': 75, '25-34': 150}}.",
    )
    top_locations: list[dict[str, Any]] = Field(
        ...,
        description="Топ локаций с количеством клиентов. Пример: [{'location': 'Moscow', 'count': 500}, ...].",
    )
    average_age: float = Field(..., description="Средний возраст клиентов.")


class CampaignFeedbackItem(BaseModel):
    client_id: UUID = Field(..., description="UUID клиента, оставившего отзыв")
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")
    comment: Optional[str] = Field(None, description="Комментарий к отзыву")
    created_at: datetime = Field(..., description="Дата создания отзыва")


class CampaignFeedbackResponse(BaseModel):
    average_rating: float = Field(..., description="Средний рейтинг кампании")
    total_ratings: int = Field(..., description="Общее количество оценок")
    feedbacks: list[CampaignFeedbackItem] = Field(..., description="Список отзывов")
