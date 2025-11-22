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

#Pasta onde os logs serão salvos:
LOG_DIR_USERS = "logs_data"
LOG_DIR_INFRA = "logs_infra"
LOG_DIR_RAW = "logs_raw"

#Garante que a pasta exista, criando automaticamente: 
for folder in [LOG_DIR_USERS, LOG_DIR_INFRA, LOG_DIR_RAW]:
      if not os.path.exists(folder):
            os.makedirs(folder)

#Logs de INFRAESTRUTURA:
def log_infra(action, detail=None):
    """
    Logs gerais deinfraestrutura.
    - Erros do servidor
    - Início e fim de rotas
    - Eventos internos
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    filename = f"{LOG_DIR_INFRA}/{date_str}.log"
    
    log_entry = {
        "timestamp": timestamp,
        "action": action,
        "detail": detail,
    }

    with open(filename, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

# Log RAW (payload bruto do webhook):
def log_raw(raw_payload):
    """
     Salva a aquisição recebida do webhook exatamente como veio.
     Debug que indica quando algo quebrar na Meta API.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{LOG_DIR_RAW}/{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(json.dumps(raw_payload, ensure_ascii=False, indent=2))
             
#Log por USUÁRIO:
def log_event(phone, message_in, action, state_before=None, state_after=None, extra=None):
    """
    Registra eventos importantes do bot para auditoria e debug.
    
    phone > Número do usuário
    message_in > Mensagem recebida
    action > O que o bot decidiu fazer
    state_before > Estado do usuário antes do processamento
    state_after > Estado do usuário depois do processamento
    extra > Dados extras (opcional)
    """

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # Nome do arquivo: logs por usuário e por dia
    filename = f"{LOG_DIR_USERS}/{phone}_{date_str}.log"

    log_entry = {
        "timestamp": timestamp,
        "phone": phone,
        "message_in": message_in,
        "action": action,
        "state_before": state_before,
        "state_after": state_after,
        "extra": extra,
    }

    #Escreve no arquivo
    with open(filename, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

#Log de ERRO POR USUÁRIO:
def log_error(phone, error_message, traceback_str=None):
    """
    Registra erros de execução que ocorrerem 
    no fluxo relacionados ao usuário.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    filename = f"{LOG_DIR_USERS}/{phone}_{date_str}_ERROR.log"
        
    log_entry = {
        "timestamp": timestamp,
        "phone": phone,
        "error": error_message,
        "traceback": traceback_str,
    }
  
    with open(filename, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

#Log de ERROS NA INFRAESTRUTURA DO SERVIDOR:
def log_system_error(error_message, traceback_str=None):
    """
    Registra erros relacionados à infraestrutura do sistema:
    - Erros no servidor Flask
    - Exceções que não envolvem fluxo do usuário
    - Problemas ao receber payloads do webhook
    - Falhas de comunicação geral

    Diferente do log_error(), este NÃO é por usuário,
    e fica armazenado em logs_infra/.
    """

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    filename = f"{LOG_DIR_INFRA}/{date_str}_ERROR.log"

    log_entry = {
        "timestamp": timestamp,
        "error": error_message,
        "traceback": traceback_str,
    }

    with open(filename, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
