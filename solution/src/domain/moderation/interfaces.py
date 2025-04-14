from typing import Dict, List, Optional, Protocol, Union

from src.application.moderation.dtos import ModerationResponse


class ModerationResult:
    def __init__(
        self,
        contains_forbidden_words: bool,
        source: str = "",
        details: Optional[Union[Dict[str, bool], ModerationResponse]] = None,
    ):
        self.contains_forbidden_words = contains_forbidden_words
        self.source = source
        self.details = details or {}


class ForbiddenWordsRepositoryProtocol(Protocol):
    async def get_all(self) -> List[str]: ...

    async def update(self, data: List[str]) -> None: ...


class GetForbiddenWordsUseCaseProtocol(Protocol):
    async def execute(self) -> List[str]: ...


class UpdateForbiddenWordsUseCaseProtocol(Protocol):
    async def execute(self, data: List[str]) -> None: ...


class CheckForbiddenWordsUseCaseProtocol(Protocol):
    async def execute(
        self,
        text: str,
        check_database: bool = True,
        check_ai: bool = True,
    ) -> ModerationResponse: ...


class ModerationServiceProtocol(Protocol):
    async def check_forbidden_words_db(self, text: str) -> ModerationResult: ...
    async def check_forbidden_words_ai(
        self,
        text: str,
        check_profanity: bool = False,
        check_offensive: bool = False,
        check_inappropriate: bool = False,
    ) -> ModerationResult: ...
    async def check_forbidden_words(
        self,
        text: str,
        check_database: bool = True,
        check_ai: bool = True,
    ) -> ModerationResult: ...


