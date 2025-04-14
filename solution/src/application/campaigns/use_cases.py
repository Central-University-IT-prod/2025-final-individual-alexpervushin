from typing import List, Optional
from uuid import UUID

from fastapi import UploadFile
from src.application.campaigns.dtos import (
    CampaignCreateRequest,
    CampaignResponse,
    CampaignUpdateRequest,
    ImageUploadResponse,
)
from src.core.settings import Settings
from src.core.uow import AbstractUow
from src.domain.advertisers.exceptions import AdvertiserNotFoundException
from src.domain.advertisers.interfaces import AdvertisersRepositoryProtocol
from src.domain.campaigns.exceptions import (
    CampaignForbiddenError,
    CampaignImageUploadError,
    CampaignModerationError,
    CampaignNotFoundException,
    CampaignRepositoryError,
)
from src.domain.campaigns.interfaces import (
    CampaignsRepositoryProtocol,
    YandexDirectServiceProtocol,
)
from src.domain.moderation.interfaces import ModerationServiceProtocol
from src.domain.storage.interfaces import MinioServiceProtocol
from src.infrastructure.campaigns.mappers import CampaignsMapper


class CreateCampaignUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: CampaignsRepositoryProtocol,
        mapper: CampaignsMapper,
        moderation_service: ModerationServiceProtocol,
        advertisers_repository: AdvertisersRepositoryProtocol,
        settings: Settings,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._mapper = mapper
        self._moderation_service = moderation_service
        self._settings = settings
        self._advertisers_repository = advertisers_repository

    async def execute(
        self, advertiser_id: UUID, data: CampaignCreateRequest
    ) -> Optional[CampaignResponse]:
        try:
            async with self._uow:
                await self._advertisers_repository.get_by_id(advertiser_id)

                title_moderation_result = (
                    await self._moderation_service.check_forbidden_words(
                        data.ad_title,
                        check_database=True,
                        check_ai=self._settings.ai_moderation_enabled,
                    )
                )

                if title_moderation_result.contains_forbidden_words:
                    raise CampaignModerationError(
                        "Название объявления содержит запрещенные слова"
                    )

                text_moderation_result = (
                    await self._moderation_service.check_forbidden_words(
                        data.ad_text,
                        check_database=True,
                        check_ai=self._settings.ai_moderation_enabled,
                    )
                )

                if text_moderation_result.contains_forbidden_words:
                    raise CampaignModerationError(
                        "Текст объявления содержит запрещенные слова"
                    )

                campaign_entity = self._mapper.from_create_schema_to_entity(data)
                campaign_entity.advertiser_id = advertiser_id
                campaign_entity = await self._repository.create(campaign_entity)
                await self._uow.commit()
                return self._mapper.from_entity_to_schema(campaign_entity)
        except AdvertiserNotFoundException as e:
            raise AdvertiserNotFoundException(str(e))
        except CampaignModerationError as e:
            raise CampaignModerationError(str(e))
        except CampaignRepositoryError as e:
            raise CampaignRepositoryError(str(e))
        except Exception as e:
            raise CampaignRepositoryError(f"Unexpected error: {str(e)}")


class GetCampaignsUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: CampaignsRepositoryProtocol,
        mapper: CampaignsMapper,
        advertisers_repository: AdvertisersRepositoryProtocol,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._mapper = mapper
        self._advertisers_repository = advertisers_repository

    async def execute(
        self, advertiser_id: UUID, size: Optional[int], page: Optional[int]
    ) -> List[CampaignResponse]:
        try:
            async with self._uow:
                await self._advertisers_repository.get_by_id(advertiser_id)

                campaigns = await self._repository.get_all(advertiser_id, size, page)
                return [
                    self._mapper.from_entity_to_schema(campaign)
                    for campaign in campaigns
                ]
        except AdvertiserNotFoundException as e:
            raise AdvertiserNotFoundException(str(e))
        except CampaignRepositoryError as e:
            raise CampaignRepositoryError(str(e))
        except Exception as e:
            raise CampaignRepositoryError(f"Unexpected error: {str(e)}")


class GetCampaignByIdUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: CampaignsRepositoryProtocol,
        mapper: CampaignsMapper,
        advertisers_repository: AdvertisersRepositoryProtocol,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._mapper = mapper
        self._advertisers_repository = advertisers_repository

    async def execute(self, advertiser_id: UUID, campaign_id: UUID) -> CampaignResponse:
        try:
            async with self._uow:
                await self._advertisers_repository.get_by_id(advertiser_id)

                campaign = await self._repository.get_by_id(campaign_id)
                if campaign.advertiser_id != advertiser_id:
                    raise CampaignForbiddenError(
                        "Объявление не принадлежит этому рекламодателю"
                    )
                return self._mapper.from_entity_to_schema(campaign)
        except AdvertiserNotFoundException as e:
            raise AdvertiserNotFoundException(str(e))
        except CampaignNotFoundException as e:
            raise CampaignNotFoundException(str(e))
        except CampaignForbiddenError as e:
            raise CampaignForbiddenError(str(e))
        except CampaignRepositoryError as e:
            raise CampaignRepositoryError(str(e))
        except Exception as e:
            raise CampaignRepositoryError(f"Unexpected error: {str(e)}")


class UpdateCampaignUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: CampaignsRepositoryProtocol,
        mapper: CampaignsMapper,
        moderation_service: ModerationServiceProtocol,
        advertisers_repository: AdvertisersRepositoryProtocol,
        settings: Settings,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._mapper = mapper
        self._moderation_service = moderation_service
        self._settings = settings
        self._advertisers_repository = advertisers_repository

    async def execute(
        self, advertiser_id: UUID, campaign_id: UUID, data: CampaignUpdateRequest
    ) -> CampaignResponse:
        try:
            async with self._uow:
                await self._advertisers_repository.get_by_id(advertiser_id)

                title_moderation_result = (
                    await self._moderation_service.check_forbidden_words(
                        data.ad_title or "",
                        check_database=True,
                        check_ai=self._settings.ai_moderation_enabled,
                    )
                )

                if title_moderation_result.contains_forbidden_words:
                    raise CampaignModerationError(
                        "Название объявления содержит запрещенные слова"
                    )

                text_moderation_result = (
                    await self._moderation_service.check_forbidden_words(
                        data.ad_text or "",
                        check_database=True,
                        check_ai=self._settings.ai_moderation_enabled,
                    )
                )

                if text_moderation_result.contains_forbidden_words:
                    raise CampaignModerationError(
                        "Текст объявления содержит запрещенные слова"
                    )

                campaign_entity = self._mapper.from_update_schema_to_entity(data)
                campaign_entity.id = campaign_id
                campaign_entity.advertiser_id = advertiser_id
                campaign_entity = await self._repository.update(campaign_entity)
                await self._uow.commit()
                return self._mapper.from_entity_to_schema(campaign_entity)
        except AdvertiserNotFoundException as e:
            raise AdvertiserNotFoundException(str(e))
        except CampaignNotFoundException as e:
            raise CampaignNotFoundException(str(e))
        except CampaignModerationError as e:
            raise CampaignModerationError(str(e))
        except CampaignRepositoryError as e:
            raise CampaignRepositoryError(str(e))
        except Exception as e:
            raise CampaignRepositoryError(f"Unexpected error: {str(e)}")


class UploadCampaignImageUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: CampaignsRepositoryProtocol,
        mapper: CampaignsMapper,
        minio_service: MinioServiceProtocol,
        advertisers_repository: AdvertisersRepositoryProtocol,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._mapper = mapper
        self._minio_service = minio_service
        self._advertisers_repository = advertisers_repository

    async def execute(
        self, advertiser_id: UUID, campaign_id: UUID, image: UploadFile
    ) -> ImageUploadResponse:
        try:
            async with self._uow:
                await self._advertisers_repository.get_by_id(advertiser_id)

                campaign_entity = await self._repository.get_by_id(campaign_id)
                if campaign_entity.advertiser_id != advertiser_id:
                    raise CampaignForbiddenError(
                        "Объявление не принадлежит этому рекламодателю"
                    )

                image_data = await image.read()
                try:
                    await self._minio_service.upload_image(campaign_id, image_data)
                    image_url = await self._minio_service.get_image_url(campaign_id)
                except Exception as e:
                    raise CampaignImageUploadError(f"Failed to upload image: {str(e)}")
                finally:
                    await image.close()

                if not image_url:
                    raise CampaignImageUploadError("Failed to generate image URL")

                await self._repository.update_image_url(campaign_id, image_url)
                await self._uow.commit()

                return ImageUploadResponse(image_url=image_url)
        except AdvertiserNotFoundException as e:
            raise AdvertiserNotFoundException(str(e))
        except CampaignNotFoundException as e:
            raise CampaignNotFoundException(str(e))
        except CampaignForbiddenError as e:
            raise CampaignForbiddenError(str(e))
        except CampaignImageUploadError as e:
            raise CampaignImageUploadError(str(e))
        except CampaignRepositoryError as e:
            raise CampaignRepositoryError(str(e))
        except Exception as e:
            raise CampaignRepositoryError(f"Unexpected error: {str(e)}")


class DeleteCampaignImageUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: CampaignsRepositoryProtocol,
        minio_service: MinioServiceProtocol,
        advertisers_repository: AdvertisersRepositoryProtocol,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._minio_service = minio_service
        self._advertisers_repository = advertisers_repository

    async def execute(self, advertiser_id: UUID, campaign_id: UUID) -> None:
        try:
            await self._advertisers_repository.get_by_id(advertiser_id)
            campaign_entity = await self._repository.get_by_id(campaign_id)
            if campaign_entity.advertiser_id != advertiser_id:
                raise CampaignForbiddenError(
                    "Объявление не принадлежит этому рекламодателю"
                )

            await self._minio_service.delete_image(campaign_id)

            async with self._uow:
                await self._repository.update_image_url(campaign_id, None)
                await self._uow.commit()
        except AdvertiserNotFoundException as e:
            raise AdvertiserNotFoundException(str(e))
        except CampaignNotFoundException as e:
            raise CampaignNotFoundException(str(e))
        except CampaignForbiddenError as e:
            raise CampaignForbiddenError(str(e))
        except CampaignRepositoryError as e:
            raise CampaignRepositoryError(str(e))
        except Exception as e:
            raise CampaignRepositoryError(f"Unexpected error: {str(e)}")


class DeleteCampaignUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        repository: CampaignsRepositoryProtocol,
        minio_service: MinioServiceProtocol,
        advertisers_repository: AdvertisersRepositoryProtocol,
    ) -> None:
        self._uow = uow
        self._repository = repository
        self._minio_service = minio_service
        self._advertisers_repository = advertisers_repository

    async def execute(self, advertiser_id: UUID, campaign_id: UUID) -> None:
        try:
            async with self._uow:
                await self._advertisers_repository.get_by_id(advertiser_id)

                campaign_entity = await self._repository.get_by_id(campaign_id)
                if campaign_entity.advertiser_id != advertiser_id:
                    raise CampaignForbiddenError(
                        "Объявление не принадлежит этому рекламодателю"
                    )

                if campaign_entity.image_url:
                    await self._minio_service.delete_image(campaign_id)

                await self._repository.delete(
                    advertiser_id=advertiser_id, campaign_id=campaign_id
                )
                await self._uow.commit()
        except AdvertiserNotFoundException as e:
            raise AdvertiserNotFoundException(str(e))
        except CampaignNotFoundException as e:
            raise CampaignNotFoundException(str(e))
        except CampaignForbiddenError as e:
            raise CampaignForbiddenError(str(e))
        except CampaignRepositoryError as e:
            raise CampaignRepositoryError(str(e))
        except Exception as e:
            raise CampaignRepositoryError(f"Unexpected error: {str(e)}")


class GetCampaignsFromYandexUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        yandex_service: YandexDirectServiceProtocol,
        mapper: CampaignsMapper,
    ) -> None:
        self._uow = uow
        self._yandex_service = yandex_service
        self._mapper = mapper

    async def execute(
        self, advertiser_id: UUID, token: Optional[str] = None
    ) -> List[CampaignResponse]:
        try:
            async with self._uow:
                campaigns = await self._yandex_service.get_campaign_entities(
                    advertiser_id=advertiser_id, token=token
                )
                return [
                    self._mapper.from_entity_to_schema(campaign)
                    for campaign in campaigns
                ]
        except CampaignRepositoryError as e:
            raise CampaignRepositoryError(str(e))
        except Exception as e:
            raise CampaignRepositoryError(f"Unexpected error: {str(e)}")


class CreateCampaignFromYandexUseCase:
    def __init__(
        self,
        uow: AbstractUow,
        yandex_service: YandexDirectServiceProtocol,
        repository: CampaignsRepositoryProtocol,
        mapper: CampaignsMapper,
        advertisers_repository: AdvertisersRepositoryProtocol,
    ) -> None:
        self._uow = uow
        self._yandex_service = yandex_service
        self._repository = repository
        self._mapper = mapper
        self._advertisers_repository = advertisers_repository

    async def execute(
        self, advertiser_id: UUID, token: Optional[str] = None
    ) -> List[CampaignResponse]:
        try:
            async with self._uow:
                await self._advertisers_repository.get_by_id(advertiser_id)

                campaigns = await self._yandex_service.get_campaign_entities(
                    advertiser_id=advertiser_id, token=token
                )
                if not campaigns:
                    raise CampaignNotFoundException("Нет кампаний в Яндекс.Директ")

                for campaign in campaigns:
                    await self._repository.create(campaign)
                    await self._uow.commit()

                return [
                    self._mapper.from_entity_to_schema(campaign)
                    for campaign in campaigns
                ]
        except AdvertiserNotFoundException as e:
            raise AdvertiserNotFoundException(str(e))
        except CampaignNotFoundException as e:
            raise CampaignNotFoundException(str(e))
        except CampaignRepositoryError as e:
            raise CampaignRepositoryError(str(e))
        except Exception as e:
            raise CampaignRepositoryError(f"Unexpected error: {str(e)}")
