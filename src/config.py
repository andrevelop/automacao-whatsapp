import os
import re
import sys
from pydantic_settings import BaseSettings
from logs.log import (
    log_system_error,
    log_infra
)


class Settings(BaseSettings):
    # Meta API
    META_TOKEN: str = os.getenv("META_TOKEN")
    PHONE_NUMBER_ID: str = os.getenv("PHONE_NUMBER_ID")
    META_API_VERSION: str = "v20.0"
    VERIFY_TOKEN: str = os.getenv("VERIFY_TOKEN")

    # Google
    GOOGLE_SHEETS_ID: str | None = os.getenv("GOOGLE_SHEETS_ID")
    GOOGLE_SERVICE_ACCOUNT_FILE: str | None = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")

    # Modos de operação
    TEST_MODE: bool = os.getenv("TEST_MODE", "false").lower() == "true"
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"

    # Destinatário da notificação
    WHATSAPP_NUMBER: str | None = os.getenv("WHATSAPP_NUMBER")

    @property
    def META_API_URL(self):
        return f"https://graph.facebook.com/{self.META_API_VERSION}/{self.PHONE_NUMBER_ID}/messages"

    class Config:
        env_file = ".env"
        extra = "ignore"



def validate_phone(number: str):
    """
    Valida telefone internacional usado pela API da Meta.
    """
    if not re.fullmatch(r"\d{11,15}", number):
        log_system_error("config_telefone_invalido", {"telefone": number})
        raise ValueError(f"Telefone inválido detectado: {number}")

#       INICIALIZAÇÃO
settings = Settings()

log_infra("config_carregado", {
    "TEST_MODE": settings.TEST_MODE,
    "DEBUG_MODE": settings.DEBUG_MODE,
    "GOOGLE_SHEETS_ID": settings.GOOGLE_SHEETS_ID is not None,
    "SERVICE_ACCOUNT_FILE": settings.GOOGLE_SERVICE_ACCOUNT_FILE
})

#       VALIDAÇÃO DO SERVICE ACCOUNT
sa_file = settings.GOOGLE_SERVICE_ACCOUNT_FILE

if sa_file:
    if not os.path.exists(sa_file):
        log_system_error("config_service_account_inexistente", {
            "arquivo_esperado": sa_file
        })
        sys.exit(f"ERRO: Arquivo de service account não encontrado: {sa_file}")
