from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path
from src.application.advertisers.dtos import (
    GetAdvertiserByIdSchema,
    MLScoreSchema,
)
from src.core.uow import AbstractUow
from src.domain.advertisers.exceptions import (
    AdvertiserNotFoundException,
    AdvertiserRepositoryError,
    MLScoreRepositoryError,
)
from src.domain.advertisers.interfaces import (
    GetAdvertiserByIdUseCaseProtocol,
    UpsertAdvertisersUseCaseProtocol,
    UpsertMLScoreUseCaseProtocol,
)
from src.domain.clients.exceptions import ClientNotFoundException

from .dependencies import (
    get_get_advertiser_by_id_use_case,
    get_uow,
    get_upsert_advertisers_use_case,
    get_upsert_ml_score_use_case,
)

router = APIRouter()


@router.get("/advertisers/{advertiserId}", tags=["Advertisers"])
async def get_advertiser_by_id(
    advertiser_id: UUID = Path(..., alias="advertiserId"),
    uow: AbstractUow = Depends(get_uow),
    usecase: GetAdvertiserByIdUseCaseProtocol = Depends(
        get_get_advertiser_by_id_use_case
    ),
) -> GetAdvertiserByIdSchema:
    """
    Получение рекламодателя по ID
    """
    try:
        async with uow:
            return await usecase.execute(advertiser_id=advertiser_id)
    except AdvertiserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AdvertiserRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/advertisers/bulk", tags=["Advertisers"], status_code=201)
async def upsert_advertisers(
    data: List[GetAdvertiserByIdSchema],
    uow: AbstractUow = Depends(get_uow),
    usecase: UpsertAdvertisersUseCaseProtocol = Depends(
        get_upsert_advertisers_use_case
    ),
) -> List[GetAdvertiserByIdSchema]:
    """
    Создание или обновление рекламодателей
    """
    try:
        async with uow:
            return await usecase.execute(data=data)
    except AdvertiserRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ml-scores", tags=["Advertisers"])
async def upsert_ml_score(
    data: MLScoreSchema,
    uow: AbstractUow = Depends(get_uow),
    usecase: UpsertMLScoreUseCaseProtocol = Depends(get_upsert_ml_score_use_case),
) -> None:
    """
    Создание или обновление ML скора
    """
    try:
        async with uow:
            await usecase.execute(data=data)
    except AdvertiserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ClientNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MLScoreRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except AdvertiserRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))
