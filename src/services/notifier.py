"""
Responsável por:
 - Gerar mensagem formatada
 - Registrar logs RAW da mensagem enviada
 - Registrar logs INFRA de envio / falha
 - Encaminhar mensagem para a Meta via meta_client
"""

from config import settings
from services.meta_client import send_text
from logs.log import log  # Logger unificado


def _get(row, index):
    """Retorna valor seguro da lista sem quebrar."""
    return row[index] if len(row) > index else ""


def format_notification(row):
    """
    Cria mensagem WhatsApp a partir de uma linha da planilha.
    """

    obra = _get(row, 0)
    etapa = _get(row, 1)
    material = _get(row, 2)
    quantidade = _get(row, 3)
    data_entrega = _get(row, 4)
    solicitante = _get(row, 5)
    observacoes = _get(row, 6)

    message = (
        "📦 *NOVO PEDIDO SOLICITADO*\n\n"
        f"🏗 *Obra:* {obra}\n"
        f"📍 *Etapa:* {etapa}\n"
        f"📦 *Material:* {material}\n"
        f"🔢 *Quantidade:* {quantidade}\n"
        f"📅 *Data Entrega:* {data_entrega}\n"
        f"👤 *Solicitante:* {solicitante}\n"
        f"📝 *Observações:* {observacoes}\n"
    )

    return message


def notify_group(group_id, row):
    """
    Envia a mensagem para o grupo WhatsApp.
    Produz logs RAW e INFRA para auditoria total.
    """

    message = format_notification(row)

    # Log RAW do conteúdo gerado
    log("raw", "INFO", "notifier_message_formatada", {
        "group": group_id,
        "message": message
    })

    # Se estiver em TEST MODE → não envia, só loga
    if settings.TEST_MODE:
        print(f"[TEST_MODE] Mensagem NÃO enviada para: {group_id}")
        print(f"[TEST_MODE] Conteúdo:\n{message}\n")

        log("infra", "INFO", "notifier_test_mode", {
            "group": group_id,
            "message": message
        })

        return {
            "status": "TEST_MODE",
            "group": group_id,
            "message": message
        }

    # Envio real
    response = send_text(group_id, message)

    # Caso send_text retorne None (erro interno)
    if response is None:
        log("infra", "CRITICAL", "notifier_envio_falhou", {
            "group": group_id,
            "erro": "send_text retornou None"
        })
        return {"status": "ERROR", "detail": "send_text retornou None"}

    # Caso a API responda com erro HTTP
    if response.status_code != 200:
        log("infra", "ERROR", "notifier_http_error", {
            "group": group_id,
            "status_code": response.status_code,
            "response": response.text
        })
        return {"status": "ERROR", "detail": response.text}

    # Sucesso
    log("infra", "INFO", "notifier_envio_sucesso", {
        "group": group_id,
        "response": response.text
    })

    return {"status": "OK", "detail": response.text}
