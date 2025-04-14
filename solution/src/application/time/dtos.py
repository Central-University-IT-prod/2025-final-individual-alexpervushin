from typing import Optional

from pydantic import BaseModel, Field


class TimeAdvancePostRequest(BaseModel):
    current_date: Optional[int] = Field(
        None, description="Текущий день (целое неотрицательное число)", ge=0
    )


class TimeAdvancePostResponse(BaseModel):
    current_date: Optional[int] = Field(None, description="Текущий день (целое число).")


class GetCurrentDateResponse(BaseModel):
    current_date: Optional[int] = Field(None, description="Текущий день (целое число).")
