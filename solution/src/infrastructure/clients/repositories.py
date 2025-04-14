from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.clients.entities import ClientEntity
from src.domain.clients.exceptions import ClientNotFoundException, ClientRepositoryError
from src.infrastructure.clients.mappers import ClientsMapper
from src.infrastructure.clients.orm import ClientModel


class ClientsRepository:
    def __init__(self, session: AsyncSession, mapper: ClientsMapper) -> None:
        self._session = session
        self._mapper = mapper

    async def get_by_id(self, id: UUID) -> ClientEntity:
        try:
            result = await self._session.execute(
                text("SELECT * FROM clients WHERE id = :id"), {"id": id}
            )
            model = result.mappings().first()
            if not model:
                raise ClientNotFoundException(f"Клиент с id {id} не найден")
            return self._mapper.from_model_to_entity(ClientModel(**model))
        except SQLAlchemyError as e:
            raise ClientRepositoryError(f"Db error: {str(e)}")

    async def bulk_upsert(self, entities: List[ClientEntity]) -> List[ClientEntity]:
        try:
            models: List[ClientModel] = []
            current_time = datetime.now()
            latest_entities = {entity.id: entity for entity in entities}

            for entity_id, entity in latest_entities.items():
                result = await self._session.execute(
                    text("SELECT * FROM clients WHERE id = :id"), {"id": entity_id}
                )
                existing = result.mappings().first()

                if existing:
                    await self._session.execute(
                        text("""
                            UPDATE clients 
                            SET login = :login, 
                                age = :age, 
                                location = :location, 
                                gender = :gender,
                                updated_at = :updated_at
                            WHERE id = :id
                        """),
                        {
                            "id": entity_id,
                            "login": entity.login,
                            "age": entity.age,
                            "location": entity.location,
                            "gender": entity.gender,
                            "updated_at": current_time,
                        },
                    )
                else:
                    await self._session.execute(
                        text("""
                            INSERT INTO clients (id, login, age, location, gender, created_at, updated_at)
                            VALUES (:id, :login, :age, :location, :gender, :created_at, :updated_at)
                        """),
                        {
                            "id": entity_id,
                            "login": entity.login,
                            "age": entity.age,
                            "location": entity.location,
                            "gender": entity.gender,
                            "created_at": current_time,
                            "updated_at": current_time,
                        },
                    )

                result = await self._session.execute(
                    text("SELECT * FROM clients WHERE id = :id"), {"id": entity_id}
                )
                model = result.mappings().one()
                count = sum(1 for e in entities if e.id == entity_id)
                models.extend([ClientModel(**model)] * count)

            await self._session.flush()
            return [self._mapper.from_model_to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise ClientRepositoryError(
                f"Db error during bulk upsert: {str(e)}"
            )
