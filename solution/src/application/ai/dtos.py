from typing import TypedDict

from pydantic import BaseModel, Field


class AdvertisementGenerationResponse(BaseModel):
    generated_text: str = Field(
        ..., description="Сгенерированный текст рекламного объявления"
    )


class GeneratedAdResponse(TypedDict):
    generated_text: str


class ImageDescriptionResponse(TypedDict):
    image_description: str


class ModerationResponse(TypedDict):
    profanity: bool
    offensive: bool
    inappropriate: bool
