from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from src.adapters.api.ads_router import router as ads_router
from src.adapters.api.advertisers_router import router as advertisers_router
from src.adapters.api.ai_router import router as ai_router
from src.adapters.api.campaigns_router import router as campaigns_router
from src.adapters.api.clients_router import router as clients_router
from src.adapters.api.export_router import router as export_router
from src.adapters.api.frontend_router import router as frontend_router
from src.adapters.api.healthcheck_router import router as healthcheck_router
from src.adapters.api.moderation_router import router as moderation_router
from src.adapters.api.statistics_router import router as statistics_router
from src.adapters.api.time_router import router as time_router
from src.core.db import init_db
from src.infrastructure.advertisers.orm import AdvertiserModel as AdvertiserModel
from src.infrastructure.campaigns.orm import CampaignModel as CampaignModel
from src.infrastructure.clients.orm import ClientModel as ClientModel
from src.infrastructure.moderation.orm import ForbiddenWordsModel as ForbiddenWordsModel
from src.infrastructure.statistics.orm import UniqueEventModel as UniqueEventModel

BASE_DIR = Path(__file__).parent.parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "static"
IMAGES_DIR = BASE_DIR / "frontend" / "images"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="PROD",
    description="PROD! PROD! PROD!",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

app.include_router(frontend_router)

app.include_router(healthcheck_router)
app.include_router(clients_router)
app.include_router(advertisers_router)
app.include_router(campaigns_router)
app.include_router(time_router)
app.include_router(statistics_router)
app.include_router(ads_router)
app.include_router(ai_router)
app.include_router(moderation_router)
app.include_router(export_router)

Instrumentator().instrument(app).expose(app)
