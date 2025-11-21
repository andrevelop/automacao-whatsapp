"""
É o cerebro do BOT. Ele recebe a mensagem e decide se vai: 
>Interpretar a mensagem recebida.   
>Decidir qual fluxo seguir.
>Retornar resposta que o servidor enviará para o usuário.
>Registrar lead
>Consultar planilha
>Responder texto
>Criar menus
>Seguir etapas.
"""
import unicodedata

# memória temporária para armazenar o estado de cada usuário
user_sessions = {}


def normalize(text):
    """Remove acentos e deixa tudo em minúsculo."""
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")
    return text.strip()


def process_message(phone, text):
    text_norm = normalize(text)
    print("Texto normalizado:", text_norm)

    # cria sessão se não existir
    if phone not in user_sessions:
        user_sessions[phone] = {"stage": "inicio"}

    stage = user_sessions[phone]["stage"]

    # --------------------
    # FLUXO PRINCIPAL
    # --------------------

    # 1) Fluxo simples para "oi", "olá"
    if stage == "inicio":
        if any(greet in text_norm for greet in ["oi", "ola", "bom dia", "boa tarde", "boa noite"]):
            return (
                "Olá! 👋\n"
                "Eu sou seu assistente de automação.\n\n"
                "Escolha uma opção:\n"
                "1️⃣ - Registrar um lead\n"
                "2️⃣ - Saber mais sobre automação\n"
                "3️⃣ - Falar com atendente"
            )

        if text_norm == "1":
            user_sessions[phone]["stage"] = "registrando_nome"
            return "Ótimo! Vamos registrar um lead.\nPrimeiro, qual é o *nome* da pessoa?"

        if text_norm == "2":
            return "Automação é incrível! Em breve teremos mais informações automáticas aqui 🙂"

        if text_norm == "3":
            return "Beleza! Vou te direcionar para um atendente (modo fake por enquanto)."

        return "Não entendi, pode repetir? Digite 'oi' para começar o menu."

    # 2) Fluxo: registrando nome
    if stage == "registrando_nome":
        user_sessions[phone]["temp_nome"] = text
        user_sessions[phone]["stage"] = "registrando_telefone"
        return "Perfeito! Agora me informe o *telefone* do lead."

    # 3) Fluxo: registrando telefone
    if stage == "registrando_telefone":
        nome = user_sessions[phone].get("temp_nome")
        telefone = text

        # aqui depois vamos salvar no Google Sheets
        user_sessions[phone]["stage"] = "inicio"  # finaliza fluxo

        return (
            f"Lead registrado com sucesso!\n\n"
            f"📌 Nome: {nome}\n"
            f"📌 Telefone: {telefone}"
        )

