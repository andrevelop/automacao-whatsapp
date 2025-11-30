"""
Gera a mensagem formatada a partir dos dados lidos no Sheets e envia via meta_client.send_text.
Modo TEST_MODE usa printing em vez de envio real.
Para envio real somente quando cadastrar o número(chip).
"""
from config import settings
from services.meta_client import send_text
from logs.log import log_system_error, log_infra

TEST_MODE = settings.TEST_MODE

def format_notification(row):
    """
    row = lista com colunas da planilha
    Ajuste os índices de acordo com sua planilha real.
    """

    obra = row[0] if len(row) > 0 else ""
    etapa = row[1] if len(row) > 1 else ""
    material = row[2] if len(row) > 2 else ""
    quantidade = row[3] if len(row) > 3 else ""
    data_entrega = row[4] if len(row) > 4 else ""
    solicitante = row[5] if len(row) > 5 else ""
    observacoes = row[6] if len(row) > 6 else ""

    return (
        "📦 *NOVO PEDIDO SOLICITADO*\n\n"
        f"🏗 *Obra:* {obra}\n"
        f"📍 *Etapa:* {etapa}\n"
        f"📦 *Material:* {material}\n"
        f"🔢 *Quantidade:* {quantidade}\n"
        f"📅 *Data Entrega:* {data_entrega}\n"
        f"👤 *Solicitante:* {solicitante}\n"
        f"📝 *Observações:* {observacoes}\n"
    )


def notify_group(group_id, row):
    """
    group_id → ID do grupo WhatsApp que vai receber a mensagem
    row → lista de valores da planilha
    """

    message = format_notification(row)

    # Modo de teste: não envia nada, apenas loga/retorna para inspeção
    if getattr(settings, "TEST_MODE", False):
        # imprimir é suficiente para debug; você também pode usar seus logs
        print(f"[TEST_MODE] Mensagem NÃO enviada para: {group_id}")
        print(f"[TEST_MODE] Conteúdo:\n{message}\n")
        return {"status": "TEST_MODE", "group": group_id, "message": message}

    # Envio real (quando TEST_MODE == False)
    return send_text(group_id, message)
