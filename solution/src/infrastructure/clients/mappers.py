from src.application.clients.dtos import (
    ClientSchema,
    ClientUpsertSchema,
)
from src.domain.clients.entities import ClientEntity
from src.infrastructure.clients.orm import ClientModel
from src.common.enums import Gender
from src.core.mappers.base_mapper import BaseMapper


class ClientsMapper(BaseMapper[ClientEntity, ClientSchema, ClientModel]):
    def from_schema_to_entity(
        self, schema: ClientSchema | ClientUpsertSchema
    ) -> ClientEntity:
        return ClientEntity(
            id=schema.client_id,
            login=schema.login,
            age=schema.age,
            location=schema.location,
            gender=schema.gender.value,
        )

    def from_entity_to_schema(self, entity: ClientEntity) -> ClientSchema:
        return ClientSchema(
            client_id=entity.id,
            login=entity.login,
            age=entity.age,
            location=entity.location,
            gender=Gender(entity.gender),
        )

    def from_entity_to_model(self, entity: ClientEntity) -> ClientModel:
        model = ClientModel()
        model.login = entity.login
        model.age = entity.age
        model.location = entity.location
        model.gender = entity.gender
        return model

    def from_model_to_entity(self, model: ClientModel) -> ClientEntity:
        return ClientEntity(
            id=model.id,
            login=model.login,
            age=model.age,
            location=model.location,
            gender=model.gender,
        )
