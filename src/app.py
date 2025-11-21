#Aqui é o Servidor, onde roda a FastAPI, recebe webhooks do whatsapp e inicia rotas.
from flask import Flask, request, jsonify
from config import settings
from whatsapp_api import send_text_message
from flow_engine import process_message

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

#2- RECEBIMENTO DE MENSAGENS

@app.route("/webhook", methods=["POST"])
def incoming_message():
    data = request.get_json()

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        phone = message["from"]
        text = message["text"]["body"]

        resposta = process_message(phone, text)
    
    #Debug:
        print("Mensagem recebida de:", phone)
        print("Conteúdo recebido:", text)
        print("Resposta gerada pelo flow:", resposta)
    #Debug.fim.
        send_text_message(phone, resposta)
    except Exception as e:
        print("Erro ao processar mensagem:", e)

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(port=5000, debug=False)

# Link para validar o token: https://lydia-wordless-reda.ngrok-free.dev/webhook?hub.mode=subscribe&hub.verify_token=automacao123&hub.challenge=1234

