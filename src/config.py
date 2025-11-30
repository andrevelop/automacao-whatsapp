import os
import re
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Meta API
    META_TOKEN: str = os.getenv("META_TOKEN")
    PHONE_NUMBER_ID: str
    META_API_VERSION: str = "v20.0"

    # Google
    GOOGLE_SHEETS_ID: str | None = None
    GOOGLE_SERVICE_ACCOUNT_FILE: str | None = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    GOOGLE_SHEET_TAB: str | None = None

    # WhatsApp (grupo)
    WHATSAPP_GROUP_ID: str | None = None

    # Modo de teste / debug controláveis via .env
    TEST_MODE: bool = os.getenv("TEST_MODE", "false").lower() == "true"
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"


    @property
    def META_API_URL(self):
        return f"https://graph.facebook.com/{self.META_API_VERSION}/{self.PHONE_NUMBER_ID}/messages"

    class Config:
        env_file = ".env"
        extra = "ignore"

def validate_phone(number: str):
    if not re.fullmatch(r"\d{11,15}", number):
        raise ValueError(f"Telefone inválido detectado: {number}")
    
settings = Settings()
import os as _os
if getattr(settings, "GOOGLE_SERVICE_ACCOUNT_FILE", None):
    sa = settings.GOOGLE_SERVICE_ACCOUNT_FILE
    if not _os.path.exists(sa):
        raise FileNotFoundError(f"Arquivo de service account não encontrado: {sa}")

