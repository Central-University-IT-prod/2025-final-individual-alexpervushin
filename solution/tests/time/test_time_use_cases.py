from unittest.mock import AsyncMock

import pytest
import redis.asyncio as redis

from src.application.time.dtos import GetCurrentDateResponse, TimeAdvancePostResponse
from src.application.time.use_cases import GetCurrentDateUseCase, TimeUseCase
from src.domain.time.exceptions import TimeRepositoryError


@pytest.mark.asyncio
class TestTimeUseCase:
    async def test_execute_success(self):
        dummy_repo = AsyncMock()
        dummy_redis = AsyncMock(spec=redis.Redis)
        initial_date = 41
        advanced_date = 42
        dummy_repo.advance_day.return_value = advanced_date

        time_use_case = TimeUseCase(repository=dummy_repo, redis=dummy_redis)

        response = await time_use_case.execute(current_date=initial_date)

        assert isinstance(response, TimeAdvancePostResponse)
        assert response.current_date == advanced_date
        dummy_repo.advance_day.assert_awaited_once_with(current_date=initial_date)

    async def test_execute_time_repository_error(self):
        dummy_repo = AsyncMock()
        dummy_redis = AsyncMock(spec=redis.Redis)
        error_message = "Advance error"
        dummy_repo.advance_day.side_effect = TimeRepositoryError(error_message)

        time_use_case = TimeUseCase(repository=dummy_repo, redis=dummy_redis)

        with pytest.raises(TimeRepositoryError) as exc_info:
            await time_use_case.execute(current_date=10)

        assert error_message in str(exc_info.value)

    async def test_execute_generic_exception(self):
        dummy_repo = AsyncMock()
        dummy_redis = AsyncMock(spec=redis.Redis)
        generic_error_message = "Unexpected error occurred"
        dummy_repo.advance_day.side_effect = Exception(generic_error_message)

        time_use_case = TimeUseCase(repository=dummy_repo, redis=dummy_redis)

        with pytest.raises(TimeRepositoryError) as exc_info:
            await time_use_case.execute(current_date=10)

        error_text = str(exc_info.value)
        assert generic_error_message in error_text
        assert "Unexpected error while advancing day" in error_text


@pytest.mark.asyncio
class TestGetCurrentDateUseCase:
    async def test_execute_success(self):
        dummy_repo = AsyncMock()
        current_date = 100
        dummy_repo.get_current_date.return_value = current_date

        get_current_date_use_case = GetCurrentDateUseCase(repository=dummy_repo)

        response = await get_current_date_use_case.execute()

        assert isinstance(response, GetCurrentDateResponse)
        assert response.current_date == current_date
        dummy_repo.get_current_date.assert_awaited_once()

    async def test_execute_time_repository_error(self):
        dummy_repo = AsyncMock()
        error_message = "Get current date error"
        dummy_repo.get_current_date.side_effect = TimeRepositoryError(error_message)

        get_current_date_use_case = GetCurrentDateUseCase(repository=dummy_repo)

        with pytest.raises(TimeRepositoryError) as exc_info:
            await get_current_date_use_case.execute()
        assert error_message in str(exc_info.value)

    async def test_execute_generic_exception(self):
        dummy_repo = AsyncMock()
        generic_error_message = "Boom"
        dummy_repo.get_current_date.side_effect = Exception(generic_error_message)

        get_current_date_use_case = GetCurrentDateUseCase(repository=dummy_repo)

        with pytest.raises(TimeRepositoryError) as exc_info:
            await get_current_date_use_case.execute()

        error_text = str(exc_info.value)
        assert generic_error_message in error_text
        assert "Unexpected error while getting current date" in error_text
