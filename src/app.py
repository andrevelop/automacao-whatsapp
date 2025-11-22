#Aqui é o Servidor, onde roda a FastAPI, recebe webhooks do whatsapp e inicia rotas.
from flask import Flask, request, jsonify
from config import settings
from whatsapp_api import send_text_message
from flow_engine import process_message
from logs.log import log_event, log_error

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

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        phone = message["from"]
        text = message["text"]["body"]

        # LOG 1 - Registrar chegada da menwsagem do webhook
        log_event(
            phone=phone,
            message_in=text,
            action="mensagem_recebida_no_webhook"
        )
        #Processar a mensagem no flow_engine:

        resposta = process_message(phone, text)
    
        send_text_message(phone, resposta)

        #LOG 2 - Registrar resposta enviada ao usuário.

        log_event(
            phone=phone,
            message_in=text,
            action="resposta_enviada",
            extra={"resposta": resposta}
        )
    except Exception as e:
        import traceback
        print("Erro ao processar mensagem:", e)

        # LOG 3 - Registrar erros (log separado)
        log_error(
            phone=phone if "phone" in locals() else "DESCONHECIDO",
            error_message=str(e),
            traceback_str=traceback.format_exc()
        )

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(port=5000, debug=False)

# Link para validar o token: https://lydia-wordless-reda.ngrok-free.dev/webhook?hub.mode=subscribe&hub.verify_token=automacao123&hub.challenge=1234

