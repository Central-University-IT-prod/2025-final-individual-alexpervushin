from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from src.domain.advertisers.entities import AdvertiserEntity, MLScoreEntity
from src.infrastructure.advertisers.mappers import AdvertisersMapper, MLScoreMapper
from src.infrastructure.advertisers.orm import AdvertiserModel
from src.infrastructure.campaigns.orm import CampaignModel as CampaignModel
from src.infrastructure.clients.orm import ClientModel as ClientModel
from src.infrastructure.moderation.orm import ForbiddenWordsModel as ForbiddenWordsModel
from src.infrastructure.statistics.orm import UniqueEventModel as UniqueEventModel


@pytest.fixture
def advertiser_id() -> UUID:
    return UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def advertiser_name() -> str:
    return "Test Advertiser"


@pytest.fixture
def advertiser_entity(advertiser_id: UUID, advertiser_name: str) -> AdvertiserEntity:
    return AdvertiserEntity(
        id=advertiser_id,
        name=advertiser_name,
    )


@pytest.fixture
def advertiser_model(advertiser_id: UUID, advertiser_name: str) -> AdvertiserModel:
    return AdvertiserModel(
        id=advertiser_id,
        name=advertiser_name,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def advertisers_mapper() -> AdvertisersMapper:
    return AdvertisersMapper()


@pytest.fixture
def ml_score_mapper() -> MLScoreMapper:
    return MLScoreMapper()


@pytest.fixture
def ml_score_entity() -> MLScoreEntity:
    return MLScoreEntity(id=uuid4(), client_id=uuid4(), advertiser_id=uuid4(), score=85)
