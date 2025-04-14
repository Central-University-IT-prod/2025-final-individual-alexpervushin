from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.clients.dtos import ClientUpsertSchema
from src.application.clients.use_cases import GetClientByIdUseCase, UpsertClientUseCase
from src.common.enums import TargetingGender
from src.common.types import ClientId
from src.domain.clients.exceptions import ClientNotFoundException, ClientRepositoryError


@pytest.fixture
def dummy_uow():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    return uow


@pytest.mark.asyncio
class TestGetClientByIdUseCase:
    async def test_execute_success(self, dummy_uow: AsyncMock):
        dummy_client_id = ClientId(uuid4())
        dummy_client_entity = MagicMock()
        repository = AsyncMock()
        repository.get_by_id.return_value = dummy_client_entity

        expected_schema = SimpleNamespace(
            client_id=dummy_client_id,
            login="test_login",
            age=30,
            location="TestLocation",
            gender="M",
        )
        mapper = MagicMock()
        mapper.from_entity_to_schema.return_value = expected_schema

        use_case = GetClientByIdUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )
        result = await use_case.execute(dummy_client_id)
        assert result == expected_schema
        repository.get_by_id.assert_called_once_with(dummy_client_id)
        mapper.from_entity_to_schema.assert_called_once_with(dummy_client_entity)

    async def test_execute_client_not_found(self, dummy_uow: AsyncMock):
        dummy_client_id = ClientId(uuid4())
        repository = AsyncMock()
        repository.get_by_id.side_effect = ClientNotFoundException("Client not found")
        mapper = MagicMock()

        use_case = GetClientByIdUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )
        with pytest.raises(ClientNotFoundException) as exc:
            await use_case.execute(dummy_client_id)
        assert "Client not found" in str(exc.value)

    async def test_execute_repository_error(self, dummy_uow: AsyncMock):
        dummy_client_id = ClientId(uuid4())
        error_message = "Repository error"
        repository = AsyncMock()
        repository.get_by_id.side_effect = ClientRepositoryError(error_message)
        mapper = MagicMock()

        use_case = GetClientByIdUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )
        with pytest.raises(ClientRepositoryError) as exc:
            await use_case.execute(dummy_client_id)
        assert error_message in str(exc.value)

    async def test_execute_generic_error(self, dummy_uow: AsyncMock):
        dummy_client_id = ClientId(uuid4())
        repository = AsyncMock()
        repository.get_by_id.side_effect = Exception("Unexpected failure")
        mapper = MagicMock()

        use_case = GetClientByIdUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )
        with pytest.raises(ClientRepositoryError) as exc:
            await use_case.execute(dummy_client_id)
        assert "Unexpected error:" in str(exc.value)


@pytest.mark.asyncio
class TestUpsertClientUseCase:
    async def test_execute_success(self, dummy_uow: AsyncMock):
        dummy_client_id = ClientId(uuid4())
        dummy_client_upsert = ClientUpsertSchema(
            client_id=dummy_client_id,
            login="test_login",
            age=30,
            location="TestLocation",
            gender=TargetingGender.MALE,
        )
        dummy_client_entity = MagicMock()
        expected_schema = SimpleNamespace(
            client_id=dummy_client_id,
            login="test_login",
            age=30,
            location="TestLocation",
            gender="M",
        )
        repository = AsyncMock()
        repository.bulk_upsert.return_value = [dummy_client_entity]
        mapper = MagicMock()
        mapper.from_schema_to_entity.return_value = dummy_client_entity
        mapper.from_entity_to_schema.return_value = expected_schema

        use_case = UpsertClientUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )
        result = await use_case.execute([dummy_client_upsert])
        assert result == [expected_schema]
        mapper.from_schema_to_entity.assert_called_once_with(dummy_client_upsert)
        repository.bulk_upsert.assert_called_once_with([dummy_client_entity])
        mapper.from_entity_to_schema.assert_called_once_with(dummy_client_entity)
        dummy_uow.commit.assert_called_once()

    async def test_execute_repository_error(self, dummy_uow: AsyncMock):
        dummy_client_upsert = ClientUpsertSchema(
            client_id=ClientId(uuid4()),
            login="test_login",
            age=30,
            location="TestLocation",
            gender=TargetingGender.MALE,
        )
        dummy_client_entity = MagicMock()
        error_message = "Bulk upsert error"
        repository = AsyncMock()
        repository.bulk_upsert.side_effect = ClientRepositoryError(error_message)
        mapper = MagicMock()
        mapper.from_schema_to_entity.return_value = dummy_client_entity

        use_case = UpsertClientUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )
        with pytest.raises(ClientRepositoryError) as exc:
            await use_case.execute([dummy_client_upsert])
        assert error_message in str(exc.value)

    async def test_execute_generic_error(self, dummy_uow: AsyncMock):
        dummy_client_upsert = ClientUpsertSchema(
            client_id=ClientId(uuid4()),
            login="test_login",
            age=30,
            location="TestLocation",
            gender=TargetingGender.MALE,
        )
        dummy_client_entity = MagicMock()
        repository = AsyncMock()
        repository.bulk_upsert.side_effect = Exception("Unexpected failure")
        mapper = MagicMock()
        mapper.from_schema_to_entity.return_value = dummy_client_entity

        use_case = UpsertClientUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )
        with pytest.raises(ClientRepositoryError) as exc:
            await use_case.execute([dummy_client_upsert])
        assert "Unexpected error during upsert:" in str(exc.value)
