from fastapi import APIRouter, Depends, HTTPException
from src.application.time.dtos import (
    GetCurrentDateResponse,
    TimeAdvancePostRequest,
    TimeAdvancePostResponse,
)
from src.domain.time.exceptions import TimeRepositoryError
from src.domain.time.interfaces import (
    GetCurrentDateUseCaseProtocol,
    TimeUseCaseProtocol,
)

from .dependencies import (
    get_get_current_date_use_case,
    get_time_use_case,
)

router = APIRouter(prefix="/time", tags=["time"])


@router.post("/advance", response_model=TimeAdvancePostResponse)
async def advance_day(
    current_date: TimeAdvancePostRequest,
    use_case: TimeUseCaseProtocol = Depends(get_time_use_case),
) -> TimeAdvancePostResponse:
    try:
        return await use_case.execute(current_date=current_date.current_date)
    except TimeRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))


@router.get("/current_date")
async def get_current_date(
    use_case: GetCurrentDateUseCaseProtocol = Depends(get_get_current_date_use_case),
) -> GetCurrentDateResponse:
    try:
        return await use_case.execute()
    except TimeRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
