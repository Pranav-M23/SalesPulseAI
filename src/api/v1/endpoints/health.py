from fastapi import APIRouter
from src.config.settings import settings
import time

router = APIRouter()
_start_time = time.time()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": round(time.time() - _start_time, 2),
        "services": {
            "groq_ai": bool(settings.GROQ_API_KEY),
            "twilio": bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN),
            "sendgrid": bool(settings.SENDGRID_API_KEY),
        },
    }
