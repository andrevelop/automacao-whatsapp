# src/scheduler.py
"""
Scheduler simplificado: roda em loop, verifica planilha a cada X segundos,
envia notificações para linhas não-notificadas e marca como Notificado.
Uso: python scheduler.py
"""

import time
import os
from services.google_client import get_unnotified_rows, mark_row_notified
from services.notifier import notify_group
import time

GROUP_ID = "COLOQUE_AQUI_O_GROUP_ID"   # depois você substitui


def run_schedule():
    """
    Loop simples que roda a cada X segundos.
    Pode ser trocado por APScheduler depois.
    """
    while True:
        print("🔄 Verificando planilha...")

        # pega linhas que não foram notificadas
        rows = get_unnotified_rows()

        if not rows:
            print("Nenhuma nova linha.")
        else:
            print(f"{len(rows)} novos pedidos encontrados!")

        for row_index, row in rows:
            print(f"Enviando notificação da linha {row_index}...")
            notify_group(GROUP_ID, row)
            mark_row_notified(row_index)
            print("Notificado e marcado como ENVIADO.\n")

        time.sleep(10)   # verifica a cada 10 segundos
