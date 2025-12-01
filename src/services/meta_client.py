import requests
from config import settings
from logs.log import log


def _post_meta(payload):
    """
    Envia POST para a API da Meta.
    Gera logs completos:
      - infra: request e response
      - raw: payload bruto enviado e recebido
    """

    url = settings.META_API_URL
    token = settings.META_TOKEN
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Log infraestrutura: envio
    log("infra", "INFO", "meta_request_enviada", {"payload": payload})

    # Log RAW: o request bruto enviado
    log("raw", "INFO", "meta_raw_request", payload)

    try:
        response = requests.post(url, headers=headers, json=payload)

        # Log do RAW da resposta
        try:
            raw_response = response.json()
        except Exception:
            raw_response = response.text
        
        log("raw", "INFO", "meta_raw_response", raw_response)

        # Log de infraestrutura
        level = "INFO" if response.status_code == 200 else "ERROR"

        log("infra", level, "meta_response_recebida", {
            "status_code": response.status_code,
            "response_text": response.text
        })

        return response
    
    except Exception as e:
        log("infra", "CRITICAL", "erro_meta_exception", {"erro": str(e)})
        return None



def send_text(to: str, message: str):
    """
    Envia uma mensagem simples de texto pelo WhatsApp Business API.
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    return _post_meta(payload)
