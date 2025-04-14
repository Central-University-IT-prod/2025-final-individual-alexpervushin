from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from src.application.ads.dtos import AdsGetResponse
from src.application.ads.use_cases import (
    GetAdForClientUseCase,
    RecordAdClickUseCase,
    SubmitAdFeedbackUseCase,
)
from src.domain.ads.entities import AdEntity
from src.domain.ads.exceptions import AdsNotFoundException
from src.domain.campaigns.entities import CampaignEntity, TargetingGender
from src.domain.campaigns.exceptions import CampaignNotFoundException
from src.domain.clients.entities import ClientEntity
from src.domain.clients.exceptions import ClientNotFoundException
from src.domain.statistics.entities import StatisticsEntity
from src.domain.statistics.exceptions import (
    DuplicateClickError,
    StatisticsRepositoryError,
)
from src.infrastructure.ads.mappers import AdsMapper


@pytest.fixture
def dummy_uow():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    uow.impression_lock = AsyncMock()
    uow.impression_lock.__aenter__.return_value = uow.impression_lock
    uow.impression_lock.__aexit__.return_value = None
    uow.click_lock = AsyncMock()
    uow.click_lock.__aenter__.return_value = uow.click_lock
    uow.click_lock.__aexit__.return_value = None
    return uow


@pytest.fixture
def ads_mapper():
    return AdsMapper()


@pytest.fixture
def dummy_client():
    return ClientEntity(
        id=uuid4(),
        login="test_client",
        age=30,
        location="NY",
        gender="MALE",
    )


@pytest.fixture
def dummy_campaign():
    return CampaignEntity(
        id=uuid4(),
        advertiser_id=uuid4(),
        impressions_limit=100,
        clicks_limit=10,
        cost_per_impression=0.1,
        cost_per_click=1.0,
        ad_title="Test Ad",
        ad_text="Test ad text",
        start_date=0,
        end_date=100,
        gender=None,
        age_from=None,
        age_to=None,
        location=None,
    )


@pytest.fixture
def dummy_stats(dummy_campaign: CampaignEntity):
    return StatisticsEntity(
        id=uuid4(),
        campaign_id=dummy_campaign.id,
        date=0,
        impressions_count=0,
        clicks_count=0,
        conversion=0.0,
        spent_impressions=0.0,
        spent_clicks=0.0,
        spent_total=0.0,
    )


class TestGetAdForClientUseCase:
    @pytest.mark.asyncio
    async def test_execute_success(
        self,
        dummy_uow: AsyncMock,
        ads_mapper: AdsMapper,
        dummy_client: ClientEntity,
        dummy_campaign: CampaignEntity,
        dummy_stats: StatisticsEntity,
    ):
        clients_repo = AsyncMock()
        clients_repo.get_by_id.return_value = dummy_client

        campaigns_repo = AsyncMock()
        campaigns_repo.get_targeted_campaigns.return_value = [dummy_campaign]

        ml_score_repo = AsyncMock()
        ml_score_repo.get_ml_score.return_value = 50

        statistics_repo = AsyncMock()
        statistics_repo.get_campaign_stats.return_value = dummy_stats
        statistics_repo.register_impression = AsyncMock()

        ad_entity = AdEntity(
            id=dummy_campaign.id,
            ad_title=dummy_campaign.ad_title,
            ad_text=dummy_campaign.ad_text,
            advertiser_id=dummy_campaign.advertiser_id,
            image_url=dummy_campaign.image_url or "",
        )
        ads_mapper.from_model_to_entity = MagicMock(return_value=ad_entity)
        expected_response = AdsGetResponse(
            ad_id=ad_entity.id,
            ad_title=ad_entity.ad_title,
            ad_text=ad_entity.ad_text,
            advertiser_id=ad_entity.advertiser_id,
            image_url=ad_entity.image_url,
        )
        ads_mapper.from_entity_to_schema = MagicMock(return_value=expected_response)

        use_case = GetAdForClientUseCase(
            uow=dummy_uow,
            mapper=ads_mapper,
            time_repository=AsyncMock(),
            clients_repository=clients_repo,
            campaigns_repository=campaigns_repo,
            ml_score_repository=ml_score_repo,
            statistics_repository=statistics_repo,
        )

        result = await use_case.execute(dummy_client.id)

        assert result == expected_response
        clients_repo.get_by_id.assert_called_once_with(dummy_client.id)
        campaigns_repo.get_targeted_campaigns.assert_called_once_with(dummy_client.id)
        ml_score_repo.get_ml_score.assert_called_once()
        statistics_repo.get_campaign_stats.assert_called_once_with(
            campaign_id=dummy_campaign.id
        )
        statistics_repo.register_impression.assert_called_once_with(
            client_id=dummy_client.id, campaign_id=dummy_campaign.id
        )
        dummy_uow.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_client_not_found(
        self, dummy_uow: AsyncMock, ads_mapper: AdsMapper
    ):
        clients_repo = AsyncMock()
        clients_repo.get_by_id.side_effect = ClientNotFoundException("Client not found")

        campaigns_repo = AsyncMock()
        ml_score_repo = AsyncMock()
        statistics_repo = AsyncMock()

        use_case = GetAdForClientUseCase(
            uow=dummy_uow,
            mapper=ads_mapper,
            time_repository=AsyncMock(),
            clients_repository=clients_repo,
            campaigns_repository=campaigns_repo,
            ml_score_repository=ml_score_repo,
            statistics_repository=statistics_repo,
        )
        with pytest.raises(ClientNotFoundException):
            await use_case.execute(uuid4())

    @pytest.mark.asyncio
    async def test_execute_no_matching_campaigns(
        self, dummy_uow: AsyncMock, ads_mapper: AdsMapper, dummy_client: ClientEntity
    ):
        non_matching_campaign = CampaignEntity(
            id=uuid4(),
            advertiser_id=uuid4(),
            impressions_limit=100,
            clicks_limit=10,
            cost_per_impression=0.1,
            cost_per_click=1.0,
            ad_title="Non-matching Ad",
            ad_text="Ad text",
            start_date=0,
            end_date=100,
            gender=TargetingGender.FEMALE,
            age_from=None,
            age_to=None,
            location=None,
        )
        clients_repo = AsyncMock()
        clients_repo.get_by_id.return_value = dummy_client

        campaigns_repo = AsyncMock()
        campaigns_repo.get_targeted_campaigns.return_value = []

        ml_score_repo = AsyncMock()
        ml_score_repo.get_ml_score.return_value = 0

        statistics_repo = AsyncMock()
        statistics_repo.get_campaign_stats.return_value = StatisticsEntity(
            id=uuid4(),
            campaign_id=non_matching_campaign.id,
            date=0,
            impressions_count=0,
            clicks_count=0,
            conversion=0.0,
            spent_impressions=0.0,
            spent_clicks=0.0,
            spent_total=0.0,
        )

        use_case = GetAdForClientUseCase(
            uow=dummy_uow,
            mapper=ads_mapper,
            time_repository=AsyncMock(),
            clients_repository=clients_repo,
            campaigns_repository=campaigns_repo,
            ml_score_repository=ml_score_repo,
            statistics_repository=statistics_repo,
        )
        with pytest.raises(AdsNotFoundException) as exc:
            await use_case.execute(dummy_client.id)
        assert "Не найдены подходящие объявления" in str(exc.value)


class TestRecordAdClickUseCase:
    @pytest.mark.asyncio
    async def test_execute_success(
        self,
        dummy_uow: AsyncMock,
        dummy_client: ClientEntity,
        dummy_campaign: CampaignEntity,
    ):
        campaigns_repo = AsyncMock()
        campaigns_repo.get_by_id.return_value = dummy_campaign

        clients_repo = AsyncMock()
        clients_repo.get_by_id.return_value = dummy_client

        statistics_repo = AsyncMock()
        statistics_repo.register_click = AsyncMock()

        use_case = RecordAdClickUseCase(
            uow=dummy_uow,
            mapper=MagicMock(),
            statistics_repository=statistics_repo,
            time_repository=AsyncMock(),
            campaigns_repository=campaigns_repo,
            clients_repository=clients_repo,
        )

        ad_id = dummy_campaign.id
        client_id = dummy_client.id

        await use_case.execute(ad_id, client_id)

        campaigns_repo.get_by_id.assert_called_once_with(ad_id)
        clients_repo.get_by_id.assert_called_once_with(client_id)
        statistics_repo.register_click.assert_called_once_with(
            client_id=client_id, campaign_id=ad_id
        )
        dummy_uow.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_campaign_not_found(
        self,
        dummy_uow: AsyncMock,
        dummy_client: ClientEntity,
    ):
        campaigns_repo = AsyncMock()
        campaigns_repo.get_by_id.side_effect = CampaignNotFoundException(
            "Campaign not found"
        )

        statistics_repo = AsyncMock()

        use_case = RecordAdClickUseCase(
            uow=dummy_uow,
            mapper=MagicMock(),
            statistics_repository=statistics_repo,
            time_repository=AsyncMock(),
            campaigns_repository=campaigns_repo,
            clients_repository=AsyncMock(),
        )
        ad_id = uuid4()
        client_id = dummy_client.id

        with pytest.raises(CampaignNotFoundException):
            await use_case.execute(ad_id, client_id)

    @pytest.mark.asyncio
    async def test_execute_client_not_found(
        self,
        dummy_uow: AsyncMock,
        dummy_campaign: CampaignEntity,
    ):
        campaigns_repo = AsyncMock()
        campaigns_repo.get_by_id.return_value = dummy_campaign

        clients_repo = AsyncMock()
        clients_repo.get_by_id.side_effect = ClientNotFoundException("Client not found")

        statistics_repo = AsyncMock()

        use_case = RecordAdClickUseCase(
            uow=dummy_uow,
            mapper=MagicMock(),
            statistics_repository=statistics_repo,
            time_repository=AsyncMock(),
            campaigns_repository=campaigns_repo,
            clients_repository=clients_repo,
        )
        ad_id = dummy_campaign.id
        client_id = uuid4()

        with pytest.raises(ClientNotFoundException):
            await use_case.execute(ad_id, client_id)

    @pytest.mark.asyncio
    async def test_execute_duplicate_click(
        self,
        dummy_uow: AsyncMock,
        dummy_campaign: CampaignEntity,
        dummy_client: ClientEntity,
    ):
        campaigns_repo = AsyncMock()
        campaigns_repo.get_by_id.return_value = dummy_campaign

        clients_repo = AsyncMock()
        clients_repo.get_by_id.return_value = dummy_client

        statistics_repo = AsyncMock()
        statistics_repo.register_click.side_effect = DuplicateClickError(
            "Duplicate click"
        )

        use_case = RecordAdClickUseCase(
            uow=dummy_uow,
            mapper=MagicMock(),
            statistics_repository=statistics_repo,
            time_repository=AsyncMock(),
            campaigns_repository=campaigns_repo,
            clients_repository=clients_repo,
        )
        ad_id = dummy_campaign.id
        client_id = dummy_client.id

        with pytest.raises(DuplicateClickError) as exc:
            await use_case.execute(ad_id, client_id)
        assert "Duplicate click" in str(exc.value)
        dummy_uow.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_unexpected_error(
        self,
        dummy_uow: AsyncMock,
        dummy_campaign: CampaignEntity,
        dummy_client: ClientEntity,
    ):
        campaigns_repo = AsyncMock()
        campaigns_repo.get_by_id.return_value = dummy_campaign

        clients_repo = AsyncMock()
        clients_repo.get_by_id.return_value = dummy_client

        statistics_repo = AsyncMock()
        statistics_repo.register_click.side_effect = ValueError("Unexpected error")

        use_case = RecordAdClickUseCase(
            uow=dummy_uow,
            mapper=MagicMock(),
            statistics_repository=statistics_repo,
            time_repository=AsyncMock(),
            campaigns_repository=campaigns_repo,
            clients_repository=clients_repo,
        )
        ad_id = dummy_campaign.id
        client_id = dummy_client.id

        with pytest.raises(StatisticsRepositoryError) as exc:
            await use_case.execute(ad_id, client_id)
        assert "Unexpected error recording click:" in str(exc.value)
        dummy_uow.rollback.assert_called_once()


class TestSubmitAdFeedbackUseCase:
    @pytest.mark.asyncio
    async def test_execute_success(
        self,
        dummy_uow: AsyncMock,
        dummy_client: ClientEntity,
        dummy_campaign: CampaignEntity,
    ):
        clients_repo = AsyncMock()
        clients_repo.get_by_id.return_value = dummy_client

        campaigns_repo = AsyncMock()
        campaigns_repo.get_by_id.return_value = dummy_campaign

        statistics_repo = AsyncMock()
        statistics_repo.register_feedback = AsyncMock()

        use_case = SubmitAdFeedbackUseCase(
            uow=dummy_uow,
            statistics_repository=statistics_repo,
            clients_repository=clients_repo,
            campaigns_repository=campaigns_repo,
        )
        ad_id = dummy_campaign.id
        client_id = dummy_client.id
        rating = 5
        comment = "Great ad!"

        await use_case.execute(ad_id, client_id, rating, comment)

        clients_repo.get_by_id.assert_called_once_with(client_id)
        campaigns_repo.get_by_id.assert_called_once_with(ad_id)
        statistics_repo.register_feedback.assert_called_once_with(
            client_id=client_id, campaign_id=ad_id, rating=rating, comment=comment
        )
        dummy_uow.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_client_not_found(
        self,
        dummy_uow: AsyncMock,
        dummy_campaign: CampaignEntity,
    ):
        clients_repo = AsyncMock()
        clients_repo.get_by_id.side_effect = ClientNotFoundException("Client not found")

        campaigns_repo = AsyncMock()
        statistics_repo = AsyncMock()

        use_case = SubmitAdFeedbackUseCase(
            uow=dummy_uow,
            statistics_repository=statistics_repo,
            clients_repository=clients_repo,
            campaigns_repository=campaigns_repo,
        )
        ad_id = dummy_campaign.id
        client_id = uuid4()
        rating = 3
        comment = "Not good"

        with pytest.raises(ClientNotFoundException):
            await use_case.execute(ad_id, client_id, rating, comment)

    @pytest.mark.asyncio
    async def test_execute_campaign_not_found(
        self,
        dummy_uow: AsyncMock,
        dummy_client: ClientEntity,
    ):
        clients_repo = AsyncMock()
        clients_repo.get_by_id.return_value = dummy_client

        campaigns_repo = AsyncMock()
        campaigns_repo.get_by_id.side_effect = CampaignNotFoundException(
            "Campaign not found"
        )

        statistics_repo = AsyncMock()

        use_case = SubmitAdFeedbackUseCase(
            uow=dummy_uow,
            statistics_repository=statistics_repo,
            clients_repository=clients_repo,
            campaigns_repository=campaigns_repo,
        )
        ad_id = uuid4()
        client_id = dummy_client.id
        rating = 4
        comment = "Good ad"

        with pytest.raises(CampaignNotFoundException):
            await use_case.execute(ad_id, client_id, rating, comment)
