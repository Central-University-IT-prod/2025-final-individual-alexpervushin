from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.advertisers.dtos import GetAdvertiserByIdSchema, MLScoreSchema
from src.application.advertisers.use_cases import (
    GetAdvertiserByIdUseCase,
    UpsertAdvertisersUseCase,
    UpsertMLScoreUseCase,
)
from src.domain.advertisers.entities import AdvertiserEntity, MLScoreEntity
from src.domain.advertisers.exceptions import (
    AdvertiserNotFoundException,
    AdvertiserRepositoryError,
    MLScoreRepositoryError,
)
from src.domain.clients.exceptions import ClientNotFoundException


@pytest.fixture
def dummy_uow():
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    return uow


@pytest.mark.asyncio
class TestGetAdvertiserByIdUseCase:
    async def test_execute_success(self, dummy_uow: AsyncMock):
        dummy_id = uuid4()
        advertiser_entity = AdvertiserEntity(id=dummy_id, name="Test Advertiser")
        repository = AsyncMock()
        repository.get_by_id.return_value = advertiser_entity

        mapper = MagicMock()
        expected_schema = {"advertiser_id": dummy_id, "name": "Test Advertiser"}
        mapper.from_entity_to_schema.return_value = expected_schema

        use_case = GetAdvertiserByIdUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )

        result = await use_case.execute(dummy_id)

        assert result == expected_schema
        repository.get_by_id.assert_called_once_with(dummy_id)
        mapper.from_entity_to_schema.assert_called_once_with(advertiser_entity)

    async def test_execute_advertiser_not_found(self, dummy_uow: AsyncMock):
        dummy_id = uuid4()
        repository = AsyncMock()
        repository.get_by_id.side_effect = AdvertiserNotFoundException(
            "Advertiser not found"
        )

        mapper = MagicMock()
        use_case = GetAdvertiserByIdUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )

        with pytest.raises(AdvertiserNotFoundException) as exc:
            await use_case.execute(dummy_id)
        assert "Advertiser not found" in str(exc.value)

    async def test_execute_generic_error(self, dummy_uow: AsyncMock):
        dummy_id = uuid4()
        repository = AsyncMock()
        repository.get_by_id.side_effect = Exception("Unexpected failure")

        mapper = MagicMock()
        use_case = GetAdvertiserByIdUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )

        with pytest.raises(AdvertiserRepositoryError) as exc:
            await use_case.execute(dummy_id)
        assert "Unexpected error:" in str(exc.value)


@pytest.mark.asyncio
class TestUpsertAdvertisersUseCase:
    async def test_execute_success(self, dummy_uow: AsyncMock):
        input_schema = GetAdvertiserByIdSchema(
            advertiser_id=uuid4(), name="Upsert Advertiser"
        )
        advertiser_entity = AdvertiserEntity(
            id=input_schema.advertiser_id, name=input_schema.name
        )

        repository = AsyncMock()
        repository.bulk_upsert.return_value = [advertiser_entity]

        mapper = MagicMock()
        mapper.from_schema_to_entity.return_value = advertiser_entity
        mapper.from_entity_to_schema.return_value = input_schema

        use_case = UpsertAdvertisersUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )

        result = await use_case.execute([input_schema])

        assert result == [input_schema]
        mapper.from_schema_to_entity.assert_called_once_with(input_schema)
        repository.bulk_upsert.assert_called_once_with([advertiser_entity])
        mapper.from_entity_to_schema.assert_called_once_with(advertiser_entity)
        dummy_uow.commit.assert_called_once()

    async def test_execute_repository_error(self, dummy_uow: AsyncMock):
        input_schema = GetAdvertiserByIdSchema(
            advertiser_id=uuid4(), name="Upsert Advertiser"
        )
        advertiser_entity = AdvertiserEntity(
            id=input_schema.advertiser_id, name=input_schema.name
        )

        repository = AsyncMock()
        repository.bulk_upsert.side_effect = AdvertiserRepositoryError(
            "Bulk upsert error"
        )

        mapper = MagicMock()
        mapper.from_schema_to_entity.return_value = advertiser_entity

        use_case = UpsertAdvertisersUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )

        with pytest.raises(AdvertiserRepositoryError) as exc:
            await use_case.execute([input_schema])
        assert "Bulk upsert error" in str(exc.value)


@pytest.mark.asyncio
class TestUpsertMLScoreUseCase:
    async def test_execute_success(self, dummy_uow: AsyncMock):
        input_schema = MLScoreSchema(client_id=uuid4(), advertiser_id=uuid4(), score=85)
        mlscore_entity = MLScoreEntity(
            id=uuid4(),
            client_id=input_schema.client_id,
            advertiser_id=input_schema.advertiser_id,
            score=input_schema.score,
        )

        repository = AsyncMock()
        mapper = MagicMock()
        mapper.from_schema_to_entity.return_value = mlscore_entity

        use_case = UpsertMLScoreUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )

        result = await use_case.execute(input_schema)

        assert result is None
        mapper.from_schema_to_entity.assert_called_once_with(input_schema)
        repository.upsert_ml_score.assert_called_once_with(mlscore_entity)
        dummy_uow.commit.assert_called_once()

    async def test_execute_advertiser_not_found(self, dummy_uow: AsyncMock):
        input_schema = MLScoreSchema(client_id=uuid4(), advertiser_id=uuid4(), score=85)
        mlscore_entity = MLScoreEntity(
            id=uuid4(),
            client_id=input_schema.client_id,
            advertiser_id=input_schema.advertiser_id,
            score=input_schema.score,
        )

        repository = AsyncMock()
        mapper = MagicMock()
        mapper.from_schema_to_entity.return_value = mlscore_entity
        repository.upsert_ml_score.side_effect = AdvertiserNotFoundException(
            "Advertiser not found"
        )

        use_case = UpsertMLScoreUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )

        with pytest.raises(AdvertiserNotFoundException) as exc:
            await use_case.execute(input_schema)
        assert "Advertiser not found" in str(exc.value)

    async def test_execute_client_not_found(self, dummy_uow: AsyncMock):
        input_schema = MLScoreSchema(client_id=uuid4(), advertiser_id=uuid4(), score=85)
        mlscore_entity = MLScoreEntity(
            id=uuid4(),
            client_id=input_schema.client_id,
            advertiser_id=input_schema.advertiser_id,
            score=input_schema.score,
        )

        repository = AsyncMock()
        mapper = MagicMock()
        mapper.from_schema_to_entity.return_value = mlscore_entity
        repository.upsert_ml_score.side_effect = ClientNotFoundException(
            "Client not found"
        )

        use_case = UpsertMLScoreUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )

        with pytest.raises(ClientNotFoundException) as exc:
            await use_case.execute(input_schema)
        assert "Client not found" in str(exc.value)

    async def test_execute_repository_error(self, dummy_uow: AsyncMock):
        input_schema = MLScoreSchema(client_id=uuid4(), advertiser_id=uuid4(), score=85)
        mlscore_entity = MLScoreEntity(
            id=uuid4(),
            client_id=input_schema.client_id,
            advertiser_id=input_schema.advertiser_id,
            score=input_schema.score,
        )

        repository = AsyncMock()
        mapper = MagicMock()
        mapper.from_schema_to_entity.return_value = mlscore_entity
        repository.upsert_ml_score.side_effect = MLScoreRepositoryError(
            "ML score error"
        )

        use_case = UpsertMLScoreUseCase(
            uow=dummy_uow, repository=repository, mapper=mapper
        )

        with pytest.raises(MLScoreRepositoryError) as exc:
            await use_case.execute(input_schema)
        assert "ML score error" in str(exc.value)
