from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "SalesPulse AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Groq (replaces OpenAI)
    GROQ_API_KEY: str = "default_groq_api_key"

    # Twilio
    TWILIO_ACCOUNT_SID: str = "default_twilio_account_sid"
    TWILIO_AUTH_TOKEN: str = "default_twilio_auth_token"
    TWILIO_WHATSAPP_NUMBER: str = "default_twilio_whatsapp_number"
    TWILIO_SMS_NUMBER: str = "default_twilio_sms_number"

    # SendGrid
    SENDGRID_API_KEY: str = "default_sendgrid_api_key"
    SENDGRID_FROM_EMAIL: str = "default_sendgrid_from_email"

    # WhatsApp provider: "twilio" or "meta" (meta = Whapi)
    WHATSAPP_PROVIDER: str = "twilio"

    # Meta / Whapi access token (only needed if WHATSAPP_PROVIDER=meta)
    META_WHATSAPP_ACCESS_TOKEN: str = ""

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./salespulse.db"

    # System Prompt
    SYSTEM_PROMPT: str = (
        "You are SalesPulse AI, an intelligent sales and booking assistant on WhatsApp. "
        "You help with sales follow-ups, booking confirmations, and order management. "
        "Keep responses short (2-3 sentences max), friendly, and professional. "
        "Never invent product features or prices. "
        "\n\n"
        "BOOKING/ORDER CAPABILITIES:\n"
        "- When a user wants to book, order, or schedule something, extract the details "
        "(what, when, time, amount) and present a summary for confirmation.\n"
        "- When presenting a booking summary, ALWAYS end with: "
        "'Reply CONFIRM to confirm or CANCEL to cancel.'\n"
        "- If the user confirms (says yes, confirm, ok, done, approved, accept), "
        "acknowledge the confirmation positively.\n"
        "- If the user cancels (says no, cancel, nevermind, decline), "
        "acknowledge the cancellation respectfully.\n"
        "- If the user asks about their bookings/orders, summarize them.\n"
        "- If the user provides a confirmation code, look up that specific booking.\n"
        "\n"
        "IMPORTANT: When you detect the user wants to CREATE a new booking, "
        "include the line [CREATE_BOOKING] in your response followed by details in this format:\n"
        "[TITLE: <title>]\n"
        "[TYPE: <booking/order/appointment/reservation>]\n"
        "[DATE: <date if mentioned>]\n"
        "[TIME: <time if mentioned>]\n"
        "[AMOUNT: <amount if mentioned>]\n"
        "These tags will be parsed by the system — the user won't see them.\n"
        "\n"
        "When the user says CONFIRM, include [ACTION: CONFIRM] in your response.\n"
        "When the user says CANCEL, include [ACTION: CANCEL] in your response.\n"
        "When the user asks for STATUS of their bookings, include [ACTION: STATUS] in your response.\n"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
