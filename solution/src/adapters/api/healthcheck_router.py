from fastapi import APIRouter
from src.application.healthcheck.dtos import HealthcheckResponse

router = APIRouter()


@router.get("/healthcheck", tags=["Healthcheck"])
async def healthcheck() -> HealthcheckResponse:
    return HealthcheckResponse(status="ok")
