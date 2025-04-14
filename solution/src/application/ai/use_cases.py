import json
from uuid import UUID

from fastapi.responses import FileResponse
from src.application.ai.dtos import AdvertisementGenerationResponse
from src.core.uow import AbstractUow
from src.domain.advertisers.interfaces import (
    AdvertisersRepositoryProtocol,
)
from src.domain.ai.exceptions import AIError, AIImageGenerationError, AIRequestError
from src.domain.ai.interfaces import AIServiceProtocol
from src.domain.campaigns.interfaces import CampaignsRepositoryProtocol


class GenerateAdUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        advertisers_repository: AdvertisersRepositoryProtocol,
        ai_service: AIServiceProtocol,
    ):
        self.uow = uow
        self.advertisers_repository = advertisers_repository
        self.ai_service = ai_service

    def _clean_markdown_response(self, text: str) -> str:
        if not (text.startswith("```") and text.endswith("```")):
            return text

        cleaned_text = text.strip("```")

        if "\n" in cleaned_text:
            cleaned_text = cleaned_text.split("\n", 1)[1]

        try:
            parsed_json = json.loads(cleaned_text)
            if "generated_text" in parsed_json:
                return parsed_json["generated_text"]
        except Exception:
            pass

        return cleaned_text

    async def execute(
        self, advertiser_id: UUID, ad_title: str
    ) -> AdvertisementGenerationResponse:
        try:
            advertiser = await self.advertisers_repository.get_by_id(advertiser_id)

            ai_response = await self.ai_service.generate_ad(
                advertiser_name=advertiser.name, ad_title=ad_title
            )

            cleaned_text = self._clean_markdown_response(ai_response["generated_text"])
            return AdvertisementGenerationResponse(generated_text=cleaned_text)
        except AIError as e:
            raise AIError(str(e))
        except Exception as e:
            raise AIRequestError(f"Unexpected error during ad generation: {str(e)}")


class GenerateImageUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        ai_service: AIServiceProtocol,
        campaigns_repository: CampaignsRepositoryProtocol,
    ):
        self.uow = uow
        self.ai_service = ai_service
        self.campaigns_repository = campaigns_repository

    async def execute(self, campaign_id: UUID) -> FileResponse:
        try:
            campaign = await self.campaigns_repository.get_by_id(campaign_id)
            return await self.ai_service.generate_image(
                ad_title=campaign.ad_title,
                ad_text=campaign.ad_text,
            )
        except AIError as e:
            raise AIError(str(e))
        except Exception as e:
            raise AIImageGenerationError(
                f"Unexpected error during image generation: {str(e)}"
            )
