from config import settings
from services.meta_client import send_template
from logs.log import log


def _get_field(row, idx):
    return row[idx] if len(row) > idx else ""


def format_notification(row):
    """
    Converte a linha da planilha para o dicionário de variáveis
    exigido pelo template pedido_forms.
    """

    return {
        "obra": _get_field(row, 1),
        "etapa": _get_field(row, 2),
        "material": _get_field(row, 3),
        "quantidade": _get_field(row, 4),
        "data_entrega": _get_field(row, 5),
        "solicitante": _get_field(row, 6),
        "observacoes": _get_field(row, 7)
    }

def notify_number(number_id: str, row):
    obra = row[1]
    etapa = row[2]
    material = row[3]
    quantidade = row[4]
    data_entrega = row[5]
    solicitante = row[6]
    observacoes = row[7]

    variables = [
        obra,
        etapa,
        material,
        quantidade,
        data_entrega,
        solicitante,
        observacoes
    ]

    log("raw", "notifier_template_variaveis", {"vars": variables})

    if settings.TEST_MODE:
        log("infra", "notifier_test_mode", {"number": number_id})
        return "TESTE_WAMID"

    wamid = send_template(
        number_id,
        template_name="pedido_forms",  # nome do template novo
        variables=variables
    )

    if wamid:
        log("audit", "notifier_envio_sucesso", {"number": number_id, "wamid": wamid})
        return wamid

    log("failed_delivery", "notifier_envio_erro", {"number": number_id})
    return False

