from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from src.application.ai.dtos import (
    AdvertisementGenerationResponse,
)
from src.common.depends import get_uow
from src.core.uow import AbstractUow
from src.domain.ai.interfaces import (
    GenerateAdUseCaseProtocol,
    GenerateImageUseCaseProtocol,
)

from .dependencies import (
    get_generate_ad_use_case,
    get_generate_image_use_case,
)

router = APIRouter()


@router.get("/generate-ad", tags=["AI"])
async def generate_ad(
    advertiser_id: UUID,
    ad_title: str,
    uow: AbstractUow = Depends(get_uow),
    usecase: GenerateAdUseCaseProtocol = Depends(get_generate_ad_use_case),
) -> AdvertisementGenerationResponse:
    """
    Генерация рекламного объявления
    """
    async with uow:
        return await usecase.execute(advertiser_id=advertiser_id, ad_title=ad_title)


@router.get("/generate-image", tags=["AI"])
async def generate_image(
    campaign_id: UUID,
    uow: AbstractUow = Depends(get_uow),
    usecase: GenerateImageUseCaseProtocol = Depends(get_generate_image_use_case),
) -> FileResponse:
    """
    Генерация изображения
    """
    async with uow:
        return await usecase.execute(campaign_id=campaign_id)
