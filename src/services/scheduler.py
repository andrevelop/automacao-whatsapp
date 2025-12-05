import threading
import time
from datetime import datetime
from logs.log import log
from config import settings
from services.google_client import get_unnotified_rows, mark_row_notified
from services.notifier import notify_number

# Intervalo entre checagens (segundos).
# Se você quiser alterar sem tocar no código, defina CHECK_INTERVAL no settings/.env.
CHECK_INTERVAL = getattr(settings, "CHECK_INTERVAL", 10)


def _is_send_success(result):
    """
    Normaliza o resultado do notify_number para True/False.
    Aceita:
      - booleano True/False
      - dict com chave "status" == "OK" (case-insensitive)
      - objeto com atributo status_code (ex.: requests.Response)
    """
    try:
        if isinstance(result, bool):
            return result
        if isinstance(result, dict):
            status = str(result.get("status", "")).strip().upper()
            return status in ("OK", "SUCCESS", "200")
        # duck-typing: requests.Response ou similar
        if hasattr(result, "status_code"):
            return getattr(result, "status_code") == 200
    except Exception:
        pass
    return False


def _process_one(row_index: int, row):
    """
    Processa uma única linha: chama notifier e atualiza a planilha com ENVIADO ou FALHOU <ts>.
    """
    log("infra", "scheduler_envio_iniciado", {"linha": row_index})

    try:
        # chama o notifier (notify_number espera number_id, row)
        result = notify_number(settings.WHATSAPP_NUMBER, row)

        success = _is_send_success(result)

        if success:
            # marca ENVIADO
            ok = mark_row_notified(row_index, "ENVIADO")
            log("audit", "scheduler_envio_ok", {"linha": row_index, "mark_ok": ok})
        else:
            # marca FALHOU com timestamp
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            ok = mark_row_notified(row_index, f"FALHOU {ts}")
            log("failed_delivery", "scheduler_envio_falhou", {
                "linha": row_index,
                "mark_ok": ok,
                "notifier_result": str(result)
            })
    except Exception as e:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        try:
            mark_row_notified(row_index, f"FALHOU {ts}")
        except Exception:
            # se não conseguir escrever, ao menos loga o erro
            log("system_errors", "scheduler_mark_failed_exception", {"linha": row_index, "erro": str(e)})
        log("system_errors", "scheduler_exception_process_one", {"linha": row_index, "erro": str(e)})


def _loop():
    """
    Loop principal do scheduler.
    - Não gera logs quando não há pendentes (evita spam).
    - Quando há pendentes, gera logs relevantes.
    """
    log("infra", "scheduler_thread_iniciada", {})

    while True:
        try:
            pendentes = get_unnotified_rows()  # deve retornar lista de tuples (index, row)

            if not pendentes:
                # sem pendentes: não gera logs e vai dormir
                time.sleep(CHECK_INTERVAL)
                continue

            # há pendentes: log uma única vez antes do processamento
            log("infra", "scheduler_verificacao", {"quantidade": len(pendentes)})
            log("infra", "scheduler_novos_pedidos", {"quantidade": len(pendentes)})

            # processa cada item (row_index, row_list)
            for item in pendentes:
                # compatibilidade com formatos: tupla (idx,row) ou dict {"index":..., "data":...}
                if isinstance(item, tuple) and len(item) == 2:
                    row_index, row = item
                elif isinstance(item, dict) and "index" in item and "data" in item:
                    row_index, row = item["index"], item["data"]
                else:
                    # formato inesperado — loga e pula
                    log("system_errors", "scheduler_item_formato_invalido", {"item": str(item)})
                    continue

                _process_one(row_index, row)

        except Exception as e:
            log("system_errors", "scheduler_loop_exception", {"erro": str(e)})

        # espera antes da próxima iteração
        time.sleep(CHECK_INTERVAL)


def run_scheduler():
    """
    Inicia a thread do scheduler (API pública).
    """
    log("infra", "run_scheduler_started", {"interval": CHECK_INTERVAL})

    t = threading.Thread(target=_loop, daemon=True)
    t.start()

    return t
