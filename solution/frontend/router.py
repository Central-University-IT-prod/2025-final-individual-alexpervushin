from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

router = APIRouter()

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
router.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/campaign/{campaign_id}")
async def campaign(request: Request, campaign_id: str):
    return templates.TemplateResponse(
        "campaign.html", {"request": request, "campaign_id": campaign_id}
    )


@router.get("/create")
async def create(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})
