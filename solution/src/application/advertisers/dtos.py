from uuid import UUID

from pydantic import BaseModel, Field


class GetAdvertiserByIdSchema(BaseModel):
    advertiser_id: UUID = Field(
        ..., description="Уникальный идентификатор рекламодателя (UUID)."
    )
    name: str = Field(..., description="Название рекламодателя.")


class AdvertiserUpsertSchema(BaseModel):
    advertiser_id: UUID = Field(..., description="UUID рекламодателя.")
    name: str


class MLScoreSchema(BaseModel):
    client_id: UUID = Field(
        ..., description="UUID клиента для которого рассчитывается ML скор."
    )
    advertiser_id: UUID = Field(
        ..., description="UUID рекламодателя для которого рассчитывается ML скор."
    )
    score: int = Field(
        ...,
        description="Целочисленное значение ML скора; чем больше – тем выше релевантность.",
    )
