#Aqui é o Servidor, onde roda a FastAPI, recebe webhooks do whatsapp e inicia rotas.
from flask import Flask, request, jsonify
from config import settings
from services.meta_client import send_text
from flow_engine import process_message
from logs.log import (
    log_event,
    log_error,
    log_infra,
    log_raw,
    log_system_error
)

app = Flask(__name__)

#1-WEBHOOK (verificação):

@app.route("/webhook", methods=["GET"])
def verify_token():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    print("hub.mode recebido:", mode)
    print("hub.verify_token recebido:", token)
    print("settings.VERIFY_TOKEN:", settings.VERIFY_TOKEN)

    if mode == "subscribe" and token == settings.VERIFY_TOKEN:
        return challenge, 200
    
    return "Erro: token inválido", 403

#2- RECEBIMENTO DE MENSAGENS (POST)

@app.route("/webhook", methods=["POST"])
def incoming_message():
    data = request.get_json()

    # Log RAW e infra
    log_raw(data)
    log_infra("webhook_post_recebido")

    try:
        value = data["entry"][0]["changes"][0]["value"]

        #Em caso de mensagem normal:
        if "messages" in value:
            message = value["messages"][0]
            phone = message["from"]
            text = message["text"]["body"]
        # Caso seja STATUS (entregue, lido, enviado) -> IGNORAR
        elif "statuses" in value:
            log_infra("webhook_status_ignorado", value["statuses"])
            return jsonify({"status": "status_ignorado"}), 200
        
        # Caso não tenha messages nem statuses -> payload estranho
        else:
            raise KeyError("Payload sem 'messages' ou 'statuses'")
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        log_system_error(f"Payload inválido recebido: {str(e)}", tb)
        return jsonify({"status": "erro_payload"}), 400
    
        # LOG 1 – Chegada da mensagem no webhook
        log_event(
            phone=phone,
            message_in=text,
            action="mensagem_recebida_no_webhook"
        )

        # Processar a mensagem no flow_engine
        resposta = process_message(phone, text)

        # Enviar resposta ao WhatsApp
        send_text(phone, resposta)

        # LOG 2 – Resposta enviada
        log_event(
            phone=phone,
            message_in=text,
            action="resposta_enviada",
            extra={"resposta": resposta}
        )

    except Exception as e:
        import traceback
        tb = traceback.format_exc()

        # ERRO DE INFRAESTRUTURA
        log_system_error(str(e), tb)

        # ERRO RELACIONADO AO USUÁRIO (somente se phone existir)
        if "phone" in locals():
            log_error(phone, str(e), tb)

        return jsonify({"status": "erro_interno"}), 500

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    log_infra("servidor_iniciado", {"porta": 5000})
    app.run(port=5000, debug=False)

# Link para validar o token: https://lydia-wordless-reda.ngrok-free.dev/webhook?hub.mode=subscribe&hub.verify_token=automacao123&hub.challenge=1234

