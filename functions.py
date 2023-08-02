import telebot
import requests
import datetime
import os
import logging
import inspect
import qrcode
import threading
import time

import keyboards
import db_functions
import utils
import config
import text


bot = telebot.TeleBot(config.TELEGRAM_TOKEN)


def get_search_prices(keyword):
    """Finds adverts prices."""

    keyword = keyword.lower()
    url = f'{config.SEARCH_ADVERTS_URL}{keyword}'

    try:
        response = requests.get(url, headers=config.HEADERS)
    except Exception as ex:
        response = None
    
    if response:
        if response.status_code == 200:
            adverts = response.json().get('adverts')
            
            if adverts:
                current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime("%d.%m.%Y %H:%M")
                reply = text.search_reply(current_time, keyword)

                for num, advert in enumerate(adverts):
                    position = f'{num + 1}.'.ljust(7, ' ')

                    price = utils.numbers_format(advert.get('cpm'))
                    price = f'{price} руб.'.ljust(12 , ' ')

                    vendor = advert.get('id')

                    url = f'https://www.wildberries.ru/catalog/{vendor}/detail.aspx'

                    if num < 100:
                        reply += f'{position} *{price}* [{vendor}]({url})\n'
                
                return reply
            
            else:
                return text.search_error(keyword)

        else:
            logging.error(f'{inspect.currentframe().f_code.co_name}: Ошибка соединения {response.status_code}.')
            return  False
    else:
        logging.error(f'{inspect.currentframe().f_code.co_name}: Ошибка соединения: {ex}.')
        return False
    

def get_product_prices(vendor):
    """Finds adverts prices in product card."""

    url = f'{config.PRODUCT_ADVERTS_URL}{vendor}'

    try:
        response = requests.get(url, headers=config.HEADERS)
    except Exception as ex:
        response = None

    if response:
        if response.status_code == 200:
            
            adverts = response.json()

            if adverts:
                current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime("%d.%m.%Y %H:%M")
                reply = text.card_reply(current_time, vendor)

                for advert in adverts:
                    position = str(advert.get('position'))
                    position = f'{position}.'.ljust(7, ' ')

                    price = utils.numbers_format(advert.get('cpm'))
                    price = f'{price} руб.'.ljust(12, ' ')

                    vendor = advert.get('nmId')

                    url = f'https://www.wildberries.ru/catalog/{vendor}/detail.aspx'

                    reply += f'{position} *{price}* [{vendor}]({url})\n'

                return reply
            
            else:
                return text.card_error(vendor)
    
        else:
            logging.error(f'{inspect.currentframe().f_code.co_name}: Ошибка соединения: {response.status_code}.')
            return False
        
    else:
        logging.error(f'{inspect.currentframe().f_code.co_name}: Ошибка соединения: {ex}.')
        return  False


def generate_qr(user_id):
    """Saves qr-code that contains user's referral link."""
    referral_url = f'https://t.me/{config.BOT_NAME}?start={user_id}'

    qr = qrcode.QRCode(version=1, 
                       error_correction=qrcode.constants.ERROR_CORRECT_L, 
                       box_size=10, 
                       border=2,
                       )

    qr.add_data(referral_url)

    qr_image = qr.make_image()

    try:
        qr_image.save(f'{user_id}.png')
    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: При сохранении qr-кода пользователя {user_id} произошла ошибка: {ex}.')


def send_qr(user_id):
    """Sends referral qr code to user and deletes it."""

    generate_qr(user_id)

    try:
        with open(f'{user_id}.png', "rb") as file:
            qr_bytes = file.read()

        bot.send_photo(user_id, photo=qr_bytes)

        os.remove(f'{user_id}.png')

    except Exception as ex:

        bot.send_message(chat_id=user_id,
                         text=text.QR_ERROR,
                         )
        
        try:
            os.remove(f'{user_id}.png')
        except:
            logging.error(f'{inspect.currentframe().f_code.co_name}: При удалении qr-кода пользователя {user_id} произошла ошибка: {ex}.')
            
        logging.error(f'{inspect.currentframe().f_code.co_name}: При генерации и отправке qr-кода пользователю {user_id} произошла ошибка: {ex}.')


def notify_referral(user_id, current_balance, amount):
    """Notifies referral when he gets reward."""

    if current_balance + amount <= 1000:
        keyboard = telebot.types.InlineKeyboardMarkup()
    else:
        keyboard = keyboards.manager_keyboard()

    reply_text = text.balance_top_up(current_balance, amount)

    try:
        bot.send_message(chat_id=user_id,
                         text=reply_text,
                         parse_mode='Markdown',
                         reply_markup=keyboard,
                         )
    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: Не удалось отправить сообщение об увеличении баланса пользователю {user_id}: {ex}.')


def proceed_request(request, user_id, chat_id, subscribe, message_id,):

    if utils.vendor_validator(request):
        reply = get_product_prices(request)

    else:
        reply = get_search_prices(request)

    if reply:
        if not subscribe and 'К сожалению,' not in reply:
            threading.Thread(daemon=True, 
                        target=db_functions.decrease_counter, 
                        args=(user_id,),
                        ).start()
        try:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass

        try:
            bot.send_message(chat_id=chat_id,
                            text=reply,
                            reply_markup=keyboards.profile_keyboard(),
                            parse_mode='Markdown',
                            )
        except:
            reply = reply.replace('*', '')

            bot.send_message(chat_id=chat_id,
                            text=reply,
                            reply_markup=keyboards.profile_keyboard(),
                            )
            
    # ошибка запроса
    else:
        try:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass

        bot.send_message(chat_id=chat_id,
                            text=text.REQUEST_ERROR,
                            reply_markup=keyboards.profile_keyboard(),
                            )
        

def delete_keyboard(chat_id, message_id):
    try:
        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=telebot.types.InlineKeyboardMarkup(),
                                      )
    except:
        pass


def notify_success_payment(user_id, days):
    profile_info = db_functions.select_profile_info(user_id)

    try:
        bot.send_message(chat_id=user_id,
                         text=text.paid_profile_info(profile_info, days),
                         reply_markup=keyboards.profile_settings_keyboard(profile_info),
                         parse_mode='Markdown',
                         )
    except:
        pass


def notify_expired(user_id):
    balance = int(db_functions.get_balance(user_id))

    try:
        bot.send_message(chat_id=user_id,
                         text=text.EXPIRED,
                         reply_markup=keyboards.buy_keyboard(balance),
                         parse_mode='Markdown',
                         )
    except:
        pass


def check_subscription():
    while True:
        users_ids = db_functions.select_expired_users()

        for user_id in users_ids:
            db_functions.drop_subscription(user_id)
            notify_expired(user_id)


def notify_cancel_autorenew(user_id):
    try:
        bot.send_message(chat_id=user_id,
                         text=text.AUTORENEW_ERROR,
                         reply_markup=keyboards.profile_keyboard(),
                         parse_mode='Markdown',
                         )
    except:
        pass


def users_to_google(user_id):
    users_info = db_functions.select_db_users()
    work_sheet = config.TABLE.worksheet(config.USERS_LIST_NAME)
    work_sheet.update(f'A2:J{len(users_info) + 1}', users_info)

    try:
        bot.send_message(chat_id=user_id,
                         text=text.DATA_TRANSFERRED,
                         )
    except:
        pass


def payments_to_google(user_id):
    payments_info = db_functions.select_db_payments()
    work_sheet = config.TABLE.worksheet(config.PAYMENTS_LIST_NAME)
    work_sheet.update(f'A2:J{len(payments_info) + 1}', payments_info)

    try:
        bot.send_message(chat_id=user_id,
                         text=text.DATA_TRANSFERRED,
                         )
    except:
        pass


def manage_free_requests():
    while True:
        if (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime("%H:%M") == '11:59':
            db_functions.update_free_requests()
            time.sleep(86100)