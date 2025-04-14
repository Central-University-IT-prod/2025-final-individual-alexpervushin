from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.domain.advertisers.entities import AdvertiserEntity, MLScoreEntity
from src.domain.advertisers.exceptions import (
    AdvertiserNotFoundException,
    AdvertiserRepositoryError,
    MLScoreRepositoryError,
)
from src.infrastructure.advertisers.orm import AdvertiserModel as AdvertiserModel
from src.infrastructure.advertisers.repositories import (
    AdvertisersRepository,
    MLScoreRepository,
)
from src.infrastructure.campaigns.orm import CampaignModel as CampaignModel
from src.infrastructure.clients.orm import ClientModel as ClientModel
from src.infrastructure.moderation.orm import ForbiddenWordsModel as ForbiddenWordsModel
from src.infrastructure.statistics.orm import UniqueEventModel as UniqueEventModel


class TestAdvertisersRepository:
    @pytest.mark.asyncio
    async def test_get_by_id_success(
        self,
        advertiser_id: UUID,
        advertiser_entity: AdvertiserEntity,
        advertiser_model: MagicMock,
        advertisers_mapper: MagicMock,
    ):
        session = AsyncMock()
        mappings = MagicMock()
        model_dict = {
            "id": advertiser_id,
            "name": "Test Advertiser",
            "created_at": "2025-02-21T19:18:00",
            "updated_at": "2025-02-21T19:18:00",
        }
        mappings.first.return_value = model_dict
        execute_result = MagicMock()
        execute_result.mappings.return_value = mappings
        session.execute = AsyncMock(return_value=execute_result)

        advertisers_mapper.from_model_to_entity = MagicMock(
            return_value=advertiser_entity
        )
        repository = AdvertisersRepository(session, advertisers_mapper)

        result = await repository.get_by_id(advertiser_id)

        assert result == advertiser_entity
        assert session.execute.called
        assert advertisers_mapper.from_model_to_entity.called

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(
        self,
        advertiser_id: UUID,
        advertisers_mapper: MagicMock,
    ):
        session = AsyncMock()
        mappings = MagicMock()
        mappings.first.return_value = None
        execute_result = MagicMock()
        execute_result.mappings.return_value = mappings
        session.execute = AsyncMock(return_value=execute_result)

        repository = AdvertisersRepository(session, advertisers_mapper)

        with pytest.raises(AdvertiserNotFoundException):
            await repository.get_by_id(advertiser_id)

    @pytest.mark.asyncio
    async def test_get_by_id_db_error(
        self,
        advertiser_id: UUID,
        advertisers_mapper: MagicMock,
    ):
        session = AsyncMock()
        session.execute = AsyncMock(side_effect=SQLAlchemyError("DB Error"))

        repository = AdvertisersRepository(session, advertisers_mapper)

        with pytest.raises(AdvertiserRepositoryError):
            await repository.get_by_id(advertiser_id)

    @pytest.mark.asyncio
    async def test_bulk_upsert_success(
        self,
        advertiser_entity: AdvertiserEntity,
        advertiser_model: MagicMock,
        advertisers_mapper: MagicMock,
    ):
        session = AsyncMock()
        mappings = MagicMock()
        model_dict = {
            "id": advertiser_entity.id,
            "name": advertiser_entity.name,
            "created_at": "2025-02-21T19:18:00",
            "updated_at": "2025-02-21T19:18:00",
        }
        mappings.first.return_value = model_dict
        mappings.one.return_value = model_dict
        execute_result = MagicMock()
        execute_result.mappings.return_value = mappings
        session.execute = AsyncMock(return_value=execute_result)
        session.flush = AsyncMock()

        advertisers_mapper.from_model_to_entity = MagicMock(
            return_value=advertiser_entity
        )
        repository = AdvertisersRepository(session, advertisers_mapper)

        result = await repository.bulk_upsert([advertiser_entity])

        assert result == [advertiser_entity]
        assert session.execute.call_count >= 2
        assert session.flush.called


class TestMLScoreRepository:
    @pytest.mark.asyncio
    async def test_upsert_ml_score_success(
        self,
        ml_score_entity: MLScoreEntity,
    ):
        session = AsyncMock()
        mapper = AsyncMock()
        clients_repository = AsyncMock()
        advertisers_repository = AsyncMock()

        mappings = MagicMock()
        mappings.first.return_value = None
        execute_result = MagicMock()
        execute_result.mappings.return_value = mappings
        session.execute = AsyncMock(return_value=execute_result)

        clients_repository.get_by_id = AsyncMock()
        advertisers_repository.get_by_id = AsyncMock()

        repository = MLScoreRepository(
            session, mapper, clients_repository, advertisers_repository
        )

        await repository.upsert_ml_score(ml_score_entity)

        assert clients_repository.get_by_id.called
        assert advertisers_repository.get_by_id.called
        assert session.execute.call_count >= 2

    @pytest.mark.asyncio
    async def test_get_ml_score_success(self):
        session = AsyncMock()
        mapper = AsyncMock()
        clients_repository = AsyncMock()
        advertisers_repository = AsyncMock()

        expected_score = 85
        execute_result = MagicMock()
        execute_result.scalar_one_or_none.return_value = expected_score
        session.execute = AsyncMock(return_value=execute_result)

        clients_repository.get_by_id = AsyncMock()
        advertisers_repository.get_by_id = AsyncMock()

        repository = MLScoreRepository(
            session, mapper, clients_repository, advertisers_repository
        )

        client_id = uuid4()
        advertiser_id = uuid4()

        score = await repository.get_ml_score(client_id, advertiser_id)

        assert score == expected_score
        assert clients_repository.get_by_id.called
        assert advertisers_repository.get_by_id.called
        assert session.execute.called

    @pytest.mark.asyncio
    async def test_get_ml_score_not_found(self):
        session = AsyncMock()
        mapper = AsyncMock()
        clients_repository = AsyncMock()
        advertisers_repository = AsyncMock()

        execute_result = MagicMock()
        execute_result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=execute_result)

        clients_repository.get_by_id = AsyncMock()
        advertisers_repository.get_by_id = AsyncMock()

        repository = MLScoreRepository(
            session, mapper, clients_repository, advertisers_repository
        )

        client_id = uuid4()
        advertiser_id = uuid4()

        score = await repository.get_ml_score(client_id, advertiser_id)

        assert score is None

    @pytest.mark.asyncio
    async def test_ml_score_db_error(self):
        session = AsyncMock()
        mapper = AsyncMock()
        clients_repository = AsyncMock()
        advertisers_repository = AsyncMock()

        session.execute = AsyncMock(side_effect=SQLAlchemyError("DB Error"))

        clients_repository.get_by_id = AsyncMock()
        advertisers_repository.get_by_id = AsyncMock()

        repository = MLScoreRepository(
            session, mapper, clients_repository, advertisers_repository
        )

        with pytest.raises(MLScoreRepositoryError):
            await repository.get_ml_score(uuid4(), uuid4())
