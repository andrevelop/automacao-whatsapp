#Aqui é o Servidor, onde roda a FastAPI, recebe webhooks do whatsapp e inicia rotas.
from flask import Flask
from logs.log import log_infra, log_system_error
from services.scheduler import run_schedule
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "<h3>Servidor da automação está rodando ✓</h3>"

def start_scheduler():
    """
    Roda o monitoramento da planilha em uma thread separada.
    Isso permite que o Flask rode normalmente.
    """
    try:
        log_infra("scheduler_iniciado")
        run_schedule()
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        log_system_error(str(e), tb)

if __name__ == "__main__":
    from config import settings  # import local para controlar debug via .env

    log_infra("servidor_iniciado", {"porta": 5000})

    # Inicia o scheduler em paralelo
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()

    # Iniciar o servidor Flask apenas uma vez, com debug controlado pelo .env
    app.run(host="0.0.0.0", port=5000, debug=getattr(settings, "DEBUG_MODE", False), use_reloader=False)
