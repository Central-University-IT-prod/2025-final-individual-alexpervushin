from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path
from src.application.clients.dtos import (
    ClientSchema,
    ClientUpsertSchema,
)
from src.common.types import ClientId
from src.core.uow import AbstractUow
from src.domain.clients.exceptions import ClientNotFoundException, ClientRepositoryError
from src.domain.clients.interfaces import (
    GetClientByIdUseCaseProtocol,
    UpsertClientUseCaseProtocol,
)

from .dependencies import (
    get_client_by_id_use_case,
    get_uow,
    get_upsert_client_use_case,
)

router = APIRouter()


@router.get("/clients/{clientId}", tags=["Clients"])
async def get_client_by_id(
    client_id: ClientId = Path(..., alias="clientId"),
    uow: AbstractUow = Depends(get_uow),
    usecase: GetClientByIdUseCaseProtocol = Depends(get_client_by_id_use_case),
) -> ClientSchema:
    """
    Получение клиента по ID
    """
    try:
        async with uow:
            return await usecase.execute(client_id=client_id)
    except ClientNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ClientRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/clients/bulk",
    tags=["Clients"],
    status_code=201,
)
async def upsert_clients(
    data: List[ClientUpsertSchema],
    uow: AbstractUow = Depends(get_uow),
    usecase: UpsertClientUseCaseProtocol = Depends(get_upsert_client_use_case),
) -> List[ClientSchema]:
    """
    Массовое создание/обновление клиентов
    """
    try:
        async with uow:
            return await usecase.execute(clients=data)
    except ClientRepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ClientNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
