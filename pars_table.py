import time
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from googleapiclient import discovery
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging
import os
import datetime as dt

from parser import search_rootId,get_feedback,rating_control,size_control


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(BASE_DIR, 'logs/')
log_file = os.path.join(BASE_DIR, 'logs/parser_table.log')
console_handler = logging.StreamHandler()
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=100000,
    backupCount=3,
    encoding='utf-8'
)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s',
    handlers=(
        file_handler,
        console_handler
    )
)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials_service.json'
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE)
service = discovery.build('sheets', 'v4', credentials=credentials)
START_POSITION_FOR_PLACE = 0

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
load_dotenv('.env ')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')


def get_article(table_id):
    articles = {}
    service = build('sheets', 'v4', credentials=credentials)
    sheet_metadata = service.spreadsheets().get(spreadsheetId=table_id).execute()
    for items in sheet_metadata['sheets']:
        range_name = items['properties'].get('title')
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=table_id,
                                    range=range_name, majorDimension='ROWS').execute()
        values = result.get('values', [])
        for article in values[0]:
            if article.isdigit():
                articles[range_name]=article
    return articles


def convert_to_column_letter(column_number):
    column_letter = ''
    while column_number != 0:
        c = ((column_number - 1) % 26)
        column_letter = chr(c + 65) + column_letter
        column_number = (column_number - c) // 26
    return column_letter


def convert_to_column_letter(column_number):
    column_letter = ''
    while column_number != 0:
        c = ((column_number - 1) % 26)
        column_letter = chr(c + 65) + column_letter
        column_number = (column_number - c) // 26
    return column_letter


def update_table_rating(range_name, table_id):
    date = f'{last_monday}.{month}-{last_sunday}.{month}'
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=table_id,
                                range=range_name, majorDimension='ROWS').execute()
    results = result.get('values', [])
    row,index,count = 4,0,0
    body_data = []
    feedback = get_feedback(search_rootId(int(get_article(table_id).get(f'{name_sheet}'))), last_week,
                                   needed_valuation=None)
    sizer = size_control(feedback)
    ratinger = rating_control(feedback)
    if not results:
        logging.info('No data found.')
    else:
        for values in results[1:]:
            if date in values:
                column = values.index(date) + 1
        try:
            five = ratinger['five']
            body_data += [{'range': f'{range_name}!{convert_to_column_letter(column + 1)}{row}',
                           'values': [[f'{five}']]}]
            four = ratinger['four']
            body_data += [{'range': f'{range_name}!{convert_to_column_letter(column + 1)}{row+1}',
                           'values': [[f'{four}']]}]
            three = ratinger['three']
            body_data += [{'range': f'{range_name}!{convert_to_column_letter(column + 1)}{row+2}',
                           'values': [[f'{three}']]}]
            two = ratinger['two']
            body_data += [{'range': f'{range_name}!{convert_to_column_letter(column + 1)}{row + 3}',
                           'values': [[f'{two}']]}]
            one = ratinger['one']
            body_data += [{'range': f'{range_name}!{convert_to_column_letter(column + 1)}{row + 4}',
                           'values': [[f'{one}']]}]
            ok = sizer['ok']
            body_data += [{'range': f'{range_name}!{convert_to_column_letter(column)}{row + 11}',
                           'values': [[f'{ok}']]}]
            bigger = sizer['bigger']
            body_data += [{'range': f'{range_name}!{convert_to_column_letter(column)}{row + 12}',
                           'values': [[f'{bigger}']]}]
            smaller = sizer['smaller']
            body_data += [{'range': f'{range_name}!{convert_to_column_letter(column)}{row + 13}',
                           'values': [[f'{smaller}']]}]
        except:
            pass
        finally:
            index += 1
            row += 1
            body = {
                'valueInputOption': 'USER_ENTERED',
                'data': body_data}
    sheet.values().batchUpdate(spreadsheetId=table_id, body=body).execute()


def update_table_reviews(range_name, table_id):
    date = f'{last_monday}.{month}-{last_sunday}.{month}'
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=table_id,
                                range=range_name, majorDimension='ROWS').execute()
    results = result.get('values', [])
    row,index,count = 20,0,0
    body_data = []
    feedback = get_feedback(search_rootId(int(get_article(table_id).get(f'{name_sheet}'))), last_week,
                                   needed_valuation=None)
    if not results:
        logging.info('No data found.')
    else:

        for values in results[1:]:
            if date in values:
                column = values.index(date) + 1
            try:
                review = feedback[index]['review']
                body_data += [{'range': f'{range_name}!{convert_to_column_letter(column)}{row}',
                                     'values': [[f'{review}']]}]
                rating = feedback[index]['rating']
                body_data += [{'range': f'{range_name}!{convert_to_column_letter(column+1)}{row}',
                                         'values': [[f'{rating}']]}]
            except:
                pass
            finally:
                index += 1
                row += 1
                body = {
                    'valueInputOption': 'USER_ENTERED',
                    'data': body_data}
    sheet.values().batchUpdate(spreadsheetId=table_id, body=body).execute()


if __name__ == '__main__':
    table_id = SPREADSHEET_ID
    date_from = dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=7)
    date_to = dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=1)
    last_monday = date_from.strftime("%d")
    last_sunday = date_to.strftime("%d")
    month = date_to.strftime("%m")
    last_week = [str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=1)),
                 str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=2)),
                 str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=3)),
                 str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=4)),
                 str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=5)),
                 str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=6)),
                 str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=7))]
    for name_sheet in get_article(table_id):
        if name_sheet.endswith('-конкуренты'):
            continue
        update_table_rating(name_sheet, table_id)
        time.sleep(60)
        update_table_reviews(name_sheet, table_id)
        time.sleep(60)



