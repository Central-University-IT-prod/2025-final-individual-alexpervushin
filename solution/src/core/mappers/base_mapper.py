from typing import Generic, Protocol, TypeVar

from src.core.entities.base_entity import BaseEntity

EntityType = TypeVar("EntityType", bound=BaseEntity)
SchemaType = TypeVar("SchemaType")
ModelType = TypeVar("ModelType")


class BaseMapper(Protocol, Generic[EntityType, SchemaType, ModelType]):
    def from_schema_to_entity(self, schema: SchemaType) -> EntityType: ...

    def from_entity_to_schema(self, entity: EntityType) -> SchemaType: ...

    def from_entity_to_model(self, entity: EntityType) -> ModelType: ...

    def from_model_to_entity(self, model: ModelType) -> EntityType: ...
