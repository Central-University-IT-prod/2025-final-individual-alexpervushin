from uuid import UUID, uuid4

import redis.asyncio as redis
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fastapi import Depends
from src.adapters.telegram.common.constants import (
    BACK_TEXT,
    CALLBACK_BACK_TO_CAMPAIGNS,
    CALLBACK_BACK_TO_MAIN,
    CALLBACK_CONFIRM,
    CALLBACK_DELETE_CAMPAIGN,
    CALLBACK_EDIT_CAMPAIGN,
    CALLBACK_SKIP,
    CREATE_CAMPAIGN_TEXT,
    LIST_CAMPAIGNS_TEXT,
)
from src.adapters.telegram.common.states import (
    CampaignCreationStates,
    CampaignManagementStates,
)
from src.adapters.telegram.common.utils import check_user, get_session_with_advertiser
from src.adapters.telegram.keyboards.campaigns import (
    CAMPAIGN_MANAGEMENT_KEYBOARD,
    CONFIRM_KEYBOARD,
    SKIP_KEYBOARD,
    get_campaign_edit_keyboard,
    get_campaigns_list_keyboard,
)
from src.adapters.telegram.messages.campaigns import Messages
from src.common.enums import TargetingGender
from src.core.redis import get_redis
from src.core.uow import SQLAlchemyUow
from src.domain.campaigns.entities import CampaignEntity
from src.domain.time.interfaces import TimeRepositoryProtocol
from src.infrastructure.campaigns.mappers import CampaignsMapper
from src.infrastructure.campaigns.repositories import CampaignsRepository
from src.infrastructure.time.repositories import TimeRepository

router = Router(name="campaign_handlers")


def get_time_repository(
    redis_client: redis.Redis = Depends(get_redis),
) -> TimeRepositoryProtocol:
    return TimeRepository(redis=redis_client)


@router.message(F.text.in_(["/campaigns", BACK_TEXT]))
async def cmd_campaigns(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(CampaignManagementStates.choosing_action)
    await message.answer(
        Messages.PROMPTS["welcome_campaigns"],
        reply_markup=CAMPAIGN_MANAGEMENT_KEYBOARD,
    )


@router.message(lambda msg: msg.text in [CREATE_CAMPAIGN_TEXT, LIST_CAMPAIGNS_TEXT])
async def handle_campaign_action(message: Message, state: FSMContext) -> None:
    if message.text == CREATE_CAMPAIGN_TEXT:
        await start_campaign_creation(message, state)
    elif message.text == LIST_CAMPAIGNS_TEXT:
        await list_campaigns(message, state)


async def start_campaign_creation(message: Message, state: FSMContext) -> None:
    user = await check_user(message)
    if not user:
        await message.answer(Messages.ERROR["user_not_found"])
        return

    async with get_session_with_advertiser(user.id) as (_, _, _, advertiser):
        if not advertiser:
            await message.answer(Messages.ERROR["not_registered"])
            return

        await state.set_state(CampaignCreationStates.entering_title)
        await message.answer(Messages.PROMPTS["enter_title"])


@router.message(CampaignCreationStates.entering_title)
async def process_campaign_title(message: Message, state: FSMContext) -> None:
    if not message.text or not message.text.strip():
        await message.answer(Messages.ERROR["campaign"]["invalid_title"])
        return

    await state.update_data(title=message.text.strip())
    await state.set_state(CampaignCreationStates.entering_text)
    await message.answer(Messages.PROMPTS["enter_text"])


@router.message(CampaignCreationStates.entering_text)
async def process_campaign_text(message: Message, state: FSMContext) -> None:
    if not message.text or not message.text.strip():
        await message.answer(Messages.ERROR["invalid_text"])
        return

    await state.update_data(text=message.text.strip())
    await state.set_state(CampaignCreationStates.entering_impressions_limit)
    await message.answer(Messages.PROMPTS["enter_impressions_limit"])


@router.message(CampaignCreationStates.entering_impressions_limit)
async def process_campaign_impressions_limit(
    message: Message, state: FSMContext
) -> None:
    try:
        limit = int(message.text.strip())
        if limit <= 0:
            raise ValueError("Лимит должен быть положительным")
        await state.update_data(impressions_limit=limit)
        await state.set_state(CampaignCreationStates.entering_clicks_limit)
        await message.answer(Messages.PROMPTS["enter_clicks_limit"])
    except ValueError:
        await message.answer(Messages.ERROR["invalid_limits"])


@router.message(CampaignCreationStates.entering_clicks_limit)
async def process_campaign_clicks_limit(message: Message, state: FSMContext) -> None:
    try:
        limit = int(message.text.strip())
        if limit <= 0:
            raise ValueError("Лимит должен быть положительным")
        await state.update_data(clicks_limit=limit)
        await state.set_state(CampaignCreationStates.entering_cost_per_impression)
        await message.answer(Messages.PROMPTS["enter_cost_per_impression"])
    except ValueError:
        await message.answer(Messages.ERROR["invalid_limits"])


@router.message(CampaignCreationStates.entering_cost_per_impression)
async def process_campaign_cost_per_impression(
    message: Message, state: FSMContext
) -> None:
    try:
        cost = float(message.text.strip())
        if cost <= 0:
            raise ValueError("Стоимость должна быть положительной")
        await state.update_data(cost_per_impression=cost)
        await state.set_state(CampaignCreationStates.entering_cost_per_click)
        await message.answer(Messages.PROMPTS["enter_cost_per_click"])
    except ValueError:
        await message.answer(Messages.ERROR["invalid_costs"])


@router.message(CampaignCreationStates.entering_cost_per_click)
async def process_campaign_cost_per_click(message: Message, state: FSMContext) -> None:
    try:
        cost = float(message.text.strip())
        if cost <= 0:
            raise ValueError("Стоимость должна быть положительной")
        await state.update_data(cost_per_click=cost)
        await state.set_state(CampaignCreationStates.entering_start_date)
        await message.answer(Messages.PROMPTS["enter_start_date"])
    except ValueError:
        await message.answer(Messages.ERROR["invalid_costs"])


@router.message(CampaignCreationStates.entering_start_date)
async def process_campaign_start_date(message: Message, state: FSMContext) -> None:
    try:
        date = int(message.text.strip())
        if date <= 0:
            raise ValueError("Дата должна быть положительной")
        await state.update_data(start_date=date)
        await state.set_state(CampaignCreationStates.entering_end_date)
        await message.answer(Messages.PROMPTS["enter_end_date"])
    except ValueError:
        await message.answer(Messages.ERROR["invalid_date"])


@router.message(CampaignCreationStates.entering_end_date)
async def process_campaign_end_date(message: Message, state: FSMContext) -> None:
    try:
        date = int(message.text.strip())
        if date <= 0:
            raise ValueError("Дата должна быть положительной")

        data = await state.get_data()
        start_date = data.get("start_date")
        if start_date and date <= start_date:
            await message.answer(Messages.ERROR["invalid_date"])
            return

        await state.update_data(end_date=date)
        await state.set_state(CampaignCreationStates.entering_gender)
        await message.answer(Messages.PROMPTS["enter_gender"])
    except ValueError:
        await message.answer(Messages.ERROR["invalid_date"])


@router.message(CampaignCreationStates.entering_gender)
async def process_campaign_gender(message: Message, state: FSMContext) -> None:
    gender = message.text.strip().upper()
    if gender not in ["MALE", "FEMALE", "ALL"]:
        await message.answer(Messages.ERROR["invalid_targeting"])
        return

    await state.update_data(gender=gender)
    await state.set_state(CampaignCreationStates.entering_age_from)
    await message.answer(
        Messages.PROMPTS["enter_age_from"],
        reply_markup=SKIP_KEYBOARD,
    )


@router.callback_query(
    CampaignCreationStates.entering_gender,
    F.data == CALLBACK_SKIP,
)
async def skip_gender(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(gender="ALL")
    await state.set_state(CampaignCreationStates.entering_age_from)
    await callback.message.edit_text(
        Messages.PROMPTS["enter_age_from"],
        reply_markup=SKIP_KEYBOARD,
    )
    await callback.answer()


@router.message(CampaignCreationStates.entering_age_from)
async def process_campaign_age_from(message: Message, state: FSMContext) -> None:
    try:
        age = int(message.text.strip())

        await state.update_data(age_from=age)
        await state.set_state(CampaignCreationStates.entering_age_to)
        await message.answer(
            Messages.PROMPTS["enter_age_to"],
            reply_markup=SKIP_KEYBOARD,
        )
    except ValueError:
        await message.answer(Messages.ERROR["invalid_targeting"])


@router.callback_query(
    CampaignCreationStates.entering_age_from,
    F.data == CALLBACK_SKIP,
)
async def skip_age_from(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(age_from=0)
    await state.set_state(CampaignCreationStates.entering_age_to)
    await callback.message.edit_text(
        Messages.PROMPTS["enter_age_to"],
        reply_markup=SKIP_KEYBOARD,
    )
    await callback.answer()


@router.message(CampaignCreationStates.entering_age_to)
async def process_campaign_age_to(message: Message, state: FSMContext) -> None:
    try:
        age = int(message.text.strip())

        data = await state.get_data()
        age_from = data.get("age_from")
        if age_from and age <= age_from:
            await message.answer(Messages.ERROR["invalid_targeting"])
            return

        await state.update_data(age_to=age)
        await state.set_state(CampaignCreationStates.entering_location)
        await message.answer(
            Messages.PROMPTS["enter_location"],
            reply_markup=SKIP_KEYBOARD,
        )
    except ValueError:
        await message.answer(Messages.ERROR["invalid_targeting"])


@router.callback_query(
    CampaignCreationStates.entering_age_to,
    F.data == CALLBACK_SKIP,
)
async def skip_age_to(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(age_to=100)
    await state.set_state(CampaignCreationStates.entering_location)
    await callback.message.edit_text(
        Messages.PROMPTS["enter_location"],
        reply_markup=SKIP_KEYBOARD,
    )
    await callback.answer()


@router.message(CampaignCreationStates.entering_location)
async def process_campaign_location(message: Message, state: FSMContext) -> None:
    location = message.text.strip()
    if not location:
        await message.answer(Messages.ERROR["invalid_targeting"])
        return

    await state.update_data(location=location)

    data = await state.get_data()
    await state.set_state(CampaignCreationStates.confirming_targeting)
    await message.answer(
        Messages.PROMPTS["confirm_targeting"].format(
            gender=data["gender"],
            age_from=data["age_from"],
            age_to=data["age_to"],
            location=location,
        ),
        reply_markup=CONFIRM_KEYBOARD,
    )


@router.callback_query(
    CampaignCreationStates.entering_location,
    F.data == CALLBACK_SKIP,
)
async def skip_location(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(location="ALL")

    data = await state.get_data()
    await state.set_state(CampaignCreationStates.confirming_targeting)
    await callback.message.edit_text(
        Messages.PROMPTS["confirm_targeting"].format(
            gender=data["gender"],
            age_from=data["age_from"],
            age_to=data["age_to"],
            location="ALL",
        ),
        reply_markup=CONFIRM_KEYBOARD,
    )
    await callback.answer()


async def list_campaigns(message: Message, state: FSMContext, page: int = 1) -> None:
    user = await check_user(message)
    if not user:
        await message.answer(Messages.ERROR["user_not_found"])
        return

    async with get_session_with_advertiser(user.id) as (session, _, _, advertiser):
        if not advertiser:
            await message.answer(Messages.ERROR["not_registered"])
            return

        mapper = CampaignsMapper()
        redis_client = await get_redis().__anext__()
        time_repository = TimeRepository(redis=redis_client)
        repository = CampaignsRepository(session, mapper, time_repository)
        uow = SQLAlchemyUow(session)

        async with uow:
            campaigns = await repository.get_all(
                advertiser_id=advertiser.id,
                size=10,
                page=page,
            )
            total_campaigns = len(campaigns)
            current_date = await time_repository.get_current_date()

            if not campaigns:
                await message.answer(Messages.INFO["no_campaigns"])
                return

            campaigns_text = "\n\n".join(
                Messages.INFO["campaign_list_item"].format(
                    id=campaign.id,
                    title=campaign.ad_title,
                    status="Активна"
                    if campaign.start_date <= current_date <= campaign.end_date
                    else "Неактивна",
                )
                for campaign in campaigns
            )

            total_pages = (total_campaigns + 9) // 10
            keyboard = get_campaigns_list_keyboard(
                current_page=page,
                total_pages=total_pages,
                has_prev=page > 1,
                has_next=page < total_pages,
            )

            await message.answer(
                Messages.INFO["campaign_list"].format(
                    total=total_campaigns,
                    page=page,
                    total_pages=total_pages,
                    campaigns=campaigns_text,
                ),
                reply_markup=keyboard,
            )


@router.callback_query(F.data.startswith("campaigns_page:"))
async def process_campaigns_page(callback: CallbackQuery, state: FSMContext) -> None:
    page = int(callback.data.split(":")[1])
    await list_campaigns(callback.message, state, page)
    await callback.answer()


@router.callback_query(F.data == CALLBACK_BACK_TO_MAIN)
async def process_back_to_main(callback: CallbackQuery, state: FSMContext) -> None:
    await cmd_campaigns(callback.message, state)
    await callback.answer()


@router.callback_query(F.data.startswith(CALLBACK_EDIT_CAMPAIGN))
async def process_edit_campaign(callback: CallbackQuery, state: FSMContext) -> None:
    campaign_id = callback.data.split(":")[1]
    keyboard = get_campaign_edit_keyboard(campaign_id)
    await callback.message.edit_text(
        Messages.PROMPTS["choose_edit_field"],
        reply_markup=keyboard,
    )
    await callback.answer()


@router.callback_query(F.data.startswith(CALLBACK_DELETE_CAMPAIGN))
async def process_delete_campaign(callback: CallbackQuery, state: FSMContext) -> None:
    campaign_id = callback.data.split(":")[1]
    await state.update_data(campaign_id=campaign_id)
    await state.set_state(CampaignManagementStates.confirming_delete)
    await callback.message.edit_text(
        Messages.PROMPTS["confirm_delete"],
        reply_markup=CONFIRM_KEYBOARD,
    )
    await callback.answer()


@router.callback_query(
    CampaignManagementStates.confirming_delete,
    F.data == CALLBACK_CONFIRM,
)
async def confirm_delete_campaign(callback: CallbackQuery, state: FSMContext) -> None:
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
        time_repository = get_time_repository()
        repository = CampaignsRepository(session, mapper, time_repository)
        uow = SQLAlchemyUow(session)

        try:
            async with uow:
                await repository.delete_campaign(
                    advertiser_id=advertiser.id,
                    campaign_id=campaign_id,
                )
                await uow.commit()
                await callback.message.edit_text(Messages.SUCCESS["campaign_deleted"])
        except Exception as e:
            await callback.message.edit_text(
                Messages.ERROR["db_error"]["campaign_delete"].format(error=str(e))
            )

    await state.clear()
    await callback.answer()


@router.callback_query(F.data == CALLBACK_BACK_TO_CAMPAIGNS)
async def process_back_to_campaigns(callback: CallbackQuery, state: FSMContext) -> None:
    await list_campaigns(callback.message, state)
    await callback.answer()


async def process_campaign_targeting_confirmation(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await callback.message.edit_text(
        Messages.PROMPTS["upload_image"],
        reply_markup=SKIP_KEYBOARD,
    )
    await state.set_state(CampaignCreationStates.uploading_image)


@router.callback_query(
    CampaignCreationStates.uploading_image,
    F.data == CALLBACK_SKIP,
)
async def skip_image_upload(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CampaignCreationStates.confirming_creation)
    data = await state.get_data()
    await callback.message.edit_text(
        Messages.PROMPTS["confirm_creation"]
        + "\n\n"
        + Messages.INFO["campaign_details"].format(
            id="Будет создан",
            title=data["title"],
            text=data["text"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            impressions_limit=data["impressions_limit"],
            clicks_limit=data["clicks_limit"],
            cost_per_impression=data["cost_per_impression"],
            cost_per_click=data["cost_per_click"],
            image_url="Не загружено",
            targeting_info=Messages.INFO["targeting_info"].format(
                gender=data["gender"],
                age_from=data["age_from"],
                age_to=data["age_to"],
                location=data["location"],
            ),
        ),
        reply_markup=CONFIRM_KEYBOARD,
    )
    await callback.answer()


@router.callback_query(
    CampaignCreationStates.confirming_creation,
    F.data == CALLBACK_CONFIRM,
)
async def confirm_campaign_creation(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    user = callback.from_user
    if not user:
        await callback.message.answer(Messages.ERROR["user_not_found"])
        return

    async with get_session_with_advertiser(user.id) as (session, _, _, advertiser):
        if not advertiser:
            await callback.message.answer(Messages.ERROR["not_registered"])
            return

        mapper = CampaignsMapper()
        time_repository = get_time_repository()
        repository = CampaignsRepository(session, mapper, time_repository)
        uow = SQLAlchemyUow(session)

        try:
            async with uow:
                campaign = await repository.create(
                    CampaignEntity(
                        id=uuid4(),
                        advertiser_id=advertiser.id,
                        ad_title=data["title"],
                        ad_text=data["text"],
                        impressions_limit=data["impressions_limit"],
                        clicks_limit=data["clicks_limit"],
                        cost_per_impression=data["cost_per_impression"],
                        cost_per_click=data["cost_per_click"],
                        start_date=data["start_date"],
                        end_date=data["end_date"],
                        gender=TargetingGender(data["gender"])
                        if data["gender"]
                        else None,
                        age_from=data["age_from"],
                        age_to=data["age_to"],
                        location=data["location"],
                    )
                )
                await uow.commit()

                await callback.message.edit_text(
                    Messages.SUCCESS["created"].format(
                        title=campaign.ad_title,
                        id=campaign.id,
                        start_date=campaign.start_date,
                        end_date=campaign.end_date,
                        impressions_limit=campaign.impressions_limit,
                        clicks_limit=campaign.clicks_limit,
                        cost_per_impression=campaign.cost_per_impression,
                        cost_per_click=campaign.cost_per_click,
                    )
                )
        except Exception as e:
            await callback.message.edit_text(
                Messages.ERROR["creation_failed"] + f"\nОшибка: {str(e)}"
            )

    await state.clear()
    await callback.answer()
