from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import UploadFile

from src.application.campaigns.dtos import (
    CampaignCreateRequest,
    CampaignUpdateRequest,
    ImageUploadResponse,
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
from src.domain.campaigns.exceptions import (
    CampaignForbiddenError,
    CampaignModerationError,
    CampaignNotFoundException,
)


class FakeModerationResult:
    def __init__(self, forbidden: bool):
        self.contains_forbidden_words = forbidden


@pytest.mark.asyncio
class TestCreateCampaignUseCase:
    async def test_execute_success(self):
        advertiser_id = uuid4()
        uow = AsyncMock()
        uow.__aenter__.return_value = uow
        mapper = MagicMock()
        repository = AsyncMock()
        moderation_service = AsyncMock()
        advertisers_repository = AsyncMock()
        settings = MagicMock()
        settings.ai_moderation_enabled = True

        moderation_service.check_forbidden_words.return_value = FakeModerationResult(
            False
        )
        advertisers_repository.get_by_id.return_value = MagicMock()

        dummy_campaign_entity = MagicMock()
        mapper.from_create_schema_to_entity.return_value = dummy_campaign_entity
        repository.create.return_value = dummy_campaign_entity
        dummy_dto = {"campaign_id": "dummy_id", "ad_title": "Test Campaign"}
        mapper.from_entity_to_schema.return_value = dummy_dto

        campaign_data = CampaignCreateRequest(
            ad_title="Test Campaign",
            ad_text="Test text",
            impressions_limit=1000,
            clicks_limit=100,
            cost_per_impression=0.5,
            cost_per_click=1.0,
            start_date=1,
            end_date=2,
            targeting=None,
        )

        use_case = CreateCampaignUseCase(
            uow=uow,
            repository=repository,
            mapper=mapper,
            moderation_service=moderation_service,
            advertisers_repository=advertisers_repository,
            settings=settings,
        )

        result = await use_case.execute(advertiser_id, campaign_data)
        assert result == dummy_dto
        advertisers_repository.get_by_id.assert_called_once_with(advertiser_id)
        assert moderation_service.check_forbidden_words.call_count >= 2
        repository.create.assert_called_once_with(dummy_campaign_entity)
        mapper.from_create_schema_to_entity.assert_called_once_with(campaign_data)
        mapper.from_entity_to_schema.assert_called_once_with(dummy_campaign_entity)
        uow.commit.assert_called_once()

    async def test_execute_title_moderation_error(self):
        advertiser_id = uuid4()
        uow = AsyncMock()
        uow.__aenter__.return_value = uow
        mapper = MagicMock()
        repository = AsyncMock()
        moderation_service = AsyncMock()
        advertisers_repository = AsyncMock()
        settings = MagicMock()
        settings.ai_moderation_enabled = True

        moderation_service.check_forbidden_words.side_effect = [
            FakeModerationResult(True),
            FakeModerationResult(False),
        ]
        campaign_data = CampaignCreateRequest(
            ad_title="Bad Title",
            ad_text="Test text",
            impressions_limit=1000,
            clicks_limit=100,
            cost_per_impression=0.5,
            cost_per_click=1.0,
            start_date=1,
            end_date=2,
            targeting=None,
        )
        use_case = CreateCampaignUseCase(
            uow=uow,
            repository=repository,
            mapper=mapper,
            moderation_service=moderation_service,
            advertisers_repository=advertisers_repository,
            settings=settings,
        )
        with pytest.raises(CampaignModerationError):
            await use_case.execute(advertiser_id, campaign_data)


@pytest.mark.asyncio
class TestGetCampaignsUseCase:
    async def test_execute_success(self):
        advertiser_id = uuid4()
        uow = AsyncMock()
        uow.__aenter__.return_value = uow
        mapper = MagicMock()
        repository = AsyncMock()
        advertisers_repository = AsyncMock()

        campaign1 = MagicMock()
        campaign2 = MagicMock()
        repository.get_all.return_value = [campaign1, campaign2]
        mapper.from_entity_to_schema.side_effect = ["dto1", "dto2"]
        advertisers_repository.get_by_id.return_value = MagicMock()

        use_case = GetCampaignsUseCase(
            uow=uow,
            repository=repository,
            mapper=mapper,
            advertisers_repository=advertisers_repository,
        )
        result = await use_case.execute(advertiser_id, size=10, page=1)
        assert result == ["dto1", "dto2"]
        advertisers_repository.get_by_id.assert_called_once_with(advertiser_id)


@pytest.mark.asyncio
class TestGetCampaignByIdUseCase:
    async def test_execute_success(self):
        advertiser_id = uuid4()
        campaign_id = uuid4()
        uow = AsyncMock()
        uow.__aenter__.return_value = uow
        advertisers_repository = AsyncMock()
        repository = AsyncMock()
        mapper = MagicMock()

        campaign_entity = MagicMock()
        campaign_entity.advertiser_id = advertiser_id
        repository.get_by_id.return_value = campaign_entity
        mapper.from_entity_to_schema.return_value = {"campaign_id": str(campaign_id)}

        use_case = GetCampaignByIdUseCase(
            uow=uow,
            repository=repository,
            mapper=mapper,
            advertisers_repository=advertisers_repository,
        )
        result = await use_case.execute(advertiser_id, campaign_id)
        assert result == {"campaign_id": str(campaign_id)}
        advertisers_repository.get_by_id.assert_called_once_with(advertiser_id)

    async def test_execute_forbidden_error(self):
        advertiser_id = uuid4()
        campaign_id = uuid4()
        uow = AsyncMock()
        uow.__aenter__.return_value = uow
        advertisers_repository = AsyncMock()
        repository = AsyncMock()
        mapper = MagicMock()

        campaign_entity = MagicMock()
        campaign_entity.advertiser_id = uuid4()
        repository.get_by_id.return_value = campaign_entity

        use_case = GetCampaignByIdUseCase(
            uow=uow,
            repository=repository,
            mapper=mapper,
            advertisers_repository=advertisers_repository,
        )
        with pytest.raises(CampaignForbiddenError):
            await use_case.execute(advertiser_id, campaign_id)


@pytest.mark.asyncio
class TestUpdateCampaignUseCase:
    async def test_execute_success(self):
        advertiser_id = uuid4()
        campaign_id = uuid4()
        uow = AsyncMock()
        uow.__aenter__.return_value = uow
        mapper = MagicMock()
        repository = AsyncMock()
        moderation_service = AsyncMock()
        advertisers_repository = AsyncMock()
        settings = MagicMock()
        settings.ai_moderation_enabled = True

        moderation_service.check_forbidden_words.return_value = FakeModerationResult(
            False
        )
        dummy_update_entity = MagicMock()
        mapper.from_update_schema_to_entity.return_value = dummy_update_entity
        repository.update.return_value = dummy_update_entity
        mapper.from_entity_to_schema.return_value = {"updated": True}
        update_data = CampaignUpdateRequest(
            ad_title="Updated Campaign",
            ad_text="Updated text",
            cost_per_impression=0.6,
            cost_per_click=1.1,
            targeting=None,
        )

        use_case = UpdateCampaignUseCase(
            uow=uow,
            repository=repository,
            mapper=mapper,
            moderation_service=moderation_service,
            advertisers_repository=advertisers_repository,
            settings=settings,
        )
        result = await use_case.execute(advertiser_id, campaign_id, update_data)
        assert result == {"updated": True}
        advertisers_repository.get_by_id.assert_called_once_with(advertiser_id)
        mapper.from_update_schema_to_entity.assert_called_once_with(update_data)
        repository.update.assert_called_once_with(dummy_update_entity)
        uow.commit.assert_called_once()

    async def test_execute_title_moderation_error(self):
        advertiser_id = uuid4()
        campaign_id = uuid4()
        uow = AsyncMock()
        uow.__aenter__.return_value = uow
        mapper = MagicMock()
        repository = AsyncMock()
        moderation_service = AsyncMock()
        advertisers_repository = AsyncMock()
        settings = MagicMock()
        settings.ai_moderation_enabled = True

        moderation_service.check_forbidden_words.side_effect = [
            FakeModerationResult(True),
            FakeModerationResult(False),
        ]
        update_data = CampaignUpdateRequest(
            ad_title="Bad Title",
            ad_text="Updated text",
            cost_per_impression=0.6,
            cost_per_click=1.1,
            targeting=None,
        )
        use_case = UpdateCampaignUseCase(
            uow=uow,
            repository=repository,
            mapper=mapper,
            moderation_service=moderation_service,
            advertisers_repository=advertisers_repository,
            settings=settings,
        )
        with pytest.raises(CampaignModerationError):
            await use_case.execute(advertiser_id, campaign_id, update_data)


@pytest.mark.asyncio
class TestUploadCampaignImageUseCase:
    async def test_execute_success(self):
        advertiser_id = uuid4()
        campaign_id = uuid4()
        uow = AsyncMock()
        uow.__aenter__.return_value = uow
        advertisers_repository = AsyncMock()
        repository = AsyncMock()
        mapper = MagicMock()
        minio_service = AsyncMock()

        campaign_entity = MagicMock()
        campaign_entity.advertiser_id = advertiser_id
        repository.get_by_id.return_value = campaign_entity
        minio_service.get_image_url.return_value = "http://image.url"

        image_file = AsyncMock(spec=UploadFile)
        image_file.read.return_value = b"binary image data"
        image_file.close.return_value = None

        use_case = UploadCampaignImageUseCase(
            uow=uow,
            repository=repository,
            mapper=mapper,
            minio_service=minio_service,
            advertisers_repository=advertisers_repository,
        )
        result = await use_case.execute(advertiser_id, campaign_id, image_file)
        assert isinstance(result, ImageUploadResponse)
        assert result.image_url == "http://image.url"
        advertisers_repository.get_by_id.assert_called_once_with(advertiser_id)
        repository.get_by_id.assert_called_once_with(campaign_id)
        minio_service.upload_image.assert_called_once_with(
            campaign_id, b"binary image data"
        )
        minio_service.get_image_url.assert_called_once_with(campaign_id)
        repository.update_image_url.assert_called_once_with(
            campaign_id, "http://image.url"
        )
        uow.commit.assert_called_once()
        image_file.close.assert_called_once()

    async def test_execute_forbidden_error(self):
        advertiser_id = uuid4()
        campaign_id = uuid4()
        uow = AsyncMock()
        advertisers_repository = AsyncMock()
        repository = AsyncMock()
        mapper = MagicMock()
        minio_service = AsyncMock()

        campaign_entity = MagicMock()
        campaign_entity.advertiser_id = uuid4()
        repository.get_by_id.return_value = campaign_entity

        image_file = AsyncMock(spec=UploadFile)
        image_file.read.return_value = b"data"
        image_file.close.return_value = None

        use_case = UploadCampaignImageUseCase(
            uow=uow,
            repository=repository,
            mapper=mapper,
            minio_service=minio_service,
            advertisers_repository=advertisers_repository,
        )
        with pytest.raises(CampaignForbiddenError):
            await use_case.execute(advertiser_id, campaign_id, image_file)


@pytest.mark.asyncio
class TestDeleteCampaignImageUseCase:
    async def test_execute_success(self):
        advertiser_id = uuid4()
        campaign_id = uuid4()
        uow = AsyncMock()
        uow.__aenter__.return_value = uow
        advertisers_repository = AsyncMock()
        repository = AsyncMock()
        minio_service = AsyncMock()

        campaign_entity = MagicMock()
        campaign_entity.advertiser_id = advertiser_id
        repository.get_by_id.return_value = campaign_entity

        use_case = DeleteCampaignImageUseCase(
            uow=uow,
            repository=repository,
            minio_service=minio_service,
            advertisers_repository=advertisers_repository,
        )
        await use_case.execute(advertiser_id, campaign_id)
        advertisers_repository.get_by_id.assert_called_once_with(advertiser_id)
        repository.get_by_id.assert_called_once_with(campaign_id)
        minio_service.delete_image.assert_called_once_with(campaign_id)
        repository.update_image_url.assert_called_once_with(campaign_id, None)
        uow.commit.assert_called_once()

    async def test_execute_forbidden_error(self):
        advertiser_id = uuid4()
        campaign_id = uuid4()
        uow = AsyncMock()
        advertisers_repository = AsyncMock()
        repository = AsyncMock()
        minio_service = AsyncMock()

        campaign_entity = MagicMock()
        campaign_entity.advertiser_id = uuid4()
        repository.get_by_id.return_value = campaign_entity

        use_case = DeleteCampaignImageUseCase(
            uow=uow,
            repository=repository,
            minio_service=minio_service,
            advertisers_repository=advertisers_repository,
        )
        with pytest.raises(CampaignForbiddenError):
            await use_case.execute(advertiser_id, campaign_id)


@pytest.mark.asyncio
class TestDeleteCampaignUseCase:
    async def test_execute_success(self):
        advertiser_id = uuid4()
        campaign_id = uuid4()
        uow = AsyncMock()
        uow.__aenter__.return_value = uow
        advertisers_repository = AsyncMock()
        repository = AsyncMock()
        minio_service = AsyncMock()

        campaign_entity = MagicMock()
        campaign_entity.advertiser_id = advertiser_id
        campaign_entity.image_url = "some_url"
        repository.get_by_id.return_value = campaign_entity

        use_case = DeleteCampaignUseCase(
            uow=uow,
            repository=repository,
            minio_service=minio_service,
            advertisers_repository=advertisers_repository,
        )
        await use_case.execute(advertiser_id, campaign_id)
        advertisers_repository.get_by_id.assert_called_once_with(advertiser_id)
        repository.get_by_id.assert_called_once_with(campaign_id)
        minio_service.delete_image.assert_called_once_with(campaign_id)
        repository.delete.assert_called_once_with(
            advertiser_id=advertiser_id, campaign_id=campaign_id
        )
        uow.commit.assert_called_once()

    async def test_execute_forbidden_error(self):
        advertiser_id = uuid4()
        campaign_id = uuid4()
        uow = AsyncMock()
        advertisers_repository = AsyncMock()
        repository = AsyncMock()
        minio_service = AsyncMock()

        campaign_entity = MagicMock()
        campaign_entity.advertiser_id = uuid4()
        repository.get_by_id.return_value = campaign_entity

        use_case = DeleteCampaignUseCase(
            uow=uow,
            repository=repository,
            minio_service=minio_service,
            advertisers_repository=advertisers_repository,
        )
        with pytest.raises(CampaignForbiddenError):
            await use_case.execute(advertiser_id, campaign_id)


@pytest.mark.asyncio
class TestGetCampaignsFromYandexUseCase:
    async def test_execute_success(self):
        advertiser_id = uuid4()
        uow = AsyncMock()
        uow.__aenter__.return_value = uow
        yandex_service = AsyncMock()
        mapper = MagicMock()

        campaign1 = MagicMock()
        campaign2 = MagicMock()
        yandex_service.get_campaign_entities.return_value = [campaign1, campaign2]
        mapper.from_entity_to_schema.side_effect = ["dto1", "dto2"]

        use_case = GetCampaignsFromYandexUseCase(
            uow=uow,
            yandex_service=yandex_service,
            mapper=mapper,
        )
        result = await use_case.execute(advertiser_id, token="dummy_token")
        assert result == ["dto1", "dto2"]
        yandex_service.get_campaign_entities.assert_called_once_with(
            advertiser_id=advertiser_id, token="dummy_token"
        )


@pytest.mark.asyncio
class TestCreateCampaignFromYandexUseCase:
    async def test_execute_success(self):
        advertiser_id = uuid4()
        uow = AsyncMock()
        uow.__aenter__.return_value = uow
        yandex_service = AsyncMock()
        repository = AsyncMock()
        mapper = MagicMock()
        advertisers_repository = AsyncMock()

        campaign1 = MagicMock()
        campaign2 = MagicMock()
        yandex_service.get_campaign_entities.return_value = [campaign1, campaign2]
        mapper.from_entity_to_schema.side_effect = ["dto1", "dto2"]

        use_case = CreateCampaignFromYandexUseCase(
            uow=uow,
            yandex_service=yandex_service,
            repository=repository,
            mapper=mapper,
            advertisers_repository=advertisers_repository,
        )
        result = await use_case.execute(advertiser_id, token="dummy_token")
        assert repository.create.call_count == 2
        assert result == ["dto1", "dto2"]
        uow.commit.assert_called()

    async def test_execute_no_campaigns_error(self):
        advertiser_id = uuid4()
        uow = AsyncMock()
        uow.__aenter__.return_value = uow
        yandex_service = AsyncMock()
        repository = AsyncMock()
        mapper = MagicMock()
        advertisers_repository = AsyncMock()

        yandex_service.get_campaign_entities.return_value = []
        use_case = CreateCampaignFromYandexUseCase(
            uow=uow,
            yandex_service=yandex_service,
            repository=repository,
            mapper=mapper,
            advertisers_repository=advertisers_repository,
        )
        with pytest.raises(CampaignNotFoundException):
            await use_case.execute(advertiser_id, token="dummy_token")
