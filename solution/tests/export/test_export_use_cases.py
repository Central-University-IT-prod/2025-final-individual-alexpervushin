from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from src.application.export.dtos import (
    AdvertiserExportSchema,
    CampaignExportSchema,
    MLScoreExportSchema,
    StatisticsExportSchema,
    UniqueEventExportSchema,
)
from src.application.export.use_cases import ExportAdvertiserDataUseCase
from src.common.enums import TargetingGender
from src.domain.advertisers.entities import AdvertiserEntity
from src.domain.advertisers.exceptions import AdvertiserNotFoundException
from src.domain.campaigns.entities import CampaignEntity
from src.domain.statistics.entities import FeedbackEntity, StatisticsEntity


@pytest.fixture
def advertiser_id() -> UUID:
    return uuid4()


@pytest.fixture
def campaign_id() -> UUID:
    return uuid4()


@pytest.fixture
def client_id() -> UUID:
    return uuid4()


@pytest.fixture
def advertiser(advertiser_id: UUID) -> AdvertiserEntity:
    return AdvertiserEntity(
        id=advertiser_id,
        name="Test Advertiser",
    )


@pytest.fixture
def campaign(advertiser_id: UUID, campaign_id: UUID) -> CampaignEntity:
    return CampaignEntity(
        id=campaign_id,
        advertiser_id=advertiser_id,
        impressions_limit=1000,
        clicks_limit=100,
        cost_per_impression=0.1,
        cost_per_click=1.0,
        ad_title="Test Ad",
        ad_text="Test Ad Text",
        start_date=1,
        end_date=2,
        image_url="http://example.com/image.jpg",
        gender=TargetingGender.MALE,
        age_from=18,
        age_to=35,
        location="Moscow",
    )


@pytest.fixture
def statistics(campaign_id: UUID) -> StatisticsEntity:
    return StatisticsEntity(
        id=uuid4(),
        campaign_id=campaign_id,
        date=1600000000,
        impressions_count=500,
        clicks_count=50,
        conversion=0.1,
        spent_impressions=50.0,
        spent_clicks=50.0,
        spent_total=100.0,
    )


@pytest.fixture
def feedback(campaign_id: UUID, client_id: UUID) -> FeedbackEntity:
    return FeedbackEntity(
        id=uuid4(),
        client_id=client_id,
        campaign_id=campaign_id,
        rating=5,
        comment="Great ad!",
        created_at=datetime.fromtimestamp(1600000000),
    )


@pytest.fixture
def uow():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    return uow


@pytest.fixture
def advertisers_repository():
    return AsyncMock()


@pytest.fixture
def campaigns_repository():
    return AsyncMock()


@pytest.fixture
def statistics_repository():
    return AsyncMock()


@pytest.fixture
def ml_score_repository():
    return AsyncMock()


@pytest.fixture
def export_service():
    return MagicMock()


@pytest.fixture
def use_case(
    uow: AsyncMock,
    advertisers_repository: AsyncMock,
    campaigns_repository: AsyncMock,
    statistics_repository: AsyncMock,
    ml_score_repository: AsyncMock,
    export_service: MagicMock,
) -> ExportAdvertiserDataUseCase:
    advertisers_repository.get_by_id = AsyncMock()
    campaigns_repository.get_all = AsyncMock()
    statistics_repository.get_campaign_stats = AsyncMock()
    statistics_repository.get_campaign_feedbacks = AsyncMock()
    ml_score_repository.get_ml_score = AsyncMock()
    export_service.create_export_archive = MagicMock()

    return ExportAdvertiserDataUseCase(
        uow=uow,
        advertisers_repository=advertisers_repository,
        campaigns_repository=campaigns_repository,
        statistics_repository=statistics_repository,
        ml_score_repository=ml_score_repository,
        export_service=export_service,
    )


@pytest.mark.asyncio
async def test_export_advertiser_data_success(
    use_case: ExportAdvertiserDataUseCase,
    advertiser: AdvertiserEntity,
    campaign: CampaignEntity,
    statistics: StatisticsEntity,
    feedback: FeedbackEntity,
    advertiser_id: UUID,
    client_id: UUID,
):
    use_case.advertisers_repository.get_by_id.return_value = advertiser
    use_case.campaigns_repository.get_all.side_effect = [
        [campaign],
        [],
    ]
    use_case.statistics_repository.get_campaign_stats.return_value = statistics
    use_case.statistics_repository.get_campaign_feedbacks.return_value = [feedback]
    use_case.ml_score_repository.get_ml_score.return_value = 2
    use_case.export_service.create_export_archive.return_value = b"test_archive"

    result = await use_case.execute(advertiser_id)

    expected_export_data = AdvertiserExportSchema(
        advertiser_id=advertiser.id,
        name=advertiser.name,
        created_at=0,
        updated_at=0,
        campaigns=[
            CampaignExportSchema(
                campaign_id=campaign.id,
                image_url=campaign.image_url,
                impressions_limit=campaign.impressions_limit,
                clicks_limit=campaign.clicks_limit,
                cost_per_impression=campaign.cost_per_impression,
                cost_per_click=campaign.cost_per_click,
                ad_title=campaign.ad_title,
                ad_text=campaign.ad_text,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                gender=str(campaign.gender),
                age_from=campaign.age_from,
                age_to=campaign.age_to,
                location=campaign.location,
                created_at=0,
                updated_at=0,
                statistics=[
                    StatisticsExportSchema(
                        date=statistics.date,
                        impressions_count=statistics.impressions_count,
                        clicks_count=statistics.clicks_count,
                        conversion=statistics.conversion,
                        spent_impressions=statistics.spent_impressions,
                        spent_clicks=statistics.spent_clicks,
                        spent_total=statistics.spent_total,
                        created_at=0,
                        updated_at=0,
                    )
                ],
                unique_events=[
                    UniqueEventExportSchema(
                        client_id=feedback.client_id,
                        event_type="feedback",
                        rating=feedback.rating,
                        comment=feedback.comment,
                        created_at=int(feedback.created_at.timestamp()),
                        updated_at=0,
                    )
                ],
            )
        ],
        ml_scores=[
            MLScoreExportSchema(
                client_id=client_id,
                score=2,
                created_at=0,
                updated_at=0,
            )
        ],
        telegram_users=[],
    )

    use_case.export_service.create_export_archive.assert_called_once_with(
        expected_export_data
    )
    assert result == b"test_archive"


@pytest.mark.asyncio
async def test_export_advertiser_data_not_found(
    use_case: ExportAdvertiserDataUseCase,
    advertiser_id: UUID,
):
    use_case.advertisers_repository.get_by_id.side_effect = AdvertiserNotFoundException(
        advertiser_id
    )

    with pytest.raises(ValueError, match=f"Рекламодатель {advertiser_id} не найден"):
        await use_case.execute(advertiser_id)


@pytest.mark.asyncio
async def test_export_advertiser_data_no_campaigns(
    use_case: ExportAdvertiserDataUseCase,
    advertiser: AdvertiserEntity,
    advertiser_id: UUID,
):
    use_case.advertisers_repository.get_by_id.return_value = advertiser
    use_case.campaigns_repository.get_all.return_value = []
    use_case.export_service.create_export_archive.return_value = b"empty_archive"

    result = await use_case.execute(advertiser_id)

    expected_export_data = AdvertiserExportSchema(
        advertiser_id=advertiser.id,
        name=advertiser.name,
        created_at=0,
        updated_at=0,
        campaigns=[],
        ml_scores=[],
        telegram_users=[],
    )

    use_case.export_service.create_export_archive.assert_called_once_with(
        expected_export_data
    )
    assert result == b"empty_archive"


@pytest.mark.asyncio
async def test_export_advertiser_data_no_statistics(
    use_case: ExportAdvertiserDataUseCase,
    advertiser: AdvertiserEntity,
    campaign: CampaignEntity,
    advertiser_id: UUID,
):
    use_case.advertisers_repository.get_by_id.return_value = advertiser
    use_case.campaigns_repository.get_all.side_effect = [
        [campaign],
        [],
    ]
    use_case.statistics_repository.get_campaign_stats.return_value = None
    use_case.statistics_repository.get_campaign_feedbacks.return_value = []
    use_case.export_service.create_export_archive.return_value = b"no_stats_archive"

    result = await use_case.execute(advertiser_id)

    expected_export_data = AdvertiserExportSchema(
        advertiser_id=advertiser.id,
        name=advertiser.name,
        created_at=0,
        updated_at=0,
        campaigns=[
            CampaignExportSchema(
                campaign_id=campaign.id,
                image_url=campaign.image_url,
                impressions_limit=campaign.impressions_limit,
                clicks_limit=campaign.clicks_limit,
                cost_per_impression=campaign.cost_per_impression,
                cost_per_click=campaign.cost_per_click,
                ad_title=campaign.ad_title,
                ad_text=campaign.ad_text,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                gender=str(campaign.gender),
                age_from=campaign.age_from,
                age_to=campaign.age_to,
                location=campaign.location,
                created_at=0,
                updated_at=0,
                statistics=[],
                unique_events=[],
            )
        ],
        ml_scores=[],
        telegram_users=[],
    )

    use_case.export_service.create_export_archive.assert_called_once_with(
        expected_export_data
    )
    assert result == b"no_stats_archive"
