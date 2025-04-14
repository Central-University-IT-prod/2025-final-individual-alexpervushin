from aiogram import Router

from .advertiser import router as advertiser_router
from .ml_score import router as ml_score_router

router = Router(name="advertisers")
router.include_router(advertiser_router)
router.include_router(ml_score_router)
