from uuid import UUID

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from src.adapters.telegram.common.constants import (
    CALLBACK_BACK_TO_CAMPAIGN,
    CALLBACK_CONFIRM,
    CALLBACK_EDIT_TARGETING,
)
from src.adapters.telegram.common.states import TargetingStates
from src.adapters.telegram.common.utils import check_user, get_session_with_advertiser
from src.adapters.telegram.keyboards.campaigns import (
    CONFIRM_KEYBOARD,
    get_campaign_management_keyboard,
)
from src.adapters.telegram.messages.campaigns import Messages
from src.application.campaigns.dtos import CampaignUpdateRequest, TargetingSchema
from src.common.enums import TargetingGender
from src.core.uow import SQLAlchemyUow
from src.infrastructure.campaigns.mappers import CampaignsMapper
from src.infrastructure.campaigns.repositories import CampaignsRepository

router = Router(name="campaign_targeting_handlers")


@router.callback_query(F.data.startswith(CALLBACK_EDIT_TARGETING))
async def start_targeting_edit(callback: CallbackQuery, state: FSMContext) -> None:
    campaign_id = callback.data.split(":")[1]
    await state.update_data(campaign_id=campaign_id)
    await state.set_state(TargetingStates.entering_gender)
    await callback.message.edit_text(Messages.PROMPTS["enter_gender"])
    await callback.answer()


@router.message(TargetingStates.entering_gender)
async def process_gender(message: Message, state: FSMContext) -> None:
    gender = message.text.upper() if message.text else None
    if gender not in [g.value for g in TargetingGender]:
        await message.answer(Messages.ERROR["campaign"]["invalid_targeting"])
        return

    await state.update_data(gender=gender)
    await state.set_state(TargetingStates.entering_age_from)
    await message.answer(Messages.PROMPTS["enter_age_from"])


@router.message(TargetingStates.entering_age_from)
async def process_age_from(message: Message, state: FSMContext) -> None:
    try:
        age_from = int(message.text) if message.text else None
        if age_from and age_from < 0:
            raise ValueError()

        await state.update_data(age_from=age_from)
        await state.set_state(TargetingStates.entering_age_to)
        await message.answer(Messages.PROMPTS["enter_age_to"])
    except ValueError:
        await message.answer(Messages.ERROR["campaign"]["invalid_targeting"])


@router.message(TargetingStates.entering_age_to)
async def process_age_to(message: Message, state: FSMContext) -> None:
    try:
        age_to = int(message.text) if message.text else None
        data = await state.get_data()
        age_from = data.get("age_from")

        if age_to and (age_to < 0 or (age_from and age_to < age_from)):
            raise ValueError()

        await state.update_data(age_to=age_to)
        await state.set_state(TargetingStates.entering_location)
        await message.answer(Messages.PROMPTS["enter_location"])
    except ValueError:
        await message.answer(Messages.ERROR["campaign"]["invalid_targeting"])


@router.message(TargetingStates.entering_location)
async def process_location(message: Message, state: FSMContext) -> None:
    location = message.text.strip() if message.text else None
    data = await state.get_data()

    targeting = TargetingSchema(
        gender=data.get("gender"),
        age_from=data.get("age_from"),
        age_to=data.get("age_to"),
        location=location,
    )

    await state.update_data(targeting=targeting.dict())
    await state.set_state(TargetingStates.confirming_targeting)
    await message.answer(
        Messages.PROMPTS["confirm_targeting"].format(
            gender=targeting.gender or "Все",
            age_from=targeting.age_from or "Не указано",
            age_to=targeting.age_to or "Не указано",
            location=targeting.location or "Не указано",
        ),
        reply_markup=CONFIRM_KEYBOARD,
    )


@router.callback_query(
    TargetingStates.confirming_targeting,
    F.data == CALLBACK_CONFIRM,
)
async def confirm_targeting(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    campaign_id = UUID(data["campaign_id"])
    targeting = TargetingSchema(**data["targeting"])

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
                update_data = CampaignUpdateRequest(targeting=targeting)
                await repository.update_campaign(
                    advertiser_id=advertiser.id,
                    campaign_id=campaign_id,
                    data=update_data,
                )
                await uow.commit()

                keyboard = get_campaign_management_keyboard(str(campaign_id))
                await callback.message.edit_text(
                    Messages.SUCCESS["targeting_updated"],
                    reply_markup=keyboard,
                )
        except Exception as e:
            await callback.message.edit_text(
                Messages.ERROR["db_error"]["campaign_update"].format(error=str(e))
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
