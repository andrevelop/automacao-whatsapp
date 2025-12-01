import time
from services.google_client import get_unnotified_rows, mark_row_notified
from services.notifier import notify_group
from logs.log import log  # novo logger unificado

GROUP_ID = "COLOQUE_AQUI_O_GROUP_ID"   # substitua depois


def run_schedule():
    """
    Loop simples que verifica a planilha a cada X segundos.
    """

    while True:
        try:
            print("🔄 Verificando planilha...")

            rows = get_unnotified_rows()

            # Loga INFRA SOMENTE quando houver novos pedidos
            if rows:
                log("infra", "INFO", "scheduler_novos_pedidos", {
                    "quantidade": len(rows)
                })

                # RAW completo das linhas também SOMENTE aqui
                log("raw", "INFO", "novos_pedidos_detectados", {
                    "quantidade": len(rows),
                    "linhas": rows
                })

                print(f"{len(rows)} novos pedidos encontrados!")

            else:
                print("Nenhuma nova linha.")  # evita spam no log

            # Enviar pedidos
            for row_index, row in rows:
                print(f"Enviando notificação da linha {row_index}...")

                log("infra", "INFO", "scheduler_envio_iniciado", {
                    "linha": row_index,
                    "conteudo": row
                })

                notify_group(GROUP_ID, row)
                mark_row_notified(row_index)

                log("infra", "INFO", "scheduler_envio_finalizado", {
                    "linha": row_index
                })

                print("Notificado e marcado como ENVIADO.\n")

        except Exception as e:
            print("⚠️ Erro no scheduler:", e)
            log("infra", "CRITICAL", "scheduler_erro", {"erro": str(e)})

        time.sleep(10)  # verifica a cada 10 segundos
