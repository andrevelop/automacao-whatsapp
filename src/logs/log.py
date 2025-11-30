import os
import datetime
import json

"""
Atualmente esse sistema de logs está gravando:
- Logs por usuário (eventos normais)
- Logs de erro por usuário
- Logs de infraestrutura (erro geral, eventos internos)
- Logs RAW (payload bruto recebido no webhook)
"""

# Diretório BASE do módulo de logs (sempre relativo ao arquivo atual)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#Pasta onde os logs serão salvos:
LOG_DIR_INFRA = os.path.join(BASE_DIR, "logs_infra")
LOG_DIR_RAW = os.path.join(BASE_DIR, "logs_raw")

#Garante que a pasta exista, criando automaticamente: 
for folder in [LOG_DIR_INFRA, LOG_DIR_RAW]:
    os.makedirs(folder, exist_ok=True)

def _write_log(directory, filename, log_entry):
    """Função interna especificada com o "_" no início da função,
    essa função grava todos os logs em formato padrão JSON"""
    filepath = os.path.join(directory, filename)

    with open (filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

#Logs de INFRAESTRUTURA (eventos normais dda infraestrutura):
def log_infra(action, detail=None, level="INFO"):
    """
    Logs gerais deinfraestrutura.
    - Erros do servidor
    - Início e fim de rotas
    - Eventos internos
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "action": action,
        "detail": detail,
    }
    
    filename = f"{date_str}.log"
    _write_log(LOG_DIR_INFRA, filename, log_entry)

# Log RAW (salva payload bruto vindo da META API):
def log_raw(raw_payload, level="DEBUG"):
    """
     Salva a aquisição recebida do webhook exatamente como veio.
     Debug que indica quando algo quebrar na Meta API.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "payload": raw_payload
    }
    filename = f"{timestamp}.json"
    _write_log(LOG_DIR_RAW, filename, log_entry)

#Log de ERROS NA INFRAESTRUTURA DO SERVIDOR (erros que acontece fora do fluxo do user, relacionado ao sistema):
def log_system_error(error_message, traceback_str=None, level="CRITICAL"):
    """
    Registra erros relacionados à infraestrutura do sistema:
    - Erros no servidor Flask
    - Exceções que não envolvem fluxo do usuário
    - Problemas ao receber payloads do webhook
    - Falhas de comunicação geral
    """

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "error": error_message,
        "traceback": traceback_str,
    }
    
    filename = f"{date_str}_SYSTEM_ERROR.log"
    _write_log(LOG_DIR_INFRA, filename, log_entry)
