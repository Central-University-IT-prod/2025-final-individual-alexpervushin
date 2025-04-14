from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.statistics.dtos import (
    CampaignFeedbackItem,
    CampaignFeedbackResponse,
    ClientStatsResponse,
    DailyStatsResponse,
    StatsResponse,
)
from src.application.statistics.use_cases import (
    GetAdvertiserCampaignsStatsUseCase,
    GetAdvertiserDailyStatsUseCase,
    GetCampaignDailyStatsUseCase,
    GetCampaignFeedbackStatsUseCase,
    GetCampaignStatsUseCase,
    GetClientsStatsUseCase,
)
from src.domain.advertisers.exceptions import AdvertiserNotFoundException
from src.domain.campaigns.exceptions import CampaignNotFoundException
from src.domain.statistics.exceptions import StatisticsRepositoryError


@pytest.fixture
def dummy_uow():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.commit = AsyncMock()
    return uow


class TestGetCampaignStatsUseCase:
    @pytest.mark.asyncio
    async def test_execute_success(self, dummy_uow: AsyncMock):
        campaign_id = uuid4()
        dummy_entity = MagicMock()
        expected_response = StatsResponse(
            impressions_count=100,
            clicks_count=10,
            conversion=0.1,
            spent_impressions=200,
            spent_clicks=30,
            spent_total=250,
        )

        campaigns_repository = AsyncMock()
        campaigns_repository.get_by_id.return_value = MagicMock()
        repository = AsyncMock()
        repository.get_campaign_stats.return_value = dummy_entity
        mapper = MagicMock()
        mapper.from_entity_to_statistics_schema.return_value = expected_response

        use_case = GetCampaignStatsUseCase(
            uow=dummy_uow,
            repository=repository,
            campaigns_repository=campaigns_repository,
            mapper=mapper,
        )

        result = await use_case.execute(campaign_id)
        assert result == expected_response
        campaigns_repository.get_by_id.assert_called_once_with(campaign_id)
        repository.get_campaign_stats.assert_called_once_with(campaign_id)
        mapper.from_entity_to_statistics_schema.assert_called_once_with(dummy_entity)

    @pytest.mark.asyncio
    async def test_execute_campaign_not_found(self, dummy_uow: AsyncMock):
        campaign_id = uuid4()
        campaigns_repository = AsyncMock()
        campaigns_repository.get_by_id.side_effect = CampaignNotFoundException(
            "Campaign not found"
        )
        repository = AsyncMock()
        mapper = MagicMock()

        use_case = GetCampaignStatsUseCase(
            uow=dummy_uow,
            repository=repository,
            campaigns_repository=campaigns_repository,
            mapper=mapper,
        )
        with pytest.raises(CampaignNotFoundException) as exc:
            await use_case.execute(campaign_id)
        assert "Campaign not found" in str(exc.value)

    @pytest.mark.asyncio
    async def test_execute_unexpected_error(self, dummy_uow: AsyncMock):
        campaign_id = uuid4()
        campaigns_repository = AsyncMock()
        campaigns_repository.get_by_id.return_value = MagicMock()
        repository = AsyncMock()
        repository.get_campaign_stats.side_effect = Exception("Unexpected error")
        mapper = MagicMock()

        use_case = GetCampaignStatsUseCase(
            uow=dummy_uow,
            repository=repository,
            campaigns_repository=campaigns_repository,
            mapper=mapper,
        )
        with pytest.raises(StatisticsRepositoryError) as exc:
            await use_case.execute(campaign_id)
        assert "Unexpected error:" in str(exc.value)


class TestGetAdvertiserCampaignsStatsUseCase:
    @pytest.mark.asyncio
    async def test_execute_success(self, dummy_uow: AsyncMock):
        advertiser_id = uuid4()
        dummy_entity = MagicMock()
        expected_response = StatsResponse(
            impressions_count=150,
            clicks_count=15,
            conversion=0.1,
            spent_impressions=250,
            spent_clicks=40,
            spent_total=300,
        )
        advertisers_repository = AsyncMock()
        advertisers_repository.get_by_id.return_value = MagicMock()
        repository = AsyncMock()
        repository.get_advertiser_stats.return_value = dummy_entity
        mapper = MagicMock()
        mapper.from_entity_to_statistics_schema.return_value = expected_response

        use_case = GetAdvertiserCampaignsStatsUseCase(
            uow=dummy_uow,
            repository=repository,
            advertisers_repository=advertisers_repository,
            mapper=mapper,
        )
        result = await use_case.execute(advertiser_id)
        assert result == expected_response
        advertisers_repository.get_by_id.assert_called_once_with(advertiser_id)
        repository.get_advertiser_stats.assert_called_once_with(advertiser_id)
        mapper.from_entity_to_statistics_schema.assert_called_once_with(dummy_entity)

    @pytest.mark.asyncio
    async def test_execute_advertiser_not_found(self, dummy_uow: AsyncMock):
        advertiser_id = uuid4()
        advertisers_repository = AsyncMock()
        advertisers_repository.get_by_id.side_effect = AdvertiserNotFoundException(
            "Advertiser not found"
        )
        repository = AsyncMock()
        mapper = MagicMock()

        use_case = GetAdvertiserCampaignsStatsUseCase(
            uow=dummy_uow,
            repository=repository,
            advertisers_repository=advertisers_repository,
            mapper=mapper,
        )
        with pytest.raises(AdvertiserNotFoundException) as exc:
            await use_case.execute(advertiser_id)
        assert "Advertiser not found" in str(exc.value)

    @pytest.mark.asyncio
    async def test_execute_unexpected_error(self, dummy_uow: AsyncMock):
        advertiser_id = uuid4()
        advertisers_repository = AsyncMock()
        advertisers_repository.get_by_id.return_value = MagicMock()
        repository = AsyncMock()
        repository.get_advertiser_stats.side_effect = Exception("Unhandled error")
        mapper = MagicMock()

        use_case = GetAdvertiserCampaignsStatsUseCase(
            uow=dummy_uow,
            repository=repository,
            advertisers_repository=advertisers_repository,
            mapper=mapper,
        )
        with pytest.raises(StatisticsRepositoryError) as exc:
            await use_case.execute(advertiser_id)
        assert "Unexpected error:" in str(exc.value)


class TestGetCampaignDailyStatsUseCase:
    @pytest.mark.asyncio
    async def test_execute_success(self, dummy_uow: AsyncMock):
        campaign_id = uuid4()
        dummy_stats_entity1 = MagicMock()
        dummy_stats_entity2 = MagicMock()

        response1 = DailyStatsResponse(
            impressions_count=100,
            clicks_count=10,
            conversion=0.1,
            spent_impressions=200,
            spent_clicks=30,
            spent_total=250,
            date=1,
        )
        response2 = DailyStatsResponse(
            impressions_count=150,
            clicks_count=15,
            conversion=0.1,
            spent_impressions=250,
            spent_clicks=40,
            spent_total=300,
            date=2,
        )

        campaigns_repository = AsyncMock()
        campaigns_repository.get_by_id.return_value = MagicMock()
        repository = AsyncMock()
        repository.get_campaign_daily_stats.return_value = [
            dummy_stats_entity1,
            dummy_stats_entity2,
        ]
        mapper = MagicMock()
        mapper.from_entity_to_schema_daily_stats.side_effect = [response1, response2]

        use_case = GetCampaignDailyStatsUseCase(
            uow=dummy_uow,
            repository=repository,
            campaigns_repository=campaigns_repository,
            mapper=mapper,
        )
        result = await use_case.execute(campaign_id)
        assert result == [response1, response2]
        campaigns_repository.get_by_id.assert_called_once_with(campaign_id)
        repository.get_campaign_daily_stats.assert_called_once_with(campaign_id)
        mapper.from_entity_to_schema_daily_stats.assert_any_call(dummy_stats_entity1)
        mapper.from_entity_to_schema_daily_stats.assert_any_call(dummy_stats_entity2)

    @pytest.mark.asyncio
    async def test_execute_campaign_not_found(self, dummy_uow: AsyncMock):
        campaign_id = uuid4()
        campaigns_repository = AsyncMock()
        campaigns_repository.get_by_id.side_effect = CampaignNotFoundException(
            "Campaign not found"
        )
        repository = AsyncMock()
        mapper = MagicMock()

        use_case = GetCampaignDailyStatsUseCase(
            uow=dummy_uow,
            repository=repository,
            campaigns_repository=campaigns_repository,
            mapper=mapper,
        )
        with pytest.raises(CampaignNotFoundException) as exc:
            await use_case.execute(campaign_id)
        assert "Campaign not found" in str(exc.value)

    @pytest.mark.asyncio
    async def test_execute_unexpected_error(self, dummy_uow: AsyncMock):
        campaign_id = uuid4()
        campaigns_repository = AsyncMock()
        campaigns_repository.get_by_id.return_value = MagicMock()
        repository = AsyncMock()
        repository.get_campaign_daily_stats.side_effect = Exception("Unexpected error")
        mapper = MagicMock()

        use_case = GetCampaignDailyStatsUseCase(
            uow=dummy_uow,
            repository=repository,
            campaigns_repository=campaigns_repository,
            mapper=mapper,
        )
        with pytest.raises(StatisticsRepositoryError) as exc:
            await use_case.execute(campaign_id)
        assert "Unexpected error:" in str(exc.value)


class TestGetAdvertiserDailyStatsUseCase:
    @pytest.mark.asyncio
    async def test_execute_success(self, dummy_uow: AsyncMock):
        advertiser_id = uuid4()
        dummy_stats_entity1 = MagicMock()
        dummy_stats_entity2 = MagicMock()

        response1 = DailyStatsResponse(
            impressions_count=200,
            clicks_count=20,
            conversion=0.1,
            spent_impressions=300,
            spent_clicks=50,
            spent_total=350,
            date=1,
        )
        response2 = DailyStatsResponse(
            impressions_count=250,
            clicks_count=25,
            conversion=0.1,
            spent_impressions=350,
            spent_clicks=60,
            spent_total=400,
            date=2,
        )
        advertisers_repository = AsyncMock()
        advertisers_repository.get_by_id.return_value = MagicMock()
        repository = AsyncMock()
        repository.get_advertiser_daily_stats.return_value = [
            dummy_stats_entity1,
            dummy_stats_entity2,
        ]
        mapper = MagicMock()
        mapper.from_entity_to_schema_daily_stats.side_effect = [response1, response2]

        use_case = GetAdvertiserDailyStatsUseCase(
            uow=dummy_uow,
            repository=repository,
            advertisers_repository=advertisers_repository,
            mapper=mapper,
        )
        result = await use_case.execute(advertiser_id)
        assert result == [response1, response2]
        advertisers_repository.get_by_id.assert_called_once_with(advertiser_id)
        repository.get_advertiser_daily_stats.assert_called_once_with(advertiser_id)
        mapper.from_entity_to_schema_daily_stats.assert_any_call(dummy_stats_entity1)
        mapper.from_entity_to_schema_daily_stats.assert_any_call(dummy_stats_entity2)

    @pytest.mark.asyncio
    async def test_execute_advertiser_not_found(self, dummy_uow: AsyncMock):
        advertiser_id = uuid4()
        advertisers_repository = AsyncMock()
        advertisers_repository.get_by_id.side_effect = AdvertiserNotFoundException(
            "Advertiser not found"
        )
        repository = AsyncMock()
        mapper = MagicMock()
        use_case = GetAdvertiserDailyStatsUseCase(
            uow=dummy_uow,
            repository=repository,
            advertisers_repository=advertisers_repository,
            mapper=mapper,
        )
        with pytest.raises(AdvertiserNotFoundException) as exc:
            await use_case.execute(advertiser_id)
        assert "Advertiser not found" in str(exc.value)

    @pytest.mark.asyncio
    async def test_execute_unexpected_error(self, dummy_uow: AsyncMock):
        advertiser_id = uuid4()
        advertisers_repository = AsyncMock()
        advertisers_repository.get_by_id.return_value = MagicMock()
        repository = AsyncMock()
        repository.get_advertiser_daily_stats.side_effect = Exception(
            "Unexpected error"
        )
        mapper = MagicMock()

        use_case = GetAdvertiserDailyStatsUseCase(
            uow=dummy_uow,
            repository=repository,
            advertisers_repository=advertisers_repository,
            mapper=mapper,
        )
        with pytest.raises(StatisticsRepositoryError) as exc:
            await use_case.execute(advertiser_id)
        assert "Unexpected error:" in str(exc.value)


class TestGetClientsStatsUseCase:
    @pytest.mark.asyncio
    async def test_execute_success(self, dummy_uow: AsyncMock):
        dummy_client_stats = ClientStatsResponse(
            total_clients=100,
            demographics_distribution={"male": {"18-24": 50}, "female": {"25-34": 50}},
            top_locations=[{"location": "Moscow", "count": 100}],
            average_age=30.5,
        )
        repository = AsyncMock()
        repository.get_clients_stats.return_value = dummy_client_stats

        use_case = GetClientsStatsUseCase(
            uow=dummy_uow,
            repository=repository,
        )
        result = await use_case.execute()
        assert result == dummy_client_stats
        repository.get_clients_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_repository_error(self, dummy_uow: AsyncMock):
        repository = AsyncMock()
        repository.get_clients_stats.side_effect = StatisticsRepositoryError("DB Error")
        use_case = GetClientsStatsUseCase(
            uow=dummy_uow,
            repository=repository,
        )
        with pytest.raises(StatisticsRepositoryError) as exc:
            await use_case.execute()
        assert "DB Error" in str(exc.value)


class TestGetCampaignFeedbackStatsUseCase:
    @pytest.mark.asyncio
    async def test_execute_success(self, dummy_uow: AsyncMock):
        campaign_id = uuid4()
        dummy_feedback_entities = [MagicMock(), MagicMock()]
        expected_response = CampaignFeedbackResponse(
            average_rating=4.5,
            total_ratings=2,
            feedbacks=[
                CampaignFeedbackItem(
                    client_id=uuid4(),
                    rating=5,
                    comment="Great",
                    created_at=datetime(2024, 1, 1),
                ),
                CampaignFeedbackItem(
                    client_id=uuid4(),
                    rating=4,
                    comment="Good",
                    created_at=datetime(2024, 1, 2),
                ),
            ],
        )
        campaigns_repository = AsyncMock()
        campaigns_repository.get_by_id.return_value = MagicMock()
        repository = AsyncMock()
        repository.get_campaign_feedbacks.return_value = dummy_feedback_entities
        mapper = MagicMock()
        mapper.from_entity_to_schema_campaign_feedback.return_value = expected_response

        use_case = GetCampaignFeedbackStatsUseCase(
            uow=dummy_uow,
            repository=repository,
            campaigns_repository=campaigns_repository,
            mapper=mapper,
        )
        result = await use_case.execute(campaign_id)
        assert result == expected_response
        campaigns_repository.get_by_id.assert_called_once_with(campaign_id)
        repository.get_campaign_feedbacks.assert_called_once_with(campaign_id)
        mapper.from_entity_to_schema_campaign_feedback.assert_called_once_with(
            dummy_feedback_entities
        )

    @pytest.mark.asyncio
    async def test_execute_campaign_not_found(self, dummy_uow: AsyncMock):
        campaign_id = uuid4()
        campaigns_repository = AsyncMock()
        campaigns_repository.get_by_id.side_effect = CampaignNotFoundException(
            "Campaign not found"
        )
        repository = AsyncMock()
        mapper = MagicMock()

        use_case = GetCampaignFeedbackStatsUseCase(
            uow=dummy_uow,
            repository=repository,
            campaigns_repository=campaigns_repository,
            mapper=mapper,
        )
        with pytest.raises(CampaignNotFoundException) as exc:
            await use_case.execute(campaign_id)
        assert "Campaign not found" in str(exc.value)

    @pytest.mark.asyncio
    async def test_execute_unexpected_error(self, dummy_uow: AsyncMock):
        campaign_id = uuid4()
        campaigns_repository = AsyncMock()
        campaigns_repository.get_by_id.return_value = MagicMock()
        repository = AsyncMock()
        repository.get_campaign_feedbacks.side_effect = Exception("Unexpected error")
        mapper = MagicMock()

        use_case = GetCampaignFeedbackStatsUseCase(
            uow=dummy_uow,
            repository=repository,
            campaigns_repository=campaigns_repository,
            mapper=mapper,
        )
        with pytest.raises(StatisticsRepositoryError) as exc:
            await use_case.execute(campaign_id)
        assert "Unexpected error:" in str(exc.value)
