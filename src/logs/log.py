import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")

# Dicionário de categorias → pastas
CATEGORIES = {
    "infra": "logs_infra",
    "raw": "logs_raw"
}

# Cria as pastas se não existirem
for folder in CATEGORIES.values():
    os.makedirs(os.path.join(LOG_DIR, folder), exist_ok=True)


def log(category: str, level: str, action: str, detail: dict = None):
    """
    Logger unificado para todo o sistema.

    category: "infra" | "raw"
    level:    "INFO" | "ERROR" | "CRITICAL"
    action:   Ação principal que está sendo registrada
    detail:   Dados complementares ou payload
    """

    if category not in CATEGORIES:
        raise ValueError(f"Categoria inválida: {category}")

    folder = CATEGORIES[category]
    timestamp = datetime.now()
    date_str = timestamp.strftime("%Y-%m-%d")
    time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    # Nome do arquivo
    filename = (
        f"{date_str}.log" if category == "infra"
        else f"{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    )

    filepath = os.path.join(LOG_DIR, folder, filename)

    # Monta entrada do log
    entry = {
        "timestamp": time_str,
        "level": level,
        "action": action,
        "detail": detail or {}
    }

    # Escreve o log
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
