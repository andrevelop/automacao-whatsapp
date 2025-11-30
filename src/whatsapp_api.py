# Arquivo dedicado so ao whatsapp Cloud API, isso deixa o codigo limpo e modular.
import requests
from config import settings

def send_text_message(to_number: str, text: str):
    """
    Envia uma mensagem de texto usando a WhatsApp Cloud API.
    """
    url = f"{settings.BASE_URL}/{settings.PHONE_NUMBER_ID}/messages"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.META_TOKEN}"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }

    response = requests.post(url, json=payload, headers=headers)

    try:
        response.raise_for_status()
        return response.json()
    except:
        print("Erro ao enviar mensagem:", response.text)
        return None
