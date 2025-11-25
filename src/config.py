from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    WHATSAPP_TOKEN: str
    PHONE_NUMBER_ID: str
    VERIFY_TOKEN: str

    @property
    def BASE_URL(self):
        # Sempre use a versão correta da API
        return "https://graph.facebook.com/v20.0"

    @property
    def META_API_URL(self):
        # Endpoint completo de envio de mensagens
        return f"{self.BASE_URL}/{self.PHONE_NUMBER_ID}/messages"

    @property
    def META_TOKEN(self):
        return self.WHATSAPP_TOKEN

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
