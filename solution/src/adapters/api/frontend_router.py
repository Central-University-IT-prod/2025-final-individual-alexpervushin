from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/web")

BASE_DIR = Path(__file__).parent.parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "frontend" / "static"
IMAGES_DIR = BASE_DIR / "frontend" / "images"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
router.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
router.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse("advertisers_index.html", {"request": request})


@router.get("/advertisers/index")
async def advertisers_index(request: Request):
    return templates.TemplateResponse("advertisers_index.html", {"request": request})


@router.get("/advertisers/login")
async def login(request: Request):
    return templates.TemplateResponse("advertisers_login.html", {"request": request})


@router.get("/advertisers/register")
async def register(request: Request):
    return templates.TemplateResponse("advertisers_register.html", {"request": request})


@router.get("/advertisers/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "advertisers_dashboard.html", {"request": request}
    )


@router.get("/advertisers/campaign/{campaign_id}")
async def campaign(request: Request, campaign_id: str):
    return templates.TemplateResponse(
        "advertisers_campaign.html", {"request": request, "campaign_id": campaign_id}
    )


@router.get("/advertisers/create")
async def create(request: Request):
    return templates.TemplateResponse("advertisers_create.html", {"request": request})


@router.get("/advertisers/moderation")
async def moderation(request: Request):
    return templates.TemplateResponse(
        "advertisers_moderation.html", {"request": request}
    )


@router.get("/advertisers/ml-score")
async def ml_score(request: Request):
    return templates.TemplateResponse("advertisers_ml_score.html", {"request": request})


@router.get("/clients/index")
async def clients_index(request: Request):
    return templates.TemplateResponse("clients_index.html", {"request": request})


@router.get("/clients/login")
async def clients_login(request: Request):
    return templates.TemplateResponse("clients_login.html", {"request": request})


@router.get("/clients/register")
async def clients_register(request: Request):
    return templates.TemplateResponse("clients_register.html", {"request": request})


@router.get("/clients/dashboard")
async def clients_dashboard(request: Request):
    return templates.TemplateResponse("clients_dashboard.html", {"request": request})


@router.get("/advertisers/profile")
async def advertisers_profile(request: Request):
    return templates.TemplateResponse("advertisers_profile.html", {"request": request})
