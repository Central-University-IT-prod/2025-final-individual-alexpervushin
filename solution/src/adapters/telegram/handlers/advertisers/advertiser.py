import uuid

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from src.adapters.telegram.common.constants import (
    BACK_TEXT,
    CREATE_ADVERTISER_TEXT,
    GET_INFO_TEXT,
    JOIN_ADVERTISER_TEXT,
    SET_ML_SCORE_TEXT,
)
from src.adapters.telegram.common.states import RegistrationStates
from src.adapters.telegram.common.utils import (
    check_user,
    get_session_with_advertiser,
    text_equals,
)
from src.adapters.telegram.handlers.advertisers.ml_score import start_ml_score
from src.adapters.telegram.keyboards.advertisers import MAIN_KEYBOARD
from src.adapters.telegram.messages.advertisers import Messages
from src.application.advertisers.dtos import GetAdvertiserByIdSchema
from src.application.advertisers.use_cases import (
    GetAdvertiserByIdUseCase,
    UpsertAdvertisersUseCase,
)
from src.core.db import async_session_maker
from src.core.uow import SQLAlchemyUow
from src.infrastructure.advertisers.mappers import AdvertisersMapper
from src.infrastructure.advertisers.repositories import AdvertisersRepository

router = Router(name="advertiser_handlers")


@router.message(lambda msg: msg.text in ["/start", BACK_TEXT])
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(RegistrationStates.choosing_action)
    await message.answer(Messages.PROMPTS["welcome"], reply_markup=MAIN_KEYBOARD)


@router.message(
    lambda msg: msg.text
    in [
        CREATE_ADVERTISER_TEXT,
        JOIN_ADVERTISER_TEXT,
        GET_INFO_TEXT,
        SET_ML_SCORE_TEXT,
    ]
)
async def handle_any_command(message: Message, state: FSMContext) -> None:
    await state.clear()

    if message.text == CREATE_ADVERTISER_TEXT:
        await create_advertiser(message, state)
    elif message.text == JOIN_ADVERTISER_TEXT:
        await join_advertiser(message, state)
    elif message.text == GET_INFO_TEXT:
        await get_advertiser_info(message)
    elif message.text == SET_ML_SCORE_TEXT:
        await handle_ml_score(message, state)


@router.message(RegistrationStates.entering_advertiser_name, text_equals(BACK_TEXT))
@router.message(RegistrationStates.entering_advertiser_id, text_equals(BACK_TEXT))
async def handle_back_to_start(message: Message, state: FSMContext) -> None:
    await cmd_start(message, state)


@router.message(RegistrationStates.entering_advertiser_name)
async def process_advertiser_name(message: Message, state: FSMContext) -> None:
    if not message.text or not message.text.strip():
        await message.answer(Messages.ERROR["empty_advertiser_name"])
        return

    user = await check_user(message)
    if not user:
        await message.answer(Messages.ERROR["user_not_found"])
        return

    advertiser_id = uuid.uuid4()
    advertiser_data = [
        GetAdvertiserByIdSchema(
            advertiser_id=advertiser_id,
            name=message.text.strip(),
        )
    ]

    try:
        async with async_session_maker() as session:
            mapper = AdvertisersMapper()
            repository = AdvertisersRepository(session, mapper)
            uow = SQLAlchemyUow(session)
            usecase = UpsertAdvertisersUseCase(uow, repository, mapper)

            async with uow:
                result = await usecase.execute(data=advertiser_data)
                if result and result[0]:
                    registered = result[0]
                    await repository.link_telegram_user(
                        telegram_id=user.id,
                        advertiser_id=advertiser_id,
                    )
                    await uow.commit()
                    await message.answer(
                        Messages.SUCCESS["advertiser_created"].format(
                            name=registered.name,
                            id=registered.advertiser_id,
                        ),
                        reply_markup=MAIN_KEYBOARD,
                    )
                else:
                    await message.answer(
                        Messages.ERROR["advertiser_creation_failed"],
                        reply_markup=MAIN_KEYBOARD,
                    )
    except Exception as e:
        await message.answer(
            f"{Messages.ERROR['db_error']['advertiser_creation']}: {str(e)}",
            reply_markup=MAIN_KEYBOARD,
        )
    await state.clear()
    await state.set_state(RegistrationStates.choosing_action)


@router.message(RegistrationStates.entering_advertiser_id)
async def process_advertiser_id(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer(
            Messages.ERROR["invalid_uuid"],
            reply_markup=MAIN_KEYBOARD,
        )
        await state.clear()
        await state.set_state(RegistrationStates.choosing_action)
        return

    user = await check_user(message)
    if not user:
        await message.answer(Messages.ERROR["user_not_found"])
        return

    try:
        advertiser_id = uuid.UUID(message.text.strip())
    except ValueError:
        await message.answer(
            f"{Messages.ERROR['invalid_uuid']}\n{Messages.PROMPTS['uuid_format']}",
            reply_markup=MAIN_KEYBOARD,
        )
        await state.clear()
        await state.set_state(RegistrationStates.choosing_action)
        return

    try:
        async with async_session_maker() as session:
            mapper = AdvertisersMapper()
            repository = AdvertisersRepository(session, mapper)
            uow = SQLAlchemyUow(session)
            usecase = GetAdvertiserByIdUseCase(uow, repository, mapper)

            async with uow:
                advertiser = await usecase.execute(advertiser_id=advertiser_id)
                if advertiser:
                    await repository.link_telegram_user(
                        telegram_id=user.id,
                        advertiser_id=advertiser_id,
                    )
                    await uow.commit()
                    await message.answer(
                        Messages.SUCCESS["advertiser_joined"].format(
                            name=advertiser.name,
                            id=advertiser.advertiser_id,
                        ),
                        reply_markup=MAIN_KEYBOARD,
                    )
                else:
                    await message.answer(
                        Messages.ERROR["advertiser_not_found"],
                        reply_markup=MAIN_KEYBOARD,
                    )
    except Exception as e:
        await message.answer(
            f"{Messages.ERROR['db_error']['advertiser_join']}: {str(e)}",
            reply_markup=MAIN_KEYBOARD,
        )
    await state.clear()
    await state.set_state(RegistrationStates.choosing_action)


@router.message(RegistrationStates.choosing_action, text_equals(GET_INFO_TEXT))
async def get_advertiser_info(message: Message) -> None:
    user = await check_user(message)
    if not user:
        await message.answer(Messages.ERROR["user_not_found"])
        return

    async with get_session_with_advertiser(user.id) as (_, _, _, advertiser):
        if advertiser:
            response = Messages.INFO["advertiser_info"].format(
                id=advertiser.id,
                name=advertiser.name,
            )
        else:
            response = Messages.ERROR["not_registered"]
        await message.answer(response, reply_markup=MAIN_KEYBOARD)


@router.message(RegistrationStates.choosing_action, text_equals(SET_ML_SCORE_TEXT))
async def handle_ml_score(message: Message, state: FSMContext) -> None:
    await start_ml_score(message, state)


@router.message(RegistrationStates.choosing_action)
async def process_unknown_action(message: Message) -> None:
    await message.answer(
        Messages.PROMPTS["use_buttons"],
        reply_markup=MAIN_KEYBOARD,
    )


async def create_advertiser(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationStates.entering_advertiser_name)
    await message.answer(
        Messages.PROMPTS["enter_advertiser_name"],
        reply_markup=MAIN_KEYBOARD,
    )


async def join_advertiser(message: Message, state: FSMContext) -> None:
    await state.set_state(RegistrationStates.entering_advertiser_id)
    await message.answer(
        Messages.PROMPTS["enter_advertiser_id"],
        reply_markup=MAIN_KEYBOARD,
    )
