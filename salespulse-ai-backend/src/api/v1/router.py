from fastapi import APIRouter
from .endpoints import health, messages, channels, webhooks

router = APIRouter()

router.include_router(health.router, prefix="/health", tags=["Health"])
router.include_router(messages.router, prefix="/messages", tags=["Messages"])
router.include_router(channels.router, prefix="/channels", tags=["Channels"])
router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])