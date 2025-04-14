import uuid

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from src.adapters.telegram.common.constants import BACK_TEXT
from src.adapters.telegram.common.states import RegistrationStates
from src.adapters.telegram.common.utils import (
    check_user,
    get_session_with_advertiser,
    text_equals,
)
from src.adapters.telegram.keyboards.advertisers import BACK_KEYBOARD, MAIN_KEYBOARD
from src.adapters.telegram.messages.advertisers import Messages
from src.application.advertisers.dtos import MLScoreSchema
from src.application.advertisers.use_cases import UpsertMLScoreUseCase
from src.core.db import async_session_maker
from src.core.uow import SQLAlchemyUow
from src.infrastructure.advertisers.mappers import MLScoreMapper
from src.infrastructure.advertisers.repositories import MLScoreRepository

router = Router(name="ml_score_handlers")


async def start_ml_score(message: Message, state: FSMContext) -> None:
    user = await check_user(message)
    if not user:
        await message.answer(Messages.ERROR["user_not_found"])
        return

    async with get_session_with_advertiser(user.id) as (_, _, _, advertiser):
        if not advertiser:
            await message.answer(
                Messages.ERROR["not_registered"], reply_markup=MAIN_KEYBOARD
            )
            await state.clear()
            return

        await state.clear()
        await state.update_data(advertiser_id=advertiser.id)
        await state.set_state(RegistrationStates.entering_client_id)
        await message.answer(
            Messages.PROMPTS["enter_client_id"],
            reply_markup=BACK_KEYBOARD,
        )


@router.message(RegistrationStates.entering_client_id, text_equals(BACK_TEXT))
@router.message(RegistrationStates.entering_ml_score, text_equals(BACK_TEXT))
async def handle_back(message: Message, state: FSMContext) -> None:
    await state.clear()
    await start_ml_score(message, state)


@router.message(RegistrationStates.entering_client_id)
async def process_client_id(message: Message, state: FSMContext) -> None:
    if message.text == BACK_TEXT:
        await start_ml_score(message, state)
        return

    if not message.text:
        await message.answer(Messages.ERROR["invalid_uuid"])
        return

    try:
        client_id = uuid.UUID(message.text.strip())
        await state.update_data(client_id=client_id)
        await state.set_state(RegistrationStates.entering_ml_score)
        await message.answer(
            Messages.PROMPTS["enter_ml_score"],
            reply_markup=BACK_KEYBOARD,
        )
    except ValueError:
        await message.answer(
            f"{Messages.ERROR['invalid_uuid']}\n{Messages.PROMPTS['uuid_format']}"
        )


@router.message(RegistrationStates.entering_ml_score)
async def process_ml_score(message: Message, state: FSMContext) -> None:
    if message.text == BACK_TEXT:
        await state.set_state(RegistrationStates.entering_client_id)
        await message.answer(
            Messages.PROMPTS["enter_client_id"],
            reply_markup=BACK_KEYBOARD,
        )
        return

    if not message.text:
        await message.answer(
            Messages.ERROR["ml_score"]["empty_score"],
            reply_markup=MAIN_KEYBOARD,
        )
        await state.clear()
        await state.set_state(RegistrationStates.choosing_action)
        return

    try:
        score = int(message.text.strip())
        state_data = await state.get_data()

        ml_score_data = MLScoreSchema(
            client_id=state_data["client_id"],
            advertiser_id=state_data["advertiser_id"],
            score=score,
        )

        try:
            async with async_session_maker() as session:
                ml_mapper = MLScoreMapper()
                ml_repository = MLScoreRepository(session, ml_mapper)
                uow = SQLAlchemyUow(session)
                usecase = UpsertMLScoreUseCase(uow, ml_repository, ml_mapper)

                async with uow:
                    await usecase.execute(data=ml_score_data)
                    await message.answer(
                        Messages.SUCCESS["ml_score_updated"].format(
                            client_id=ml_score_data.client_id,
                            score=ml_score_data.score,
                        ),
                        reply_markup=MAIN_KEYBOARD,
                    )
        except Exception as e:
            await message.answer(
                f"{Messages.ERROR['ml_score']['update_failed']}: {str(e)}",
                reply_markup=MAIN_KEYBOARD,
            )
    except ValueError:
        await message.answer(
            Messages.ERROR["ml_score"]["invalid_format"],
            reply_markup=MAIN_KEYBOARD,
        )
        await state.clear()
        await state.set_state(RegistrationStates.choosing_action)
        return

    await state.clear()
    await state.set_state(RegistrationStates.choosing_action)
