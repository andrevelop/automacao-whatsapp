from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from logs.log import log
from services.scheduler import run_scheduler
from services.google_client import get_unnotified_rows
from config import settings
from datetime import datetime

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
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # 1) VERIFICAÇÃO DO FACEBOOK (GET)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        # Logs úteis para debug
        log("infra", "webhook_verificacao", {
            "mode": mode, 
            "token": token
        })

        if mode == "subscribe" and token == settings.VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Erro: token inválido", 403

    # 2) RECEBENDO EVENTOS (POST)
    if request.method == "POST":
        data = request.json
        log("raw", "webhook_evento_recebido", data)
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
