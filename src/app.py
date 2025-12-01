from flask import Flask
from logs.log import log
from services.scheduler import run_schedule
import threading
from services.google_client import get_unnotified_rows
from datetime import datetime
from config import settings

app = Flask(__name__)


@app.route("/")
def home():
    return "<h3>Servidor da automação está rodando ✓</h3>"


@app.route("/health")
def health_check():
    try:
        rows = get_unnotified_rows()
        pending = len(rows)

        log("infra", "INFO", "health_check_ok", {"pending": pending})

        status = "ok"
    except Exception as e:
        log("infra", "ERROR", "health_check_error", {"erro": str(e)})
        pending = None
        status = "error"

    return {
        "status": status,
        "pending_rows": pending,
        "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_mode": settings.TEST_MODE,
    }


def start_scheduler():
    """
    Roda o monitoramento da planilha em uma thread separada.
    """
    try:
        log("infra", "INFO", "scheduler_iniciado")
        run_schedule()
    except Exception as e:
        import traceback
        tb = traceback.format_exc()

        log("infra", "CRITICAL", "scheduler_erro", {
            "erro": str(e),
            "traceback": tb
        })


if __name__ == "__main__":
    log("infra", "INFO", "servidor_iniciado", {"porta": 5000})

    # Inicia o scheduler em paralelo
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=getattr(settings, "DEBUG_MODE", False),
        use_reloader=False
    )
