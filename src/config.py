"""
Aqui é onde guardamos as configurações, como:
Token do whatsapp, phone number ID, Spreadsheet ID, Verify token e carrega isso automaticamente do .env.
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    WHATSAPP_TOKEN: str
    PHONE_NUMBER_ID: str
    VERIFY_TOKEN: str
    BASE_URL: str = "https://graph.facebook.com/v.20.0"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
