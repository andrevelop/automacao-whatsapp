import requests
from config import settings
from logs.log import log_infra, log_system_error

def _post_meta(payload):
    """Função interna para enviar requisição POST para a API da Meta.
    Faz logs automáticos de sucesso e erro.
    """
    url = settings.META_API_URL
    token = settings.META_TOKEN
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try: 
        #Log antes da requisição:
        log_infra("meta_request_enviada", {"payload": payload})

        response = requests.post(url, headers=headers, json=payload)

        #Log após a requisição:
        log_infra("meta_response_recebida", {
            "status_code": response.status_code,
            "response_text": response.text
        })

        return response
    
    except Exception as e:
        log_system_error("meta_request_falhou", {"erro": str(e)})
        return None
    
def send_text(to: str, message: str):
    """
    Envia uma mensagem de texto simples usando a API da Meta.
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    return _post_meta(payload)
