import uuid

from src.application.advertisers.dtos import (
    GetAdvertiserByIdSchema,
    MLScoreSchema,
)
from src.core.mappers.base_mapper import BaseMapper
from src.domain.advertisers.entities import AdvertiserEntity, MLScoreEntity
from src.infrastructure.advertisers.orm import AdvertiserModel, MLScoreModel


class AdvertisersMapper(
    BaseMapper[AdvertiserEntity, GetAdvertiserByIdSchema, AdvertiserModel]
):
    def from_schema_to_entity(
        self, schema: GetAdvertiserByIdSchema
    ) -> AdvertiserEntity:
        return AdvertiserEntity(
            id=schema.advertiser_id,
            name=schema.name,
        )

    def from_entity_to_schema(
        self, entity: AdvertiserEntity
    ) -> GetAdvertiserByIdSchema:
        return GetAdvertiserByIdSchema(
            advertiser_id=entity.id,
            name=entity.name,
        )

    def from_entity_to_model(self, entity: AdvertiserEntity) -> AdvertiserModel:
        model = AdvertiserModel()
        model.id = entity.id
        model.name = entity.name
        return model

    def from_model_to_entity(self, model: AdvertiserModel) -> AdvertiserEntity:
        return AdvertiserEntity(
            id=model.id,
            name=model.name,
        )


class MLScoreMapper(BaseMapper[MLScoreEntity, MLScoreSchema, MLScoreModel]):
    def from_schema_to_entity(self, schema: MLScoreSchema) -> MLScoreEntity:
        return MLScoreEntity(
            id=uuid.uuid4(),
            client_id=schema.client_id,
            advertiser_id=schema.advertiser_id,
            score=schema.score,
        )

    def from_entity_to_schema(self, entity: MLScoreEntity) -> MLScoreSchema:
        return MLScoreSchema(
            client_id=entity.client_id,
            advertiser_id=entity.advertiser_id,
            score=entity.score,
        )

    def from_entity_to_model(self, entity: MLScoreEntity) -> MLScoreModel:
        model = MLScoreModel()
        model.client_id = entity.client_id
        model.advertiser_id = entity.advertiser_id
        model.score = entity.score
        return model

    def from_model_to_entity(self, model: MLScoreModel) -> MLScoreEntity:
        return MLScoreEntity(
            id=model.id,
            client_id=model.client_id,
            advertiser_id=model.advertiser_id,
            score=model.score,
        )
