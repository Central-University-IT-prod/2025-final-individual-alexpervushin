import uuid

from src.application.moderation.dtos import (
    ForbiddenWord,
    ModerationResponse,
)
from src.domain.moderation.entities import (
    ForbiddenWordsEntity,
    ModerationResultEntity,
)
from src.domain.moderation.interfaces import ModerationResult
from src.infrastructure.moderation.orm import ForbiddenWordsModel


class ModerationMapper:
    def from_entity_to_schema(self, entity: ForbiddenWordsModel) -> ForbiddenWord:
        return ForbiddenWord(word=entity.word)

    def from_entity_to_model(self, entity: ForbiddenWordsEntity) -> ForbiddenWordsModel:
        return ForbiddenWordsModel(id=entity.id, word=entity.word)

    def from_schema_to_entity(self, schema: ForbiddenWord) -> ForbiddenWordsEntity:
        return ForbiddenWordsEntity(id=uuid.uuid4(), word=schema.word)

    def from_moderation_result_to_entity(
        self, result: ModerationResult
    ) -> ModerationResultEntity:
        return ModerationResultEntity(
            id=uuid.uuid4(),
            contains_forbidden_words=result.contains_forbidden_words,
            source=result.source,
            details=result.details,
        )

    def from_entity_to_response(
        self, entity: ModerationResultEntity
    ) -> ModerationResponse:
        return ModerationResponse(
            contains_forbidden_words=entity.contains_forbidden_words,
            source=entity.source,
            details=entity.details,
        )
