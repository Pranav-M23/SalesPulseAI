from fastapi import APIRouter
from src.api.v1.endpoints import health, messages, channels, webhooks, triggers, bookings
from src.api.v1.endpoints import conversations, analytics

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(messages.router, tags=["Messages"])
api_router.include_router(channels.router, prefix="/send", tags=["Channels"])
api_router.include_router(webhooks.router, prefix="/webhook", tags=["Webhooks"])
api_router.include_router(triggers.router, tags=["Triggers"])
api_router.include_router(bookings.router, tags=["Bookings"])
api_router.include_router(conversations.router, tags=["Conversations"])
api_router.include_router(analytics.router, tags=["Analytics"])
