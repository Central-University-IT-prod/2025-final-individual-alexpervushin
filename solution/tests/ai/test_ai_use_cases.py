from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.ai.dtos import AdvertisementGenerationResponse
from src.application.ai.use_cases import GenerateAdUseCase, GenerateImageUseCase
from src.domain.ai.exceptions import AIError, AIImageGenerationError, AIRequestError


class DummyAdvertiser:
    def __init__(self, name: str):
        self.name = name


class DummyCampaign:
    def __init__(self, ad_title: str, ad_text: str):
        self.ad_title = ad_title
        self.ad_text = ad_text


@pytest.mark.asyncio
class TestGenerateAdUseCase:
    async def test_execute_plain_text_success(self):
        advertiser_id = uuid4()
        ad_title = "Test Ad Title"
        dummy_advertiser = DummyAdvertiser("Test Advertiser")
        plain_text = "Simple ad text"
        ai_response = {"generated_text": plain_text}

        uow = AsyncMock()
        advertisers_repository = AsyncMock()
        advertisers_repository.get_by_id.return_value = dummy_advertiser
        ai_service = AsyncMock()
        ai_service.generate_ad.return_value = ai_response

        use_case = GenerateAdUseCase(uow, advertisers_repository, ai_service)

        result = await use_case.execute(advertiser_id, ad_title)

        assert isinstance(result, AdvertisementGenerationResponse)
        assert result.generated_text == plain_text
        advertisers_repository.get_by_id.assert_called_once_with(advertiser_id)
        ai_service.generate_ad.assert_called_once_with(
            advertiser_name=dummy_advertiser.name, ad_title=ad_title
        )

    async def test_execute_markdown_json_success(self):
        advertiser_id = uuid4()
        ad_title = "Special Ad Title"
        dummy_advertiser = DummyAdvertiser("Advertiser XYZ")
        markdown_response = '```json\n{"generated_text": "Formatted ad text"}```'
        ai_response = {"generated_text": markdown_response}

        uow = AsyncMock()
        advertisers_repository = AsyncMock()
        advertisers_repository.get_by_id.return_value = dummy_advertiser
        ai_service = AsyncMock()
        ai_service.generate_ad.return_value = ai_response

        use_case = GenerateAdUseCase(uow, advertisers_repository, ai_service)

        result = await use_case.execute(advertiser_id, ad_title)

        assert result.generated_text == "Formatted ad text"

    async def test_execute_ai_error(self):
        advertiser_id = uuid4()
        ad_title = "Ad Title"
        dummy_advertiser = DummyAdvertiser("Advertiser ABC")
        error_message = "AI processing error"

        uow = AsyncMock()
        advertisers_repository = AsyncMock()
        advertisers_repository.get_by_id.return_value = dummy_advertiser
        ai_service = AsyncMock()
        ai_service.generate_ad.side_effect = AIError(error_message)

        use_case = GenerateAdUseCase(uow, advertisers_repository, ai_service)

        with pytest.raises(AIError) as exc_info:
            await use_case.execute(advertiser_id, ad_title)
        assert error_message in str(exc_info.value)

    async def test_execute_generic_exception(self):
        advertiser_id = uuid4()
        ad_title = "Ad Title"

        uow = AsyncMock()
        advertisers_repository = AsyncMock()
        advertisers_repository.get_by_id.side_effect = Exception("Repository failure")
        ai_service = AsyncMock()

        use_case = GenerateAdUseCase(uow, advertisers_repository, ai_service)

        with pytest.raises(AIRequestError) as exc_info:
            await use_case.execute(advertiser_id, ad_title)
        assert "Unexpected error during ad generation:" in str(exc_info.value)
        assert "Repository failure" in str(exc_info.value)


@pytest.mark.asyncio
class TestGenerateImageUseCase:
    async def test_execute_success(self):
        campaign_id = uuid4()
        dummy_campaign = DummyCampaign("Campaign Title", "Campaign Text")
        file_response = MagicMock(name="FileResponse")

        uow = AsyncMock()
        ai_service = AsyncMock()
        ai_service.generate_image.return_value = file_response
        campaigns_repository = AsyncMock()
        campaigns_repository.get_by_id.return_value = dummy_campaign

        use_case = GenerateImageUseCase(uow, ai_service, campaigns_repository)

        result = await use_case.execute(campaign_id)

        assert result == file_response
        campaigns_repository.get_by_id.assert_called_once_with(campaign_id)
        ai_service.generate_image.assert_called_once_with(
            ad_title=dummy_campaign.ad_title, ad_text=dummy_campaign.ad_text
        )

    async def test_execute_ai_error(self):
        campaign_id = uuid4()
        dummy_campaign = DummyCampaign("Campaign Title", "Campaign Text")
        error_message = "AI image generation error"

        uow = AsyncMock()
        ai_service = AsyncMock()
        ai_service.generate_image.side_effect = AIError(error_message)
        campaigns_repository = AsyncMock()
        campaigns_repository.get_by_id.return_value = dummy_campaign

        use_case = GenerateImageUseCase(uow, ai_service, campaigns_repository)

        with pytest.raises(AIError) as exc_info:
            await use_case.execute(campaign_id)
        assert error_message in str(exc_info.value)

    async def test_execute_generic_exception(self):
        campaign_id = uuid4()
        dummy_campaign = DummyCampaign("Campaign Title", "Campaign Text")

        uow = AsyncMock()
        ai_service = AsyncMock()
        ai_service.generate_image.side_effect = Exception("Generic image error")
        campaigns_repository = AsyncMock()
        campaigns_repository.get_by_id.return_value = dummy_campaign

        use_case = GenerateImageUseCase(uow, ai_service, campaigns_repository)

        with pytest.raises(AIImageGenerationError) as exc_info:
            await use_case.execute(campaign_id)
        assert "Unexpected error during image generation:" in str(exc_info.value)
        assert "Generic image error" in str(exc_info.value)
