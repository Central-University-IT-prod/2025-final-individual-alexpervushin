from uuid import UUID

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from src.adapters.telegram.common.constants import (
    CALLBACK_BACK_TO_CAMPAIGN,
    CALLBACK_CONFIRM,
    CALLBACK_DELETE_IMAGE,
    CALLBACK_UPLOAD_IMAGE,
)
from src.adapters.telegram.common.states import CampaignImageStates
from src.adapters.telegram.common.utils import check_user, get_session_with_advertiser
from src.adapters.telegram.keyboards.campaigns import (
    get_campaign_management_keyboard,
)
from src.adapters.telegram.messages.campaigns import Messages
from src.core.uow import SQLAlchemyUow
from src.infrastructure.campaigns.mappers import CampaignsMapper
from src.infrastructure.campaigns.repositories import CampaignsRepository

router = Router(name="campaign_image_handlers")


@router.callback_query(F.data.startswith(CALLBACK_UPLOAD_IMAGE))
async def start_image_upload(callback: CallbackQuery, state: FSMContext) -> None:
    campaign_id = callback.data.split(":")[1]
    await state.update_data(campaign_id=campaign_id)
    await state.set_state(CampaignImageStates.uploading_image)
    await callback.message.edit_text(Messages.PROMPTS["upload_image"])
    await callback.answer()


@router.message(CampaignImageStates.uploading_image, F.content_type == "photo")
async def process_image_upload(message: Message, state: FSMContext) -> None:
    if not message.photo:
        await message.answer(Messages.ERROR["campaign"]["image_upload"])
        return

    data = await state.get_data()
    campaign_id = UUID(data["campaign_id"])

    user = await check_user(message)
    if not user:
        await message.answer(Messages.ERROR["user_not_found"])
        return

    async with get_session_with_advertiser(user.id) as (session, _, _, advertiser):
        if not advertiser:
            await message.answer(Messages.ERROR["not_registered"])
            return

        mapper = CampaignsMapper()
        repository = CampaignsRepository(session, mapper)
        uow = SQLAlchemyUow(session)

        try:
            async with uow:
                image = message.photo[-1]
                file = await message.bot.get_file(image.file_id)
                file_path = file.file_path

                image_url = "example.com/image.jpg"

                await repository.update_campaign_image(
                    advertiser_id=advertiser.id,
                    campaign_id=campaign_id,
                    image_url=image_url,
                )
                await uow.commit()

                keyboard = get_campaign_management_keyboard(str(campaign_id))
                await message.answer(
                    Messages.SUCCESS["image_uploaded"].format(image_url=image_url),
                    reply_markup=keyboard,
                )
        except Exception as e:
            await message.answer(
                Messages.ERROR["db_error"]["campaign_update"].format(error=str(e))
            )

    await state.clear()


@router.callback_query(F.data.startswith(CALLBACK_DELETE_IMAGE))
async def confirm_image_delete(callback: CallbackQuery, state: FSMContext) -> None:
    campaign_id = callback.data.split(":")[1]
    await state.update_data(campaign_id=campaign_id)
    await state.set_state(CampaignImageStates.confirming_delete)
    await callback.message.edit_text(
        Messages.PROMPTS["confirm_delete_image"],
        reply_markup=CONFIRM_KEYBOARD,
    )
    await callback.answer()


@router.callback_query(
    CampaignImageStates.confirming_delete,
    F.data == CALLBACK_CONFIRM,
)
async def process_image_delete(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    campaign_id = UUID(data["campaign_id"])

    user = await check_user(callback.message)
    if not user:
        await callback.message.answer(Messages.ERROR["user_not_found"])
        return

    async with get_session_with_advertiser(user.id) as (session, _, _, advertiser):
        if not advertiser:
            await callback.message.answer(Messages.ERROR["not_registered"])
            return

        mapper = CampaignsMapper()
        repository = CampaignsRepository(session, mapper)
        uow = SQLAlchemyUow(session)

        try:
            async with uow:
                await repository.delete_campaign_image(
                    advertiser_id=advertiser.id,
                    campaign_id=campaign_id,
                )
                await uow.commit()

                keyboard = get_campaign_management_keyboard(str(campaign_id))
                await callback.message.edit_text(
                    Messages.SUCCESS["image_deleted"],
                    reply_markup=keyboard,
                )
        except Exception as e:
            await callback.message.edit_text(
                Messages.ERROR["db_error"]["campaign_delete"].format(error=str(e))
            )

    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith(CALLBACK_BACK_TO_CAMPAIGN))
async def process_back_to_campaign(callback: CallbackQuery, state: FSMContext) -> None:
    campaign_id = callback.data.split(":")[1]
    keyboard = get_campaign_management_keyboard(campaign_id)
    await callback.message.edit_text(
        Messages.PROMPTS["campaign_management"],
        reply_markup=keyboard,
    )
    await callback.answer()
