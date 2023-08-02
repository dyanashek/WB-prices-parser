import os
import gspread
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BOT_ID = os.getenv('BOT_ID')
MANAGER_ID = os.getenv('MANAGER_ID')
MANAGER_USERNAME = os.getenv('MANAGER_USERNAME')

WB_TOKEN = os.getenv('WB_TOKEN')

# data for Ukassa
ACCOUNT_ID = os.getenv('ACCOUNT_ID')
SECRET_KEY = os.getenv('SECRET_KEY')


SPREAD_NAME = os.getenv('SPREAD_NAME')
USERS_LIST_NAME = os.getenv('USERS_LIST_NAME')
PAYMENTS_LIST_NAME = os.getenv('PAYMENTS_LIST_NAME')

SERVICE_ACC = gspread.service_account(filename='service_account.json')
TABLE = SERVICE_ACC.open(SPREAD_NAME)


BOT_NAME = 'WildBoost_bot'


HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
SEARCH_ADVERTS_URL = 'https://catalog-ads.wildberries.ru/api/v5/search?keyword='
PRODUCT_ADVERTS_URL = f'https://carousel-ads.wildberries.ru/api/v4/carousel?nm='

REFERRAL_START_BONUS = 20

BONUS_PERCENT = 0.2

FREE_REQUESTS = 5

PRICE = {
    1 : 20,
    7 : 50,
    30 : 100,
}