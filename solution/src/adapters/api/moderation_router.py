from typing import List

from fastapi import APIRouter, Depends
from src.application.moderation.dtos import ModerationResponse
from src.common.depends import get_uow
from src.core.uow import AbstractUow
from src.domain.moderation.interfaces import (
    CheckForbiddenWordsUseCaseProtocol,
    GetForbiddenWordsUseCaseProtocol,
    UpdateForbiddenWordsUseCaseProtocol,
)

from .dependencies import (
    get_check_forbidden_words_use_case,
    get_get_forbidden_words_use_case,
    get_update_forbidden_words_use_case,
)

router = APIRouter()


@router.get("/forbidden-words", tags=["Moderation"])
async def get_forbidden_words(
    uow: AbstractUow = Depends(get_uow),
    usecase: GetForbiddenWordsUseCaseProtocol = Depends(
        get_get_forbidden_words_use_case
    ),
) -> List[str]:
    async with uow:
        return await usecase.execute()


@router.put("/forbidden-words", tags=["Moderation"])
async def update_forbidden_words(
    data: List[str],
    uow: AbstractUow = Depends(get_uow),
    usecase: UpdateForbiddenWordsUseCaseProtocol = Depends(
        get_update_forbidden_words_use_case
    ),
) -> None:
    async with uow:
        await usecase.execute(data=data)


@router.post("/check-forbidden-words", tags=["Moderation"])
async def check_forbidden_words(
    text: str,
    check_database: bool = True,
    check_ai: bool = True,
    uow: AbstractUow = Depends(get_uow),
    usecase: CheckForbiddenWordsUseCaseProtocol = Depends(
        get_check_forbidden_words_use_case
    ),
) -> ModerationResponse:
    async with uow:
        return await usecase.execute(text, check_database, check_ai)
