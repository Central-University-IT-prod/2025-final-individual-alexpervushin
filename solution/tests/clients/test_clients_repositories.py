from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.domain.clients.entities import ClientEntity
from src.domain.clients.exceptions import ClientNotFoundException, ClientRepositoryError
from src.infrastructure.clients.repositories import ClientsRepository


@pytest.mark.asyncio
class TestClientsRepository:
    async def test_get_by_id_success(self):
        client_id = uuid4()
        session = AsyncMock()
        client_data = {
            "id": client_id,
            "login": "test_user",
            "age": 25,
            "location": "Testville",
            "gender": "FEMALE",
        }
        mappings = MagicMock()
        mappings.first.return_value = client_data
        execute_result = MagicMock()
        execute_result.mappings.return_value = mappings
        session.execute = AsyncMock(return_value=execute_result)

        expected_client = ClientEntity(
            id=client_id,
            login="test_user",
            age=25,
            location="Testville",
            gender="FEMALE",
        )

        mapper = MagicMock()
        mapper.from_model_to_entity.return_value = expected_client

        repository = ClientsRepository(session, mapper)

        result = await repository.get_by_id(client_id)

        assert result == expected_client
        session.execute.assert_called_once()
        mapper.from_model_to_entity.assert_called_once()

    async def test_get_by_id_not_found(self):
        client_id = uuid4()
        session = AsyncMock()
        mappings = MagicMock()
        mappings.first.return_value = None
        execute_result = MagicMock()
        execute_result.mappings.return_value = mappings
        session.execute = AsyncMock(return_value=execute_result)

        mapper = MagicMock()

        repository = ClientsRepository(session, mapper)

        with pytest.raises(ClientNotFoundException):
            await repository.get_by_id(client_id)

    async def test_get_by_id_db_error(self):
        client_id = uuid4()
        session = AsyncMock()
        session.execute = AsyncMock(side_effect=SQLAlchemyError("DB error"))
        mapper = MagicMock()

        repository = ClientsRepository(session, mapper)

        with pytest.raises(ClientRepositoryError):
            await repository.get_by_id(client_id)

    async def test_bulk_upsert_success(self):
        client_id = uuid4()
        client_entity = ClientEntity(
            id=client_id,
            login="test_user",
            age=25,
            location="Testville",
            gender="FEMALE",
        )

        session = AsyncMock()
        mappings = MagicMock()
        model_dict = {
            "id": client_id,
            "login": "test_user",
            "age": 25,
            "location": "Testville",
            "gender": "FEMALE",
        }
        mappings.first.return_value = model_dict
        mappings.one.return_value = model_dict
        execute_result = MagicMock()
        execute_result.mappings.return_value = mappings
        session.execute = AsyncMock(return_value=execute_result)
        session.flush = AsyncMock()

        mapper = MagicMock()
        mapper.from_model_to_entity.return_value = client_entity

        repository = ClientsRepository(session, mapper)

        result = await repository.bulk_upsert([client_entity])

        assert result == [client_entity]
        assert session.execute.call_count >= 2
        session.flush.assert_called_once()
