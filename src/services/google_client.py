import os
from config import settings
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from logs.log import log

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SPREADSHEET_ID = settings.GOOGLE_SHEETS_ID
SERVICE_ACCOUNT_FILE = settings.GOOGLE_SERVICE_ACCOUNT_FILE


def _get_service():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds).spreadsheets()


# Convert number to column letter
def col_number_to_letter(n):
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result


# Read sheet once
def read_sheet():
    try:
        service = _get_service()

        result = service.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range="A:ZZZ"
        ).execute()

        values = result.get("values", [])

        return values

    except Exception as e:
        log("infra", "CRITICAL", "erro_ler_planilha", {"erro": str(e)})
        return []


# Last column
def get_last_column_index_from_rows(rows):
    if not rows:
        return 1
    return len(rows[0])


# Notify column
def get_notify_column_letter_from_rows(rows):
    last_index = get_last_column_index_from_rows(rows)
    return col_number_to_letter(last_index + 1)


# Get unnotified rows
def get_unnotified_rows():
    rows = read_sheet()

    if not rows:
        return []

    control_index = get_last_column_index_from_rows(rows)

    unnotified = []

    for index, row in enumerate(rows, start=1):
        if index == 1:
            continue

        enviado = row[control_index] if len(row) > control_index else ""

        if enviado.strip() == "":
            unnotified.append((index, row))

    return unnotified


# Mark row
def mark_row_notified(row_index, text="ENVIADO"):
    rows = read_sheet()

    notify_letter = get_notify_column_letter_from_rows(rows)
    range_ = f"{notify_letter}{row_index}"

    service = _get_service()

    body = {"values": [[text]]}

    service.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_,
        valueInputOption="RAW",
        body=body
    ).execute()

    return True
