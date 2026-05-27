import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Auth
    SECRET_KEY: str         = os.getenv("SECRET_KEY", "changeme")
    ALGORITHM: str          = "HS256"
    TOKEN_EXPIRY_HOURS: int = int(os.getenv("TOKEN_EXPIRY_HOURS", "24"))

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str   = os.getenv("OPENAI_MODEL", "gpt-4o")

    # Email
    EMAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    SMTP_SERVER: str    = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int      = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str  = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str  = os.getenv("SMTP_PASSWORD", "")
    CAM_EMAIL: str      = os.getenv("CAM_EMAIL", "")

    # CORS
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")


settings = Settings()
