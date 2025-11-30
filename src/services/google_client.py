import os
from config import settings
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Configurações
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SPREADSHEET_ID = settings.GOOGLE_SHEETS_ID
SERVICE_ACCOUNT_FILE = settings.GOOGLE_SERVICE_ACCOUNT_FILE


# ----------------------------
# FUNÇÃO INTERNA PARA CRIAR O SERVICE
# ----------------------------
def _get_service():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds).spreadsheets()


# ----------------------------
# FUNÇÃO: converter número de coluna → letra (1=A, 2=B, 27=AA)
# ----------------------------
def col_number_to_letter(n):
    """Converte número de coluna (1=A) para letra (ex: 26=Z, 27=AA)."""
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result


# ----------------------------
# LER A PLANILHA COMPLETA
# ----------------------------
def read_sheet():
    service = _get_service()

    # Ler tudo dinamicamente: só pedimos o range A:zzzz
    # O Sheets só retorna até onde existirem dados.
    result = service.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="A:ZZZ"   # suporta até centenas de colunas
    ).execute()

    values = result.get("values", [])
    return values


# ----------------------------
# DESCOBRIR AUTOMATICAMENTE A ÚLTIMA COLUNA EXISTENTE
# ----------------------------
def get_last_column_index():
    """
    Lê a primeira linha da planilha e retorna o número da última coluna existente.
    Exemplo: se há 14 colunas, retorna 14.
    """
    rows = read_sheet()
    if not rows:
        return 1
    return len(rows[0])


# ----------------------------
# IDENTIFICAR A COLUNA DE CONTROLE "NOTIFICADO"
# SEMPRE É A ÚLTIMA + 1
# ----------------------------
def get_notify_column_letter():
    last_col_index = get_last_column_index()     # ex: 14
    notify_col_index = last_col_index + 1        # ex: 15
    return col_number_to_letter(notify_col_index)  # ex: 15 → O


# ----------------------------
# Pegar as linhas NÃO notificadas
# ----------------------------
def get_unnotified_rows():
    rows = read_sheet()
    unnotified = []

    # descobrir qual coluna será usada para marcar
    notify_col_letter = get_notify_column_letter()
    notify_col_index = get_last_column_index()  # última coluna real
    # a coluna de "controle" é notify_col_index (0-based)
    # mas rows usam índice 0-based → então ajustamos:
    control_index = notify_col_index

    for index, row in enumerate(rows, start=1):

        if index == 1:
            continue  # pular cabeçalho

        enviado = row[control_index] if len(row) > control_index else ""

        if enviado.strip() == "":
            unnotified.append((index, row))

    return unnotified


# ----------------------------
# Marcar linha como notificada (dinâmico)
# ----------------------------
def mark_row_notified(row_index, text="ENVIADO"):
    service = _get_service()

    notify_letter = get_notify_column_letter()  # exemplo: "O"
    range_ = f"{notify_letter}{row_index}"

    body = {"values": [[text]]}

    service.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_,
        valueInputOption="RAW",
        body=body
    ).execute()

    return True
