from typing import List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    HTTPException,
    Path,
    Query,
    UploadFile,
)
from src.application.campaigns.dtos import (
    CampaignCreateRequest,
    CampaignResponse,
    CampaignUpdateRequest,
    ImageUploadResponse,
)
from src.common.depends import get_uow
from src.core.uow import AbstractUow
from src.domain.advertisers.exceptions import AdvertiserNotFoundException
from src.domain.campaigns.exceptions import (
    CampaignForbiddenError,
    CampaignImageUploadError,
    CampaignModerationError,
    CampaignNotFoundException,
    CampaignRepositoryError,
)
from src.domain.campaigns.interfaces import (
    CreateCampaignFromYandexUseCaseProtocol,
    CreateCampaignUseCaseProtocol,
    DeleteCampaignImageUseCaseProtocol,
    DeleteCampaignUseCaseProtocol,
    GetCampaignByIdUseCaseProtocol,
    GetCampaignsFromYandexUseCaseProtocol,
    GetCampaignsUseCaseProtocol,
    UpdateCampaignUseCaseProtocol,
    UploadCampaignImageUseCaseProtocol,
)

from .dependencies import (
    get_create_campaign_from_yandex_use_case,
    get_create_campaign_use_case,
    get_delete_campaign_image_use_case,
    get_delete_campaign_use_case,
    get_get_campaign_by_id_use_case,
    get_get_campaigns_from_yandex_use_case,
    get_get_campaigns_use_case,
    get_update_campaign_use_case,
    get_upload_campaign_image_use_case,
)

router = APIRouter()


@router.post(
    "/advertisers/{advertiserId}/campaigns",
    tags=["Campaigns"],
    status_code=201,
)
async def create_campaign(
    advertiser_id: UUID = Path(..., alias="advertiserId"),
    data: CampaignCreateRequest = Body(
        ...,
    ),
    uow: AbstractUow = Depends(get_uow),
    usecase: CreateCampaignUseCaseProtocol = Depends(get_create_campaign_use_case),
) -> Optional[CampaignResponse]:
    """
    Создание рекламной кампании
    """
    try:
        async with uow:
            return await usecase.execute(advertiser_id=advertiser_id, data=data)
    except AdvertiserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CampaignModerationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CampaignRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/advertisers/{advertiserId}/campaigns",
    tags=["Campaigns"],
)
async def list_campaigns(
    advertiser_id: UUID = Path(..., alias="advertiserId"),
    size: Optional[int] = Query(None),
    page: Optional[int] = Query(None),
    uow: AbstractUow = Depends(get_uow),
    usecase: GetCampaignsUseCaseProtocol = Depends(get_get_campaigns_use_case),
) -> List[CampaignResponse]:
    """
    Получение рекламных кампаний рекламодателя c пагинацией
    """
    try:
        async with uow:
            return await usecase.execute(
                advertiser_id=advertiser_id, size=size, page=page
            )
    except AdvertiserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CampaignRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/advertisers/{advertiserId}/campaigns/{campaignId}",
    tags=["Campaigns"],
)
async def get_advertisers_advertiser_id_campaigns_campaign_id(
    advertiser_id: UUID = Path(..., alias="advertiserId"),
    campaign_id: UUID = Path(..., alias="campaignId"),
    uow: AbstractUow = Depends(get_uow),
    usecase: GetCampaignByIdUseCaseProtocol = Depends(get_get_campaign_by_id_use_case),
) -> CampaignResponse:
    """
    Получение кампании по ID
    """
    try:
        async with uow:
            return await usecase.execute(
                advertiser_id=advertiser_id, campaign_id=campaign_id
            )
    except AdvertiserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CampaignNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CampaignForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except CampaignRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/advertisers/{advertiserId}/campaigns/{campaignId}",
    tags=["Campaigns"],
)
async def update_campaign(
    advertiser_id: UUID = Path(..., alias="advertiserId"),
    campaign_id: UUID = Path(..., alias="campaignId"),
    data: CampaignUpdateRequest = Body(...),
    uow: AbstractUow = Depends(get_uow),
    usecase: UpdateCampaignUseCaseProtocol = Depends(get_update_campaign_use_case),
) -> CampaignResponse:
    """
    Обновление рекламной кампании
    """
    try:
        async with uow:
            return await usecase.execute(
                advertiser_id=advertiser_id, campaign_id=campaign_id, data=data
            )
    except AdvertiserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CampaignNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CampaignModerationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CampaignForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except CampaignRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/advertisers/{advertiserId}/campaigns/{campaignId}",
    tags=["Campaigns"],
    status_code=204,
)
async def delete_campaign(
    advertiser_id: UUID = Path(..., alias="advertiserId"),
    campaign_id: UUID = Path(..., alias="campaignId"),
    uow: AbstractUow = Depends(get_uow),
    usecase: DeleteCampaignUseCaseProtocol = Depends(get_delete_campaign_use_case),
) -> None:
    """
    Удаление рекламной кампании
    """
    try:
        async with uow:
            await usecase.execute(advertiser_id=advertiser_id, campaign_id=campaign_id)
    except AdvertiserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CampaignNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CampaignForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except CampaignRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/advertisers/{advertiserId}/campaigns/{campaignId}/image",
    tags=["Campaigns"],
)
async def upload_campaign_image(
    advertiser_id: UUID = Path(..., alias="advertiserId"),
    campaign_id: UUID = Path(..., alias="campaignId"),
    image: UploadFile = File(
        ...,
        description="Изображение рекламной кампании (jpeg, png, gif, webp)",
        media_type="image/*",
    ),
    uow: AbstractUow = Depends(get_uow),
    usecase: UploadCampaignImageUseCaseProtocol = Depends(
        get_upload_campaign_image_use_case
    ),
) -> ImageUploadResponse:
    """
    Загрузка или обновление изображения рекламной кампании
    """
    try:
        async with uow:
            return await usecase.execute(
                advertiser_id=advertiser_id, campaign_id=campaign_id, image=image
            )
    except AdvertiserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CampaignNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CampaignForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except CampaignImageUploadError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except CampaignRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/advertisers/{advertiserId}/campaigns/{campaignId}/image",
    tags=["Campaigns"],
    status_code=204,
)
async def delete_campaign_image(
    advertiser_id: UUID = Path(..., alias="advertiserId"),
    campaign_id: UUID = Path(..., alias="campaignId"),
    uow: AbstractUow = Depends(get_uow),
    usecase: DeleteCampaignImageUseCaseProtocol = Depends(
        get_delete_campaign_image_use_case
    ),
) -> None:
    """
    Удаление изображения рекламной кампании
    """
    try:
        async with uow:
            await usecase.execute(advertiser_id=advertiser_id, campaign_id=campaign_id)
    except AdvertiserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CampaignNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CampaignForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except CampaignRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/advertisers/{advertiserId}/yandex", tags=["Campaigns"])
async def get_campaigns_from_yandex(
    token: Optional[str] = None,
    advertiser_id: UUID = Path(..., alias="advertiserId"),
    uow: AbstractUow = Depends(get_uow),
    usecase: GetCampaignsFromYandexUseCaseProtocol = Depends(
        get_get_campaigns_from_yandex_use_case
    ),
) -> List[CampaignResponse]:
    """
    Получение рекламных кампаний из Яндекс.Директ
    """
    try:
        async with uow:
            return await usecase.execute(advertiser_id=advertiser_id, token=token)
    except AdvertiserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CampaignRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/advertisers/{advertiserId}/yandex", tags=["Campaigns"])
async def create_campaign_from_yandex(
    token: Optional[str] = None,
    advertiser_id: UUID = Path(..., alias="advertiserId"),
    uow: AbstractUow = Depends(get_uow),
    usecase: CreateCampaignFromYandexUseCaseProtocol = Depends(
        get_create_campaign_from_yandex_use_case
    ),
) -> List[CampaignResponse]:
    """
    Перенос рекламных кампаний из Яндекс.Директ в систему
    """
    try:
        async with uow:
            return await usecase.execute(advertiser_id=advertiser_id, token=token)
    except AdvertiserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CampaignNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CampaignRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))
