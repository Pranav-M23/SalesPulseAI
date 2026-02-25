from src.config.settings import settings


async def verify_api_configured() -> bool:
    return bool(settings.OPENAI_API_KEY)
