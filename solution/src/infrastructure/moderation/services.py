from logging import getLogger

from src.core.settings import Settings
from src.core.uow import AbstractUow
from src.domain.ai.interfaces import AIServiceProtocol
from src.domain.moderation.interfaces import (
    ForbiddenWordsRepositoryProtocol,
    ModerationResult,
)

logger = getLogger(__name__)


class ModerationService:
    def __init__(
        self,
        uow: AbstractUow,
        repository: ForbiddenWordsRepositoryProtocol,
        ai_service: AIServiceProtocol,
        settings: Settings,
    ):
        self.uow = uow
        self.repository = repository
        self.ai_service = ai_service
        self.settings = settings

    async def check_forbidden_words_db(self, text: str) -> ModerationResult:
        try:
            async with self.uow:
                forbidden_words = await self.repository.get_all()
                text_lower = text.lower()
                contains_forbidden = any(
                    word.lower() in text_lower for word in forbidden_words
                )
                return ModerationResult(
                    contains_forbidden_words=contains_forbidden, source="database"
                )
        except Exception as e:
            logger.error(f"Error checking forbidden words in database: {str(e)}")
            return ModerationResult(
                contains_forbidden_words=False, source="database_error"
            )

    async def check_forbidden_words_ai(
        self,
        text: str,
        check_profanity: bool = False,
        check_offensive: bool = False,
        check_inappropriate: bool = False,
    ) -> ModerationResult:
        try:
            if not any([check_profanity, check_offensive, check_inappropriate]):
                return ModerationResult(
                    contains_forbidden_words=False, source="ai_skipped"
                )

            moderation_result = await self.ai_service.check_forbidden_words(text)

            contains_forbidden = any(
                [
                    check_profanity and moderation_result["profanity"],
                    check_offensive and moderation_result["offensive"],
                    check_inappropriate and moderation_result["inappropriate"],
                ]
            )

            return ModerationResult(
                contains_forbidden_words=contains_forbidden,
                source="ai",
                details=moderation_result,
            )
        except Exception as e:
            logger.error(f"Error checking forbidden words with AI: {str(e)}")
            return ModerationResult(contains_forbidden_words=False, source="ai_error")

    async def check_forbidden_words(
        self,
        text: str,
        check_database: bool = True,
        check_ai: bool = True,
    ) -> ModerationResult:
        if not text.strip():
            return ModerationResult(
                contains_forbidden_words=False, source="empty_input"
            )

        if check_database:
            db_result = await self.check_forbidden_words_db(text)
            if db_result.contains_forbidden_words:
                return db_result

        if check_ai and self.settings.ai_moderation_enabled:
            ai_result = await self.check_forbidden_words_ai(
                text,
                check_profanity=self.settings.ai_check_profanity,
                check_offensive=self.settings.ai_check_offensive,
                check_inappropriate=self.settings.ai_check_inappropriate,
            )
            return ai_result

        return ModerationResult(
            contains_forbidden_words=False, source="no_checks_enabled"
        )
