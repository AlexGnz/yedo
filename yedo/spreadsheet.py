import gspread
from oauth2client.service_account import ServiceAccountCredentials


def sendNotif(messenger_id):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive',
             'https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/spreadsheets']

    creds = ServiceAccountCredentials.from_json_keyfile_name('./yedo/yedo-253509-633f05edeb30.json', scope)

    client = gspread.authorize(creds)

    sheet = client.open('Notifications - Students').sheet1
    row = [messenger_id]
    sheet.append_row(row)
    return True

