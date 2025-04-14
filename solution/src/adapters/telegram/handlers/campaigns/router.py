from aiogram import Router

from .campaign import router as campaign_router
from .image import router as image_router
from .targeting import router as targeting_router

router = Router(name="campaigns")
router.include_router(campaign_router)
router.include_router(image_router)
router.include_router(targeting_router) 