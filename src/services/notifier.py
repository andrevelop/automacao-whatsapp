from config import settings
from services.meta_client import send_message
from logs.log import log


def _get_field(row, idx):
    return row[idx] if len(row) > idx else ""


def format_notification(row):
    obra = _get_field(row, 0)
    etapa = _get_field(row, 1)
    material = _get_field(row, 2)
    quantidade = _get_field(row, 3)
    data_entrega = _get_field(row, 4)
    solicitante = _get_field(row, 5)
    observacoes = _get_field(row, 6)

    message = (
        "*NOVO PEDIDO SOLICITADO*\n\n"
        f"*Obra:* {obra}\n"
        f"*Etapa:* {etapa}\n"
        f"*Material:* {material}\n"
        f"*Quantidade:* {quantidade}\n"
        f"*Data Entrega:* {data_entrega}\n"
        f"*Solicitante:* {solicitante}\n"
        f"*Observações:* {observacoes}\n"
    )
    return message


def notify_number(number_id: str, row):
    """
    Envia a mensagem para number_id usando meta_client.send_message.
    Retorna True se enviado, False se falhou.
    """
    message = format_notification(row)
    log("raw", "notifier_message_formatada", {"number": number_id, "message": message})

    if settings.TEST_MODE:
        log("infra", "notifier_test_mode", {"number": number_id})
        return True

    success = send_message(number_id, message)

    if success:
        log("audit", "notifier_envio_sucesso", {"number": number_id})
        return True

    log("failed_delivery", "notifier_envio_erro", {"number": number_id})
    return False
