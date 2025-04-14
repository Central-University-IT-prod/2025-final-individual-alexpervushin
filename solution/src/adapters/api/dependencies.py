import redis.asyncio as redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.ads.use_cases import (
    GetAdForClientUseCase,
    RecordAdClickUseCase,
    SubmitAdFeedbackUseCase,
)
from src.application.advertisers.use_cases import (
    GetAdvertiserByIdUseCase,
    UpsertAdvertisersUseCase,
    UpsertMLScoreUseCase,
)
from src.application.ai.use_cases import (
    GenerateAdUseCase,
    GenerateImageUseCase,
)
from src.application.campaigns.use_cases import (
    CreateCampaignFromYandexUseCase,
    CreateCampaignUseCase,
    DeleteCampaignImageUseCase,
    DeleteCampaignUseCase,
    GetCampaignByIdUseCase,
    GetCampaignsFromYandexUseCase,
    GetCampaignsUseCase,
    UpdateCampaignUseCase,
    UploadCampaignImageUseCase,
)
from src.application.clients.use_cases import (
    GetClientByIdUseCase,
    UpsertClientUseCase,
)
from src.application.export.use_cases import ExportAdvertiserDataUseCase
from src.application.moderation.use_cases import (
    CheckForbiddenWordsUseCase,
    GetForbiddenWordsUseCase,
    UpdateForbiddenWordsUseCase,
)
from src.application.statistics.use_cases import (
    GetAdvertiserCampaignsStatsUseCase,
    GetAdvertiserDailyStatsUseCase,
    GetCampaignDailyStatsUseCase,
    GetCampaignFeedbackStatsUseCase,
    GetCampaignStatsUseCase,
    GetClientsStatsUseCase,
)
from src.application.time.use_cases import (
    GetCurrentDateUseCase,
    TimeUseCase,
)
from src.common.depends import get_session, get_uow
from src.core.redis import get_redis
from src.core.settings import Settings, get_settings
from src.core.uow import AbstractUow
from src.domain.ads.interfaces import (
    GetAdForClientUseCaseProtocol,
    RecordAdClickUseCaseProtocol,
    SubmitAdFeedbackUseCaseProtocol,
)
from src.domain.advertisers.interfaces import (
    AdvertisersRepositoryProtocol,
    GetAdvertiserByIdUseCaseProtocol,
    MLScoreRepositoryProtocol,
    UpsertAdvertisersUseCaseProtocol,
    UpsertMLScoreUseCaseProtocol,
)
from src.domain.ai.interfaces import (
    AIServiceProtocol,
    GenerateAdUseCaseProtocol,
    GenerateImageUseCaseProtocol,
)
from src.domain.campaigns.interfaces import (
    CampaignsRepositoryProtocol,
    CreateCampaignFromYandexUseCaseProtocol,
    CreateCampaignUseCaseProtocol,
    DeleteCampaignImageUseCaseProtocol,
    DeleteCampaignUseCaseProtocol,
    GetCampaignByIdUseCaseProtocol,
    GetCampaignsFromYandexUseCaseProtocol,
    GetCampaignsUseCaseProtocol,
    UpdateCampaignUseCaseProtocol,
    UploadCampaignImageUseCaseProtocol,
    YandexDirectServiceProtocol,
)
from src.domain.clients.interfaces import (
    ClientsRepositoryProtocol,
    GetClientByIdUseCaseProtocol,
    UpsertClientUseCaseProtocol,
)
from src.domain.export.interfaces import (
    ExportAdvertiserDataUseCaseProtocol,
    ExportServiceProtocol,
)
from src.domain.moderation.interfaces import (
    CheckForbiddenWordsUseCaseProtocol,
    ForbiddenWordsRepositoryProtocol,
    GetForbiddenWordsUseCaseProtocol,
    ModerationServiceProtocol,
    UpdateForbiddenWordsUseCaseProtocol,
)
from src.domain.statistics.interfaces import (
    GetCampaignFeedbackStatsUseCaseProtocol,
    GetClientsStatsUseCaseProtocol,
    StatisticsRepositoryProtocol,
)
from src.domain.storage.interfaces import (
    MinioServiceProtocol,
)
from src.domain.time.interfaces import (
    GetCurrentDateUseCaseProtocol,
)
from src.infrastructure.ads.mappers import AdsMapper
from src.infrastructure.advertisers.mappers import AdvertisersMapper, MLScoreMapper
from src.infrastructure.advertisers.repositories import (
    AdvertisersRepository,
    MLScoreRepository,
)
from src.infrastructure.ai.ai_service import AIService
from src.infrastructure.campaigns.mappers import CampaignsMapper
from src.infrastructure.campaigns.repositories import (
    CampaignsRepository,
)
from src.infrastructure.clients.mappers import ClientsMapper
from src.infrastructure.clients.repositories import (
    ClientsRepository,
)
from src.infrastructure.export.export_service import ExportService
from src.infrastructure.moderation.mappers import ModerationMapper
from src.infrastructure.moderation.repositories import ForbiddenWordsRepository
from src.infrastructure.moderation.services import ModerationService
from src.infrastructure.statistics.mappers import StatisticsMapper
from src.infrastructure.statistics.repositories import (
    StatisticsRepository,
)
from src.infrastructure.storage.minio_service import MinioService
from src.infrastructure.time.repositories import (
    TimeRepository,
    TimeRepositoryProtocol,
)
from src.infrastructure.yandex.yandex_service import YandexDirectService


def get_ai_service(settings: Settings = Depends(get_settings)) -> AIServiceProtocol:
    return AIService(settings=settings)


def get_moderation_mapper() -> ModerationMapper:
    return ModerationMapper()


def get_moderation_repository(
    session: AsyncSession = Depends(get_session),
) -> ForbiddenWordsRepositoryProtocol:
    return ForbiddenWordsRepository(session)


def get_moderation_service(
    uow: AbstractUow = Depends(get_uow),
    repository: ForbiddenWordsRepositoryProtocol = Depends(get_moderation_repository),
    ai_service: AIServiceProtocol = Depends(get_ai_service),
    settings: Settings = Depends(get_settings),
) -> ModerationServiceProtocol:
    return ModerationService(uow, repository, ai_service, settings)


def get_get_forbidden_words_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: ForbiddenWordsRepositoryProtocol = Depends(get_moderation_repository),
) -> GetForbiddenWordsUseCaseProtocol:
    return GetForbiddenWordsUseCase(uow, repository)


def get_update_forbidden_words_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: ForbiddenWordsRepositoryProtocol = Depends(get_moderation_repository),
) -> UpdateForbiddenWordsUseCaseProtocol:
    return UpdateForbiddenWordsUseCase(uow, repository)


def get_check_forbidden_words_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: ForbiddenWordsRepositoryProtocol = Depends(get_moderation_repository),
    moderation_service: ModerationServiceProtocol = Depends(get_moderation_service),
    mapper: ModerationMapper = Depends(get_moderation_mapper),
) -> CheckForbiddenWordsUseCaseProtocol:
    return CheckForbiddenWordsUseCase(uow, repository, moderation_service, mapper)


def get_time_repository(
    redis: redis.Redis = Depends(get_redis),
) -> TimeRepositoryProtocol:
    return TimeRepository(redis=redis)


def get_minio_service(
    settings: Settings = Depends(get_settings),
) -> MinioServiceProtocol:
    return MinioService(settings)


def get_clients_mapper() -> ClientsMapper:
    return ClientsMapper()


def get_advertisers_mapper() -> AdvertisersMapper:
    return AdvertisersMapper()


def get_advertisers_repository(
    session: AsyncSession = Depends(get_session),
    mapper: AdvertisersMapper = Depends(get_advertisers_mapper),
) -> AdvertisersRepositoryProtocol:
    return AdvertisersRepository(session, mapper)


def get_clients_repository(
    session: AsyncSession = Depends(get_session),
    mapper: ClientsMapper = Depends(get_clients_mapper),
) -> ClientsRepositoryProtocol:
    return ClientsRepository(session, mapper)


def get_client_by_id_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: ClientsRepositoryProtocol = Depends(get_clients_repository),
    mapper: ClientsMapper = Depends(get_clients_mapper),
) -> GetClientByIdUseCaseProtocol:
    return GetClientByIdUseCase(uow, repository, mapper)


def get_upsert_client_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: ClientsRepositoryProtocol = Depends(get_clients_repository),
    mapper: ClientsMapper = Depends(get_clients_mapper),
) -> UpsertClientUseCaseProtocol:
    return UpsertClientUseCase(uow, repository, mapper)


def get_campaigns_mapper() -> CampaignsMapper:
    return CampaignsMapper()


def get_campaigns_repository(
    session: AsyncSession = Depends(get_session),
    mapper: CampaignsMapper = Depends(get_campaigns_mapper),
    time_repository: TimeRepositoryProtocol = Depends(get_time_repository),
) -> CampaignsRepositoryProtocol:
    return CampaignsRepository(session, mapper, time_repository)


def get_create_campaign_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: CampaignsRepositoryProtocol = Depends(get_campaigns_repository),
    mapper: CampaignsMapper = Depends(get_campaigns_mapper),
    moderation_service: ModerationServiceProtocol = Depends(get_moderation_service),
    advertisers_repository: AdvertisersRepositoryProtocol = Depends(
        get_advertisers_repository
    ),
    settings: Settings = Depends(get_settings),
) -> CreateCampaignUseCaseProtocol:
    return CreateCampaignUseCase(
        uow,
        repository,
        mapper,
        moderation_service,
        advertisers_repository,
        settings,
    )


def get_get_campaign_by_id_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: CampaignsRepositoryProtocol = Depends(get_campaigns_repository),
    mapper: CampaignsMapper = Depends(get_campaigns_mapper),
    advertisers_repository: AdvertisersRepositoryProtocol = Depends(
        get_advertisers_repository
    ),
) -> GetCampaignByIdUseCaseProtocol:
    return GetCampaignByIdUseCase(uow, repository, mapper, advertisers_repository)


def get_update_campaign_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: CampaignsRepositoryProtocol = Depends(get_campaigns_repository),
    mapper: CampaignsMapper = Depends(get_campaigns_mapper),
    moderation_service: ModerationServiceProtocol = Depends(get_moderation_service),
    advertisers_repository: AdvertisersRepositoryProtocol = Depends(
        get_advertisers_repository
    ),
    settings: Settings = Depends(get_settings),
) -> UpdateCampaignUseCaseProtocol:
    return UpdateCampaignUseCase(
        uow,
        repository,
        mapper,
        moderation_service,
        advertisers_repository,
        settings,
    )


def get_delete_campaign_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: CampaignsRepositoryProtocol = Depends(get_campaigns_repository),
    minio_service: MinioServiceProtocol = Depends(get_minio_service),
    advertisers_repository: AdvertisersRepositoryProtocol = Depends(
        get_advertisers_repository
    ),
) -> DeleteCampaignUseCaseProtocol:
    return DeleteCampaignUseCase(uow, repository, minio_service, advertisers_repository)


def get_upload_campaign_image_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: CampaignsRepositoryProtocol = Depends(get_campaigns_repository),
    mapper: CampaignsMapper = Depends(get_campaigns_mapper),
    minio_service: MinioServiceProtocol = Depends(get_minio_service),
    advertisers_repository: AdvertisersRepositoryProtocol = Depends(
        get_advertisers_repository
    ),
) -> UploadCampaignImageUseCaseProtocol:
    return UploadCampaignImageUseCase(
        uow, repository, mapper, minio_service, advertisers_repository
    )


def get_delete_campaign_image_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: CampaignsRepositoryProtocol = Depends(get_campaigns_repository),
    minio_service: MinioServiceProtocol = Depends(get_minio_service),
    advertisers_repository: AdvertisersRepositoryProtocol = Depends(
        get_advertisers_repository
    ),
) -> DeleteCampaignImageUseCaseProtocol:
    return DeleteCampaignImageUseCase(
        uow, repository, minio_service, advertisers_repository
    )


def get_ml_score_mapper() -> MLScoreMapper:
    return MLScoreMapper()


def get_ml_score_repository(
    session: AsyncSession = Depends(get_session),
    mapper: MLScoreMapper = Depends(get_ml_score_mapper),
    clients_repository: ClientsRepositoryProtocol = Depends(get_clients_repository),
    advertisers_repository: AdvertisersRepositoryProtocol = Depends(
        get_advertisers_repository
    ),
) -> MLScoreRepositoryProtocol:
    return MLScoreRepository(
        session, mapper, clients_repository, advertisers_repository
    )


def get_upsert_ml_score_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: MLScoreRepositoryProtocol = Depends(get_ml_score_repository),
    mapper: MLScoreMapper = Depends(get_ml_score_mapper),
) -> UpsertMLScoreUseCaseProtocol:
    return UpsertMLScoreUseCase(uow, repository, mapper)


async def get_ads_mapper() -> AdsMapper:
    return AdsMapper()


def get_statistics_mapper() -> StatisticsMapper:
    return StatisticsMapper()


def get_statistics_repository(
    session: AsyncSession = Depends(get_session),
    mapper: StatisticsMapper = Depends(get_statistics_mapper),
    time_repository: TimeRepositoryProtocol = Depends(get_time_repository),
) -> StatisticsRepositoryProtocol:
    return StatisticsRepository(session, mapper, time_repository)


def get_get_campaign_stats_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: StatisticsRepositoryProtocol = Depends(get_statistics_repository),
    campaigns_repository: CampaignsRepositoryProtocol = Depends(
        get_campaigns_repository
    ),
    mapper: StatisticsMapper = Depends(get_statistics_mapper),
) -> GetCampaignStatsUseCase:
    return GetCampaignStatsUseCase(
        uow,
        repository,
        campaigns_repository,
        mapper,
    )


def get_get_advertiser_campaigns_stats_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: StatisticsRepositoryProtocol = Depends(get_statistics_repository),
    advertisers_repository: AdvertisersRepositoryProtocol = Depends(
        get_advertisers_repository
    ),
    mapper: StatisticsMapper = Depends(get_statistics_mapper),
) -> GetAdvertiserCampaignsStatsUseCase:
    return GetAdvertiserCampaignsStatsUseCase(
        uow,
        repository,
        advertisers_repository,
        mapper,
    )


def get_get_campaign_daily_stats_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: StatisticsRepositoryProtocol = Depends(get_statistics_repository),
    campaigns_repository: CampaignsRepositoryProtocol = Depends(
        get_campaigns_repository
    ),
    mapper: StatisticsMapper = Depends(get_statistics_mapper),
) -> GetCampaignDailyStatsUseCase:
    return GetCampaignDailyStatsUseCase(uow, repository, campaigns_repository, mapper)


def get_get_advertiser_daily_stats_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: StatisticsRepositoryProtocol = Depends(get_statistics_repository),
    advertisers_repository: AdvertisersRepositoryProtocol = Depends(
        get_advertisers_repository
    ),
    mapper: StatisticsMapper = Depends(get_statistics_mapper),
) -> GetAdvertiserDailyStatsUseCase:
    return GetAdvertiserDailyStatsUseCase(
        uow, repository, advertisers_repository, mapper
    )


async def get_get_ad_for_client_use_case(
    uow: AbstractUow = Depends(get_uow),
    mapper: AdsMapper = Depends(get_ads_mapper),
    time_repository: TimeRepositoryProtocol = Depends(get_time_repository),
    clients_repository: ClientsRepositoryProtocol = Depends(get_clients_repository),
    campaigns_repository: CampaignsRepositoryProtocol = Depends(
        get_campaigns_repository
    ),
    ml_score_repository: MLScoreRepositoryProtocol = Depends(get_ml_score_repository),
    statistics_repository: StatisticsRepositoryProtocol = Depends(
        get_statistics_repository
    ),
) -> GetAdForClientUseCaseProtocol:
    return GetAdForClientUseCase(
        uow,
        mapper,
        time_repository,
        clients_repository,
        campaigns_repository,
        ml_score_repository,
        statistics_repository,
    )


async def get_record_ad_click_use_case(
    uow: AbstractUow = Depends(get_uow),
    mapper: AdsMapper = Depends(get_ads_mapper),
    statistics_repository: StatisticsRepositoryProtocol = Depends(
        get_statistics_repository
    ),
    time_repository: TimeRepositoryProtocol = Depends(get_time_repository),
    campaigns_repository: CampaignsRepositoryProtocol = Depends(
        get_campaigns_repository
    ),
    clients_repository: ClientsRepositoryProtocol = Depends(get_clients_repository),
) -> RecordAdClickUseCaseProtocol:
    return RecordAdClickUseCase(
        uow,
        mapper,
        statistics_repository,
        time_repository,
        campaigns_repository,
        clients_repository,
    )


def get_get_campaigns_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: CampaignsRepositoryProtocol = Depends(get_campaigns_repository),
    mapper: CampaignsMapper = Depends(get_campaigns_mapper),
    advertisers_repository: AdvertisersRepositoryProtocol = Depends(
        get_advertisers_repository
    ),
) -> GetCampaignsUseCaseProtocol:
    return GetCampaignsUseCase(uow, repository, mapper, advertisers_repository)


def get_get_advertiser_by_id_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: AdvertisersRepositoryProtocol = Depends(get_advertisers_repository),
    mapper: AdvertisersMapper = Depends(get_advertisers_mapper),
) -> GetAdvertiserByIdUseCaseProtocol:
    return GetAdvertiserByIdUseCase(uow, repository, mapper)


def get_upsert_advertisers_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: AdvertisersRepositoryProtocol = Depends(get_advertisers_repository),
    mapper: AdvertisersMapper = Depends(get_advertisers_mapper),
) -> UpsertAdvertisersUseCaseProtocol:
    return UpsertAdvertisersUseCase(uow, repository, mapper)


def get_generate_ad_use_case(
    uow: AbstractUow = Depends(get_uow),
    advertisers_repository: AdvertisersRepositoryProtocol = Depends(
        get_advertisers_repository
    ),
    ai_service: AIServiceProtocol = Depends(get_ai_service),
) -> GenerateAdUseCaseProtocol:
    return GenerateAdUseCase(
        uow=uow, advertisers_repository=advertisers_repository, ai_service=ai_service
    )


def get_time_use_case(
    repository: TimeRepositoryProtocol = Depends(get_time_repository),
    redis: redis.Redis = Depends(get_redis),
) -> TimeUseCase:
    return TimeUseCase(repository=repository, redis=redis)


def get_get_current_date_use_case(
    repository: TimeRepositoryProtocol = Depends(get_time_repository),
) -> GetCurrentDateUseCaseProtocol:
    return GetCurrentDateUseCase(repository=repository)


def get_get_clients_stats_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: StatisticsRepositoryProtocol = Depends(get_statistics_repository),
) -> GetClientsStatsUseCaseProtocol:
    return GetClientsStatsUseCase(uow, repository)


def get_submit_ad_feedback_use_case(
    uow: AbstractUow = Depends(get_uow),
    statistics_repository: StatisticsRepositoryProtocol = Depends(
        get_statistics_repository
    ),
    clients_repository: ClientsRepositoryProtocol = Depends(get_clients_repository),
    campaigns_repository: CampaignsRepositoryProtocol = Depends(
        get_campaigns_repository
    ),
) -> SubmitAdFeedbackUseCaseProtocol:
    return SubmitAdFeedbackUseCase(
        uow=uow,
        statistics_repository=statistics_repository,
        clients_repository=clients_repository,
        campaigns_repository=campaigns_repository,
    )


def get_get_campaign_feedback_stats_use_case(
    uow: AbstractUow = Depends(get_uow),
    repository: StatisticsRepositoryProtocol = Depends(get_statistics_repository),
    campaigns_repository: CampaignsRepositoryProtocol = Depends(
        get_campaigns_repository
    ),
    mapper: StatisticsMapper = Depends(get_statistics_mapper),
) -> GetCampaignFeedbackStatsUseCaseProtocol:
    return GetCampaignFeedbackStatsUseCase(
        uow, repository, campaigns_repository, mapper
    )


def get_export_service() -> ExportServiceProtocol:
    return ExportService()


def get_export_advertiser_data_use_case(
    uow: AbstractUow = Depends(get_uow),
    advertisers_repository: AdvertisersRepositoryProtocol = Depends(
        get_advertisers_repository
    ),
    campaigns_repository: CampaignsRepositoryProtocol = Depends(
        get_campaigns_repository
    ),
    statistics_repository: StatisticsRepositoryProtocol = Depends(
        get_statistics_repository
    ),
    ml_score_repository: MLScoreRepositoryProtocol = Depends(get_ml_score_repository),
    export_service: ExportServiceProtocol = Depends(get_export_service),
) -> ExportAdvertiserDataUseCaseProtocol:
    return ExportAdvertiserDataUseCase(
        uow=uow,
        advertisers_repository=advertisers_repository,
        campaigns_repository=campaigns_repository,
        statistics_repository=statistics_repository,
        ml_score_repository=ml_score_repository,
        export_service=export_service,
    )


def get_yandex_direct_service(
    settings: Settings = Depends(get_settings),
) -> YandexDirectServiceProtocol:
    return YandexDirectService(settings)


def get_get_campaigns_from_yandex_use_case(
    uow: AbstractUow = Depends(get_uow),
    yandex_service: YandexDirectServiceProtocol = Depends(get_yandex_direct_service),
    mapper: CampaignsMapper = Depends(get_campaigns_mapper),
) -> GetCampaignsFromYandexUseCaseProtocol:
    return GetCampaignsFromYandexUseCase(uow, yandex_service, mapper)


def get_create_campaign_from_yandex_use_case(
    uow: AbstractUow = Depends(get_uow),
    yandex_service: YandexDirectServiceProtocol = Depends(get_yandex_direct_service),
    repository: CampaignsRepositoryProtocol = Depends(get_campaigns_repository),
    mapper: CampaignsMapper = Depends(get_campaigns_mapper),
    advertisers_repository: AdvertisersRepositoryProtocol = Depends(
        get_advertisers_repository
    ),
) -> CreateCampaignFromYandexUseCaseProtocol:
    return CreateCampaignFromYandexUseCase(
        uow, yandex_service, repository, mapper, advertisers_repository
    )


def get_generate_image_use_case(
    uow: AbstractUow = Depends(get_uow),
    ai_service: AIServiceProtocol = Depends(get_ai_service),
    campaigns_repository: CampaignsRepositoryProtocol = Depends(
        get_campaigns_repository
    ),
) -> GenerateImageUseCaseProtocol:
    return GenerateImageUseCase(uow, ai_service, campaigns_repository)
