import os
import json
from datetime import datetime

#   CONFIGURAÇÃO DE PASTAS
BASE_DIR = os.path.join(os.getcwd(), "logs")

LOG_FOLDERS = {
    "raw": "raw",
    "infra": "infra",
    "failed_delivery": "failed_delivery",
    "google_errors": "google_errors",
    "system_errors": "system_errors",
    "audit": "audit"
}

# Cria todas as pastas se não existirem
for folder in LOG_FOLDERS.values():
    path = os.path.join(BASE_DIR, folder)
    os.makedirs(path, exist_ok=True)

#   FUNÇÕES AUXILIARES
def timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def json_datetime():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


#   MOTOR DE LOG
def write_log(folder_key: str, event: str, details: dict):
    """
    folder_key: chave dentro de LOG_FOLDERS (ex: 'infra', 'raw', etc.)
    event: nome curto do evento (ex: scheduler_iniciado)
    details: dicionário com informações do evento
    """
    folder = LOG_FOLDERS.get(folder_key)

    if not folder:
        raise ValueError(f"Pasta de log inválida: {folder_key}")

    log_dir = os.path.join(BASE_DIR, folder)

    file_name = f"{event}_{timestamp()}.json"
    file_path = os.path.join(log_dir, file_name)

    payload = {
        "timestamp": json_datetime(),
        "event": event,
        "details": details
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4, ensure_ascii=False)

    return True


#   API SIMPLIFICADA PARA LOGS ESPECÍFICOS
def log_raw(event: str, data: dict):
    return write_log("raw", event, data)


def log_infra(event: str, data: dict):
    return write_log("infra", event, data)


def log_failed(event: str, data: dict):
    return write_log("failed_delivery", event, data)


def log_google_error(event: str, data: dict):
    return write_log("google_errors", event, data)


def log_system_error(event: str, data: dict):
    return write_log("system_errors", event, data)


def log_audit(event: str, data: dict):
    return write_log("audit", event, data)


#   🚀 FUNÇÃO PRINCIPAL COMPATÍVEL COM O RESTANTE DO PROJETO
def log(category: str, event: str, data: dict):
    """
    API unificada para logs — compatível com o projeto inteiro.
    Exemplo:
        log("infra", "scheduler_iniciado", {"x": 1})
    """

    if category == "raw":
        return log_raw(event, data)

    if category == "infra":
        return log_infra(event, data)

    if category == "failed_delivery":
        return log_failed(event, data)

    if category == "google_errors":
        return log_google_error(event, data)

    if category == "system_errors":
        return log_system_error(event, data)

    if category == "audit":
        return log_audit(event, data)

    raise ValueError(f"Categoria inválida enviada ao log(): {category}")
