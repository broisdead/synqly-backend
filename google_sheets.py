from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1lYDvQkHjT6KYLas9yp1Da08wIz3Oef_OLFsYKf7twh0'
SHEET_NAME = 'Sheet1'  # Update this if your tab has a different name

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

def append_to_sheet(data):
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    values = [[
        data.get('name'),
        data.get('email'),
        data.get('message'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ]]

    body = {'values': values}

    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A:D",
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()

    return result

