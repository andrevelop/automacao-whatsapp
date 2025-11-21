#Aqui é onde conecta no Google Sheets para ler e escrever.
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from .config import settings

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_sheets_service():
    creds = Credentials.from_service_account_file(settings.GOOGLE_CRED_FILE, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets()

def append_row(values: list, sheet_range="Sheet1!A:Z"):
    sheet = get_sheets_service()
    body = {"values": [values]}
    res = sheet.values().append(
        spreadsheetId=settings.SPREADSHEET_ID,
        range=sheet_range,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()
    return res
