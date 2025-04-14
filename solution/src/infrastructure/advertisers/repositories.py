from datetime import UTC, datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.advertisers.entities import AdvertiserEntity, MLScoreEntity
from src.domain.advertisers.exceptions import (
    AdvertiserNotFoundException,
    AdvertiserRepositoryError,
    MLScoreRepositoryError,
    TelegramLinkError,
)
from src.domain.advertisers.interfaces import AdvertisersRepositoryProtocol
from src.domain.clients.exceptions import ClientNotFoundException
from src.domain.clients.interfaces import ClientsRepositoryProtocol
from src.infrastructure.advertisers.mappers import AdvertisersMapper, MLScoreMapper
from src.infrastructure.advertisers.orm import AdvertiserModel


class AdvertisersRepository:
    def __init__(self, session: AsyncSession, mapper: AdvertisersMapper) -> None:
        self._session = session
        self._mapper = mapper

    async def get_by_id(self, id: UUID) -> AdvertiserEntity:
        try:
            result = await self._session.execute(
                text("SELECT * FROM advertisers WHERE id = :id"), {"id": id}
            )
            model = result.mappings().first()
            if not model:
                raise AdvertiserNotFoundException(f"Рекламодатель с id {id} не найден")
            return self._mapper.from_model_to_entity(AdvertiserModel(**model))
        except SQLAlchemyError as e:
            raise AdvertiserRepositoryError(f"Db error: {str(e)}")

    async def bulk_upsert(
        self, entities: List[AdvertiserEntity]
    ) -> List[AdvertiserEntity]:
        try:
            models: List[AdvertiserModel] = []
            current_time = datetime.now(UTC)
            latest_entities = {entity.id: entity for entity in entities}

            for entity_id, entity in latest_entities.items():
                result = await self._session.execute(
                    text("SELECT * FROM advertisers WHERE id = :id"), {"id": entity_id}
                )
                existing = result.mappings().first()

                if existing:
                    await self._session.execute(
                        text("""
                            UPDATE advertisers 
                            SET name = :name, 
                                updated_at = :updated_at
                            WHERE id = :id
                        """),
                        {
                            "id": entity_id,
                            "name": entity.name,
                            "updated_at": current_time,
                        },
                    )
                else:
                    await self._session.execute(
                        text("""
                            INSERT INTO advertisers (id, name, created_at, updated_at)
                            VALUES (:id, :name, :created_at, :updated_at)
                        """),
                        {
                            "id": entity_id,
                            "name": entity.name,
                            "created_at": current_time,
                            "updated_at": current_time,
                        },
                    )

                result = await self._session.execute(
                    text("SELECT * FROM advertisers WHERE id = :id"), {"id": entity_id}
                )
                model = result.mappings().one()
                count = sum(1 for e in entities if e.id == entity_id)
                models.extend([AdvertiserModel(**model)] * count)

            await self._session.flush()
            return [self._mapper.from_model_to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise AdvertiserRepositoryError(f"Db error during bulk upsert: {str(e)}")

    async def link_telegram_user(self, telegram_id: int, advertiser_id: UUID) -> None:
        try:
            current_time = datetime.now(UTC)
            result = await self._session.execute(
                text(
                    "SELECT * FROM telegram_advertisers WHERE telegram_id = :telegram_id"
                ),
                {"telegram_id": telegram_id},
            )
            existing = result.mappings().first()

            if existing:
                await self._session.execute(
                    text("""
                        UPDATE telegram_advertisers 
                        SET advertiser_id = :advertiser_id,
                            updated_at = :updated_at
                        WHERE telegram_id = :telegram_id
                    """),
                    {
                        "telegram_id": telegram_id,
                        "advertiser_id": advertiser_id,
                        "updated_at": current_time,
                    },
                )
            else:
                await self._session.execute(
                    text("""
                        INSERT INTO telegram_advertisers (
                            id, telegram_id, advertiser_id, created_at, updated_at
                        ) VALUES (
                            :id, :telegram_id, :advertiser_id, :created_at, :updated_at
                        )
                    """),
                    {
                        "id": uuid4(),
                        "telegram_id": telegram_id,
                        "advertiser_id": advertiser_id,
                        "created_at": current_time,
                        "updated_at": current_time,
                    },
                )
        except SQLAlchemyError as e:
            raise TelegramLinkError(f"Failed to link telegram user: {str(e)}")

    async def get_advertiser_by_telegram_id(
        self, telegram_id: int
    ) -> Optional[AdvertiserEntity]:
        try:
            result = await self._session.execute(
                text("""
                    SELECT a.* FROM advertisers a
                    JOIN telegram_advertisers ta ON ta.advertiser_id = a.id
                    WHERE ta.telegram_id = :telegram_id
                """),
                {"telegram_id": telegram_id},
            )
            model = result.mappings().first()
            if not model:
                return None
            return self._mapper.from_model_to_entity(AdvertiserModel(**model))
        except SQLAlchemyError as e:
            raise AdvertiserRepositoryError(
                f"Failed to get advertiser by telegram ID: {str(e)}"
            )


class MLScoreRepository:
    def __init__(
        self,
        session: AsyncSession,
        mapper: MLScoreMapper,
        clients_repository: ClientsRepositoryProtocol,
        advertisers_repository: AdvertisersRepositoryProtocol,
    ) -> None:
        self._session = session
        self._mapper = mapper
        self._clients_repository = clients_repository
        self._advertisers_repository = advertisers_repository

    async def upsert_ml_score(self, entity: MLScoreEntity) -> None:
        try:
            await self._clients_repository.get_by_id(entity.client_id)
            await self._advertisers_repository.get_by_id(entity.advertiser_id)

            current_time = datetime.now(UTC)
            result = await self._session.execute(
                text("""
                    SELECT * FROM ml_scores 
                    WHERE client_id = :client_id AND advertiser_id = :advertiser_id
                """),
                {"client_id": entity.client_id, "advertiser_id": entity.advertiser_id},
            )
            existing = result.mappings().first()

            if existing:
                await self._session.execute(
                    text("""
                        UPDATE ml_scores 
                        SET score = :score,
                            updated_at = :updated_at
                        WHERE client_id = :client_id 
                        AND advertiser_id = :advertiser_id
                    """),
                    {
                        "client_id": entity.client_id,
                        "advertiser_id": entity.advertiser_id,
                        "score": entity.score,
                        "updated_at": current_time,
                    },
                )
            else:
                await self._session.execute(
                    text("""
                        INSERT INTO ml_scores (
                            id, client_id, advertiser_id, score, created_at, updated_at
                        ) VALUES (
                            :id, :client_id, :advertiser_id, :score, :created_at, :updated_at
                        )
                    """),
                    {
                        "id": uuid4(),
                        "client_id": entity.client_id,
                        "advertiser_id": entity.advertiser_id,
                        "score": entity.score,
                        "created_at": current_time,
                        "updated_at": current_time,
                    },
                )
        except ClientNotFoundException as e:
            raise ClientNotFoundException(str(e))
        except AdvertiserNotFoundException as e:
            raise AdvertiserNotFoundException(str(e))
        except SQLAlchemyError as e:
            raise MLScoreRepositoryError(f"Failed to upsert ML score: {str(e)}")

    async def get_ml_score(self, client_id: UUID, advertiser_id: UUID) -> int | None:
        try:
            await self._clients_repository.get_by_id(client_id)
            await self._advertisers_repository.get_by_id(advertiser_id)

            result = await self._session.execute(
                text("""
                    SELECT score FROM ml_scores 
                    WHERE client_id = :client_id AND advertiser_id = :advertiser_id
                """),
                {"client_id": client_id, "advertiser_id": advertiser_id},
            )
            return result.scalar_one_or_none()
        except ClientNotFoundException as e:
            raise ClientNotFoundException(str(e))
        except AdvertiserNotFoundException as e:
            raise AdvertiserNotFoundException(str(e))
        except SQLAlchemyError as e:
            raise MLScoreRepositoryError(f"Failed to get ML score: {str(e)}")
