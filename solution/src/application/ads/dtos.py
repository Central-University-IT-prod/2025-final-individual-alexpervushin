from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AdsGetResponse(BaseModel):
    ad_id: UUID = Field(
        ...,
        description="Уникальный идентификатор рекламного объявления (всегда совпадает с id рекламной кампании).",
    )
    ad_title: str = Field(..., description="Название рекламного объявления.")
    ad_text: str = Field(
        ..., description="Текст рекламного объявления, который видит клиент."
    )
    image_url: str = Field(..., description="URL изображения рекламного объявления.")
    advertiser_id: UUID = Field(
        ..., description="UUID рекламодателя, которому принадлежит объявление."
    )


class AdsAdIdClickPostRequest(BaseModel):
    client_id: UUID = Field(
        ..., description="UUID клиента, совершившего клик по объявлению."
    )


class AdFeedbackRequest(BaseModel):
    ad_id: UUID
    client_id: UUID
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")
    comment: Optional[str] = Field(None, description="Комментарий")
