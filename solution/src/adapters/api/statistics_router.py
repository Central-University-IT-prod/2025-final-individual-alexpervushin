from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path
from src.application.statistics.dtos import (
    CampaignFeedbackResponse,
    ClientStatsResponse,
    DailyStatsResponse,
    StatsResponse,
)
from src.common.depends import get_uow
from src.core.uow import AbstractUow
from src.domain.advertisers.exceptions import AdvertiserNotFoundException
from src.domain.campaigns.exceptions import CampaignNotFoundException
from src.domain.statistics.exceptions import (
    StatisticsRepositoryError,
)
from src.domain.statistics.interfaces import (
    GetAdvertiserCampaignsStatsUseCaseProtocol,
    GetAdvertiserDailyStatsUseCaseProtocol,
    GetCampaignDailyStatsUseCaseProtocol,
    GetCampaignFeedbackStatsUseCaseProtocol,
    GetCampaignStatsUseCaseProtocol,
    GetClientsStatsUseCaseProtocol,
)

from .dependencies import (
    get_get_advertiser_campaigns_stats_use_case,
    get_get_advertiser_daily_stats_use_case,
    get_get_campaign_daily_stats_use_case,
    get_get_campaign_feedback_stats_use_case,
    get_get_campaign_stats_use_case,
    get_get_clients_stats_use_case,
)

router = APIRouter()


@router.get("/stats/campaigns/{campaignId}", tags=["Statistics"])
async def get_campaign_stats(
    campaign_id: UUID = Path(..., alias="campaignId"),
    uow: AbstractUow = Depends(get_uow),
    usecase: GetCampaignStatsUseCaseProtocol = Depends(get_get_campaign_stats_use_case),
) -> StatsResponse:
    """
    Получение статистики по рекламной кампании
    """
    try:
        async with uow:
            return await usecase.execute(campaign_id)
    except CampaignNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except StatisticsRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats/advertisers/{advertiserId}/campaigns",
    tags=["Statistics"],
)
async def get_advertiser_campaigns_stats(
    advertiser_id: UUID = Path(..., alias="advertiserId"),
    uow: AbstractUow = Depends(get_uow),
    usecase: GetAdvertiserCampaignsStatsUseCaseProtocol = Depends(
        get_get_advertiser_campaigns_stats_use_case
    ),
) -> StatsResponse:
    """
    Получение агрегированной статистики по всем кампаниям рекламодателя
    """
    try:
        async with uow:
            return await usecase.execute(advertiser_id)
    except AdvertiserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except StatisticsRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats/campaigns/{campaignId}/daily",
    tags=["Statistics"],
)
async def get_campaign_daily_stats(
    campaign_id: UUID = Path(..., alias="campaignId"),
    uow: AbstractUow = Depends(get_uow),
    usecase: GetCampaignDailyStatsUseCaseProtocol = Depends(
        get_get_campaign_daily_stats_use_case
    ),
) -> List[DailyStatsResponse]:
    """
    Получение ежедневной статистики по рекламной кампании
    """
    try:
        async with uow:
            return await usecase.execute(campaign_id)
    except CampaignNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except StatisticsRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats/advertisers/{advertiserId}/campaigns/daily",
    tags=["Statistics"],
)
async def get_advertiser_daily_stats(
    advertiser_id: UUID = Path(..., alias="advertiserId"),
    uow: AbstractUow = Depends(get_uow),
    usecase: GetAdvertiserDailyStatsUseCaseProtocol = Depends(
        get_get_advertiser_daily_stats_use_case
    ),
) -> List[DailyStatsResponse]:
    """
    Получение ежедневной агрегированной статистики по всем кампаниям рекламодателя
    """
    try:
        async with uow:
            return await usecase.execute(advertiser_id)
    except AdvertiserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except StatisticsRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats/clients",
    tags=["Statistics"],
)
async def get_clients_stats(
    uow: AbstractUow = Depends(get_uow),
    usecase: GetClientsStatsUseCaseProtocol = Depends(get_get_clients_stats_use_case),
) -> ClientStatsResponse:
    """
    Получение статистики по клиентам
    """
    try:
        async with uow:
            return await usecase.execute()
    except StatisticsRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats/campaigns/{campaignId}/feedback",
    tags=["Statistics"],
)
async def get_campaign_feedback_stats(
    campaign_id: UUID = Path(..., alias="campaignId"),
    uow: AbstractUow = Depends(get_uow),
    usecase: GetCampaignFeedbackStatsUseCaseProtocol = Depends(
        get_get_campaign_feedback_stats_use_case
    ),
) -> CampaignFeedbackResponse:
    """
    Получение статистики по отзывам о рекламной кампании
    """
    try:
        async with uow:
            return await usecase.execute(campaign_id)
    except CampaignNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except StatisticsRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))
