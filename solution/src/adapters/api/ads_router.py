from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from src.application.ads.dtos import (
    AdFeedbackRequest,
    AdsAdIdClickPostRequest,
    AdsGetResponse,
)
from src.common.depends import get_uow
from src.core.uow import AbstractUow
from src.domain.ads.exceptions import AdsNotFoundException
from src.domain.ads.interfaces import (
    GetAdForClientUseCaseProtocol,
    RecordAdClickUseCaseProtocol,
    SubmitAdFeedbackUseCaseProtocol,
)
from src.domain.campaigns.exceptions import CampaignNotFoundException
from src.domain.clients.exceptions import ClientNotFoundException
from src.domain.statistics.exceptions import (
    ClicksLimitReachedError,
    DuplicateClickError,
    NoImpressionError,
    StatisticsRepositoryError,
)

from .dependencies import (
    get_get_ad_for_client_use_case,
    get_record_ad_click_use_case,
    get_submit_ad_feedback_use_case,
)

router = APIRouter()


@router.get("/ads", tags=["Ads"])
async def get_ad_for_client(
    client_id: UUID,
    uow: AbstractUow = Depends(get_uow),
    usecase: GetAdForClientUseCaseProtocol = Depends(get_get_ad_for_client_use_case),
) -> AdsGetResponse:
    """
    Получение рекламного объявления для клиента
    """
    try:
        async with uow:
            return await usecase.execute(client_id=client_id)
    except ClientNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except AdsNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except StatisticsRepositoryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/ads/{adId}/click", tags=["Ads"])
async def record_ad_click(
    ad_id: UUID = Path(..., alias="adId"),
    data: AdsAdIdClickPostRequest = Body(...),
    uow: AbstractUow = Depends(get_uow),
    usecase: RecordAdClickUseCaseProtocol = Depends(get_record_ad_click_use_case),
) -> None:
    """
    Фиксация перехода по рекламному объявлению
    """
    try:
        async with uow:
            await usecase.execute(ad_id=ad_id, client_id=data.client_id)
    except CampaignNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ClientNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except (DuplicateClickError, NoImpressionError, ClicksLimitReachedError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except StatisticsRepositoryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/ads/feedback", tags=["Ads"])
async def submit_ad_feedback(
    feedback: AdFeedbackRequest,
    uow: AbstractUow = Depends(get_uow),
    usecase: SubmitAdFeedbackUseCaseProtocol = Depends(get_submit_ad_feedback_use_case),
) -> dict[str, str]:
    """
    Сохранение отзыва о рекламном объявлении
    """
    try:
        async with uow:
            await usecase.execute(
                ad_id=feedback.ad_id,
                client_id=feedback.client_id,
                rating=feedback.rating,
                comment=feedback.comment,
            )
            return {"message": "Отзыв успешно получен"}
    except CampaignNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ClientNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except StatisticsRepositoryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
