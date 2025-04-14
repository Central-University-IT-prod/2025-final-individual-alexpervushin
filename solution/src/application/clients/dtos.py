from uuid import UUID

from pydantic import BaseModel, Field
from src.common.enums import Gender, TargetingGender


class ClientSchema(BaseModel):
    client_id: UUID = Field(..., description="Уникальный идентификатор клиента (UUID).")
    login: str = Field(..., description="Логин клиента в системе.")
    age: int = Field(..., description="Возраст клиента.", gt=0)
    location: str = Field(..., description="Локация клиента (город, регион или район).")
    gender: Gender = Field(..., description="Пол клиента (MALE или FEMALE).")


class ClientUpsertSchema(BaseModel):
    client_id: UUID
    login: str
    age: int = Field(..., gt=0)
    location: str
    gender: TargetingGender
