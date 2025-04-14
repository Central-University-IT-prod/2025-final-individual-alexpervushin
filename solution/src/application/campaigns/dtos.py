from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from src.common.enums import TargetingGender


class TargetingSchema(BaseModel):
    gender: Optional[TargetingGender] = Field(
        None, description="Пол аудитории для показа объявления (MALE, FEMALE или ALL)."
    )
    age_from: Optional[int] = Field(
        None,
        description="Минимальный возраст аудитории (включительно) для показа объявления.",
        ge=0,
    )
    age_to: Optional[int] = Field(
        None,
        description="Максимальный возраст аудитории (включительно) для показа объявления.",
        ge=0,
    )
    location: Optional[str] = Field(
        None, description="Локация аудитории, для которой будет показано объявление."
    )

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: Optional[str]) -> Optional[str]:
        if v == "":
            raise ValueError("Локация не может быть пустой строкой")
        return v

    @field_validator("age_to")
    @classmethod
    def validate_age_range(cls, v: Optional[int], info: Any) -> Optional[int]:
        age_from = info.data.get("age_from")
        if age_from is not None and v is not None and v < age_from:
            raise ValueError("age_to должен быть больше или равен age_from")
        return v


class CampaignCreateRequest(BaseModel):
    impressions_limit: int = Field(
        ...,
        description="Задаёт лимит показов для рекламного объявления.",
        gt=0,
    )
    clicks_limit: int = Field(
        ...,
        description="Задаёт лимит переходов для рекламного объявления.",
        gt=0,
    )
    cost_per_impression: float = Field(
        ...,
        description="Стоимость одного показа объявления.",
        gt=0,
    )
    cost_per_click: float = Field(
        ...,
        description="Стоимость одного перехода (клика) по объявлению.",
        gt=0,
    )
    ad_title: str = Field(..., description="Название рекламного объявления.")
    ad_text: str = Field(..., description="Текст рекламного объявления.")
    start_date: int = Field(
        ..., description="День начала показа рекламного объявления (включительно)."
    )
    end_date: int = Field(
        ..., description="День окончания показа рекламного объявления (включительно)."
    )
    targeting: Optional[TargetingSchema] = Field(
        None, description="Параметры таргетирования для рекламной кампании."
    )

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: int, info: Any) -> int:
        start_date = info.data.get("start_date")
        if start_date is not None and v < start_date:
            raise ValueError("end_date должен быть больше или равен start_date")
        return v

    @field_validator("clicks_limit")
    @classmethod
    def validate_clicks_limit(cls, v: int, info: Any) -> int:
        impressions_limit = info.data.get("impressions_limit")
        if impressions_limit is not None and v > impressions_limit:
            raise ValueError(
                "clicks_limit должен быть меньше или равен impressions_limit"
            )
        return v


class CampaignUpdateRequest(BaseModel):
    cost_per_impression: float = Field(
        ...,
        description="Новая стоимость одного показа объявления.",
        gt=0,
    )
    cost_per_click: float = Field(
        ...,
        description="Новая стоимость одного перехода (клика) по объявлению.",
        gt=0,
    )
    ad_title: str = Field(..., description="Новое название рекламного объявления.")
    ad_text: str = Field(..., description="Новый текст рекламного объявления.")
    targeting: Optional[TargetingSchema] = Field(
        None, description="Новые параметры таргетирования для рекламной кампании."
    )


class CampaignResponse(BaseModel):
    campaign_id: UUID = Field(
        ..., description="Уникальный идентификатор рекламной кампании (UUID)."
    )
    advertiser_id: UUID = Field(
        ..., description="UUID рекламодателя, которому принадлежит кампания."
    )
    impressions_limit: int = Field(
        ...,
        description="Лимит показов рекламного объявления (фиксируется до старта кампании).",
    )
    clicks_limit: int = Field(
        ...,
        description="Лимит переходов (кликов) по рекламному объявлению (фиксируется до старта кампании).",
    )
    cost_per_impression: float = Field(
        ..., description="Стоимость одного показа рекламного объявления."
    )
    cost_per_click: float = Field(
        ..., description="Стоимость одного перехода (клика) по рекламному объявлению."
    )
    ad_title: str = Field(..., description="Название рекламного объявления.")
    ad_text: str = Field(..., description="Текст рекламного объявления.")
    start_date: int = Field(
        ..., description="День старта показа рекламного объявления (включительно)."
    )
    end_date: int = Field(
        ..., description="День окончания показа рекламного объявления (включительно)."
    )
    targeting: TargetingSchema
    image_url: Optional[str] = Field(
        None,
        description="URL изображения рекламной кампании.",
    )


class ImageUploadResponse(BaseModel):
    image_url: str = Field(..., description="URL загруженного изображения.")
