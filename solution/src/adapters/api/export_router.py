from uuid import UUID

from fastapi import APIRouter, Depends, Response
from src.domain.export.interfaces import ExportAdvertiserDataUseCaseProtocol

from .dependencies import (
    get_export_advertiser_data_use_case,
)

router = APIRouter()


@router.get("/{advertiser_id}/export", tags=["Export"])
async def export_advertiser_data(
    advertiser_id: UUID,
    usecase: ExportAdvertiserDataUseCaseProtocol = Depends(
        get_export_advertiser_data_use_case
    ),
) -> Response:
    archive = await usecase.execute(advertiser_id=advertiser_id)

    return Response(
        content=archive,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="export_{advertiser_id}.zip"'
        },
    )
