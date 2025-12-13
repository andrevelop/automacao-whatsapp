from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from logs.log import log
from services.scheduler import run_scheduler, PENDING
from services.google_client import get_unnotified_rows
from config import settings
from datetime import datetime
from services.google_client import mark_row_notified

app = Flask(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=["10 per minute"])
limiter.init_app(app)

# ROTA PRINCIPAL
@app.route("/")
def home():
    log("infra", "rota_home", {})
    return "<h3>Servidor da automação está rodando ✓</h3>"

# HEALTH CHECK
@app.route("/health")
def health_check():
    try:
        pending = len(get_unnotified_rows())
        log("infra", "health_check_ok", {"pending": pending})
        return {
            "status": "ok",
            "pending_rows": pending,
            "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "test_mode": settings.TEST_MODE
        }
    except Exception as e:
        log("system_errors", "health_check_error", {"erro": str(e)})
        return {"status": "error"}

# WEBHOOK — OBRIGATÓRIO PARA META
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    log("raw", "webhook_evento_recebido", data)

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "statuses" in value:
            status_obj = value["statuses"][0]
            wamid = status_obj.get("id")
            status = status_obj.get("status")

            if status == "sent" and wamid in PENDING:
                row_index = PENDING.pop(wamid)
                mark_row_notified(row_index, "ENVIADO")
                log("audit", "webhook_mensagem_enviada", {"wamid": wamid, "linha": row_index})

    except Exception as e:
        log("system_errors", "webhook_process_error", {"erro": str(e)})

    return "EVENT_RECEIVED", 200


# START SERVER
if __name__ == "__main__":
    log("infra", "servidor_iniciado", {"porta": 5000})
    run_scheduler()
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=getattr(settings, "DEBUG_MODE", False),
        use_reloader=False
    )
