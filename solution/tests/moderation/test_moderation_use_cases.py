from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.moderation.dtos import ModerationResponse
from src.application.moderation.use_cases import (
    CheckForbiddenWordsUseCase,
    GetForbiddenWordsUseCase,
    UpdateForbiddenWordsUseCase,
)


@pytest.fixture
def dummy_uow():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    return uow


@pytest.mark.asyncio
class TestGetForbiddenWordsUseCase:
    async def test_execute_success(self, dummy_uow: AsyncMock):
        expected_words = ["forbidden1", "forbidden2"]
        repository = AsyncMock()
        repository.get_all.return_value = expected_words

        use_case = GetForbiddenWordsUseCase(uow=dummy_uow, repository=repository)

        result = await use_case.execute()

        assert result == expected_words
        repository.get_all.assert_awaited_once()

    async def test_execute_error(self, dummy_uow: AsyncMock):
        repository = AsyncMock()
        repository.get_all.side_effect = Exception("Database Error")

        use_case = GetForbiddenWordsUseCase(uow=dummy_uow, repository=repository)

        with pytest.raises(Exception) as exc_info:
            await use_case.execute()
        assert "Database Error" in str(exc_info.value)


@pytest.mark.asyncio
class TestUpdateForbiddenWordsUseCase:
    async def test_execute_success(self, dummy_uow: AsyncMock):
        data = ["forbidden1", "forbidden2"]
        repository = AsyncMock()
        repository.update.return_value = None
        dummy_uow.commit = AsyncMock(return_value=None)

        use_case = UpdateForbiddenWordsUseCase(uow=dummy_uow, repository=repository)

        await use_case.execute(data)

        repository.update.assert_awaited_once_with(data)
        dummy_uow.commit.assert_awaited_once()

    async def test_execute_error(self, dummy_uow: AsyncMock):
        data = ["forbidden1", "forbidden2"]
        repository = AsyncMock()
        repository.update.side_effect = Exception("Update Error")
        dummy_uow.commit = AsyncMock(return_value=None)

        use_case = UpdateForbiddenWordsUseCase(uow=dummy_uow, repository=repository)

        with pytest.raises(Exception) as exc_info:
            await use_case.execute(data)
        assert "Update Error" in str(exc_info.value)
        repository.update.assert_awaited_once_with(data)
        dummy_uow.commit.assert_not_awaited()


@pytest.mark.asyncio
class TestCheckForbiddenWordsUseCase:
    async def test_execute_success(self, dummy_uow: AsyncMock):
        text = "Some input text"
        dummy_mod_result = MagicMock()
        dummy_mod_result.contains_forbidden_words = True
        dummy_mod_result.source = "test_service"
        dummy_mod_result.details = {"flag": True}

        repository = AsyncMock()
        moderation_service = AsyncMock()
        moderation_service.check_forbidden_words.return_value = dummy_mod_result
        mapper = MagicMock()
        dummy_mod_entity = MagicMock()
        mapper.from_moderation_result_to_entity.return_value = dummy_mod_entity
        expected_response = ModerationResponse(
            contains_forbidden_words=dummy_mod_result.contains_forbidden_words,
            source=dummy_mod_result.source,
            details=dummy_mod_result.details,
        )
        mapper.from_entity_to_response.return_value = expected_response

        use_case = CheckForbiddenWordsUseCase(
            uow=dummy_uow,
            repository=repository,
            moderation_service=moderation_service,
            mapper=mapper,
        )

        result = await use_case.execute(text, check_database=True, check_ai=True)

        assert result == expected_response
        moderation_service.check_forbidden_words.assert_awaited_once_with(
            text, check_database=True, check_ai=True
        )
        mapper.from_moderation_result_to_entity.assert_called_once_with(
            dummy_mod_result
        )
        mapper.from_entity_to_response.assert_called_once_with(dummy_mod_entity)

    async def test_execute_with_flags(self, dummy_uow: AsyncMock):
        text = "Another text input"
        dummy_mod_result = MagicMock()
        dummy_mod_result.contains_forbidden_words = False
        dummy_mod_result.source = "service"
        dummy_mod_result.details = {}

        repository = AsyncMock()
        moderation_service = AsyncMock()
        moderation_service.check_forbidden_words.return_value = dummy_mod_result
        mapper = MagicMock()
        dummy_mod_entity = MagicMock()
        mapper.from_moderation_result_to_entity.return_value = dummy_mod_entity
        expected_response = ModerationResponse(
            contains_forbidden_words=False, source="service", details={}
        )
        mapper.from_entity_to_response.return_value = expected_response

        use_case = CheckForbiddenWordsUseCase(
            uow=dummy_uow,
            repository=repository,
            moderation_service=moderation_service,
            mapper=mapper,
        )

        result = await use_case.execute(text, check_database=False, check_ai=False)

        assert result == expected_response
        moderation_service.check_forbidden_words.assert_awaited_once_with(
            text, check_database=False, check_ai=False
        )
        mapper.from_moderation_result_to_entity.assert_called_once_with(
            dummy_mod_result
        )
        mapper.from_entity_to_response.assert_called_once_with(dummy_mod_entity)

    async def test_execute_error(self, dummy_uow: AsyncMock):
        text = "Error text"
        repository = AsyncMock()
        moderation_service = AsyncMock()
        moderation_service.check_forbidden_words.side_effect = Exception(
            "Moderation error"
        )
        mapper = MagicMock()

        use_case = CheckForbiddenWordsUseCase(
            uow=dummy_uow,
            repository=repository,
            moderation_service=moderation_service,
            mapper=mapper,
        )

        with pytest.raises(Exception) as exc_info:
            await use_case.execute(text)
        assert "Moderation error" in str(exc_info.value)
        moderation_service.check_forbidden_words.assert_awaited_once_with(
            text, check_database=True, check_ai=True
        )
