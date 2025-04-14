from typing import Protocol
from uuid import UUID

from src.application.export.dtos import AdvertiserExportSchema


class ExportAdvertiserDataUseCaseProtocol(Protocol):
    async def execute(self, advertiser_id: UUID) -> bytes: ...


class ExportServiceProtocol(Protocol):
    def create_export_archive(self, data: AdvertiserExportSchema) -> bytes: ...
