from pydantic import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "SalesPulse AI"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    # Database Configuration
    DATABASE_URL: str

    # Logging Configuration
    LOG_LEVEL: str = "INFO"

    # External Service Configuration
    OPENAI_API_KEY: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    SENDGRID_API_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()