import json
import requests
from config import settings
from logs.log import log


def _post_to_meta(payload: dict):
    url = settings.META_API_URL
    token = settings.META_TOKEN

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    log("raw", "meta_payload_enviado", payload)

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)

        try:
            raw = resp.json()
        except Exception:
            raw = resp.text

        log("raw", "meta_raw_response", {"status": resp.status_code, "body": raw})

        if resp.status_code != 200:
            log("failed_delivery", "meta_http_error", {"status": resp.status_code, "body": resp.text})
        else:
            log("infra", "meta_http_ok", {"status": resp.status_code})

        return resp

    except requests.RequestException as e:
        log("failed_delivery", "meta_request_exception", {"erro": str(e)})
        return None
    except Exception as e:
        log("system_errors", "meta_exception", {"erro": str(e)})
        return None


def send_message(to: str, message: str):
    """
    API pública: envia texto via Meta (WhatsApp). Retorna True em sucesso, False em falha.
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    resp = _post_to_meta(payload)
    if resp is None:
        return False
    return resp.status_code == 200
