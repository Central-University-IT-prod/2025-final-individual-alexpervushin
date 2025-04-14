from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from src.adapters.telegram.common.constants import (
    ADVERTISERS_TEXT,
    CALLBACK_CONFIRM,
    CAMPAIGNS_TEXT,
    CREATE_ADVERTISER_TEXT,
    CREATE_CAMPAIGN_TEXT,
    GET_INFO_TEXT,
    JOIN_ADVERTISER_TEXT,
    LIST_CAMPAIGNS_TEXT,
    SET_ML_SCORE_TEXT,
)
from src.adapters.telegram.common.states import (
    CampaignCreationStates,
    RegistrationStates,
)
from src.adapters.telegram.handlers.advertisers.advertiser import (
    cmd_start as advertiser_start,
)
from src.adapters.telegram.handlers.advertisers.advertiser import (
    handle_any_command as advertiser_command,
)
from src.adapters.telegram.handlers.advertisers.advertiser import (
    process_advertiser_id,
    process_advertiser_name,
)
from src.adapters.telegram.handlers.campaigns.campaign import (
    cmd_campaigns,
    process_campaign_age_from,
    process_campaign_age_to,
    process_campaign_clicks_limit,
    process_campaign_cost_per_click,
    process_campaign_cost_per_impression,
    process_campaign_end_date,
    process_campaign_gender,
    process_campaign_impressions_limit,
    process_campaign_location,
    process_campaign_start_date,
    process_campaign_targeting_confirmation,
    process_campaign_text,
    process_campaign_title,
)
from src.adapters.telegram.handlers.campaigns.campaign import (
    handle_campaign_action as campaign_command,
)
from src.adapters.telegram.keyboards.main import MAIN_KEYBOARD
from src.adapters.telegram.messages.main import Messages

router = Router(name="main_handlers")


@router.message(lambda msg: msg.text == "/start")
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        Messages.PROMPTS["welcome"],
        reply_markup=MAIN_KEYBOARD,
    )


@router.message(F.text.in_([CAMPAIGNS_TEXT, ADVERTISERS_TEXT]))
async def handle_section_choice(message: Message, state: FSMContext) -> None:
    if message.text == CAMPAIGNS_TEXT:
        await cmd_campaigns(message, state)
    elif message.text == ADVERTISERS_TEXT:
        await advertiser_start(message, state)


@router.message(
    F.text.in_(
        [
            CREATE_CAMPAIGN_TEXT,
            LIST_CAMPAIGNS_TEXT,
        ]
    )
)
async def handle_campaign_commands(message: Message, state: FSMContext) -> None:
    await campaign_command(message, state)


@router.message(
    F.text.in_(
        [
            CREATE_ADVERTISER_TEXT,
            JOIN_ADVERTISER_TEXT,
            GET_INFO_TEXT,
            SET_ML_SCORE_TEXT,
        ]
    )
)
async def handle_advertiser_commands(message: Message, state: FSMContext) -> None:
    await advertiser_command(message, state)


@router.message(CampaignCreationStates.entering_title)
async def handle_campaign_title(message: Message, state: FSMContext) -> None:
    await process_campaign_title(message, state)


@router.message(CampaignCreationStates.entering_text)
async def handle_campaign_text(message: Message, state: FSMContext) -> None:
    await process_campaign_text(message, state)


@router.message(CampaignCreationStates.entering_impressions_limit)
async def handle_campaign_impressions_limit(
    message: Message, state: FSMContext
) -> None:
    await process_campaign_impressions_limit(message, state)


@router.message(CampaignCreationStates.entering_clicks_limit)
async def handle_campaign_clicks_limit(message: Message, state: FSMContext) -> None:
    await process_campaign_clicks_limit(message, state)


@router.message(CampaignCreationStates.entering_cost_per_impression)
async def handle_campaign_cost_per_impression(
    message: Message, state: FSMContext
) -> None:
    await process_campaign_cost_per_impression(message, state)


@router.message(CampaignCreationStates.entering_cost_per_click)
async def handle_campaign_cost_per_click(message: Message, state: FSMContext) -> None:
    await process_campaign_cost_per_click(message, state)


@router.message(CampaignCreationStates.entering_start_date)
async def handle_campaign_start_date(message: Message, state: FSMContext) -> None:
    await process_campaign_start_date(message, state)


@router.message(CampaignCreationStates.entering_end_date)
async def handle_campaign_end_date(message: Message, state: FSMContext) -> None:
    await process_campaign_end_date(message, state)


@router.message(CampaignCreationStates.entering_gender)
async def handle_campaign_gender(message: Message, state: FSMContext) -> None:
    await process_campaign_gender(message, state)


@router.message(CampaignCreationStates.entering_age_from)
async def handle_campaign_age_from(message: Message, state: FSMContext) -> None:
    await process_campaign_age_from(message, state)


@router.message(CampaignCreationStates.entering_age_to)
async def handle_campaign_age_to(message: Message, state: FSMContext) -> None:
    await process_campaign_age_to(message, state)


@router.message(CampaignCreationStates.entering_location)
async def handle_campaign_location(message: Message, state: FSMContext) -> None:
    await process_campaign_location(message, state)


@router.message(RegistrationStates.entering_advertiser_name)
async def handle_advertiser_creation(message: Message, state: FSMContext) -> None:
    await process_advertiser_name(message, state)


@router.message(RegistrationStates.entering_advertiser_id)
async def handle_advertiser_joining(message: Message, state: FSMContext) -> None:
    await process_advertiser_id(message, state)


@router.message()
async def handle_unknown(message: Message) -> None:
    await message.answer(
        Messages.ERROR["unknown_command"],
        reply_markup=MAIN_KEYBOARD,
    )


@router.callback_query(
    CampaignCreationStates.confirming_targeting,
    F.data == CALLBACK_CONFIRM,
)
async def confirm_campaign_targeting(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await process_campaign_targeting_confirmation(callback, state)
