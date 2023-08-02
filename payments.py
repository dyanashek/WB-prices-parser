import uuid
import logging
import inspect
import threading
import time

from yookassa import Configuration, Payment

import config
import db_functions
import functions


Configuration.account_id = config.ACCOUNT_ID
Configuration.secret_key = config.SECRET_KEY


def create_payment(days):
    if days == 1:
        description = '1 день'
    else:
        description = f'{days} дней'

    save_payment = False
    if days == 30:
        save_payment = True

    payment = Payment.create({
        "amount": {
            "value": config.PRICE[days],
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url" : f"https://t.me/{config.BOT_NAME}"
        },
        "capture": True,
        "save_payment_method": save_payment,
        "description": f"Оплата подписки, {description}.",
        "receipt": {
        "customer": {"email": 'test@mail.ru'},
        "items":
            [{
              "description": f"Подписка WildBoost, {description}.",
              "quantity": "1",
              "amount": {
                "value": config.PRICE[days],
                "currency": "RUB"
              },
              "vat_code": "1"
            }]
        },
    }, uuid.uuid4())

    try:
        payment_url = payment.confirmation.confirmation_url
        payment_id = payment.id
    except Exception as ex:
        payment_url = False
        payment_id = False

        logging.error(f'{inspect.currentframe().f_code.co_name}: Не удалось сгенерировать ссылку для платежа. {ex}')
    
    return payment_url, payment_id


def create_autopayment(payment_method_id):

    payment = Payment.create({
        "amount": {
            "value": config.PRICE[30],
            "currency": "RUB"
        },
        "capture": True,
        "payment_method_id": payment_method_id,
        "description": f"Оплата подписки, 30 дней.",
        "receipt": {
        "customer": {"email": 'test@mail.ru'},
        "items":
            [{
              "description": f"Подписка WildBoost, 30 дней.",
              "quantity": "1",
              "amount": {
                "value": config.PRICE[30],
                "currency": "RUB"
              },
              "vat_code": "1"
            }]
        },
    }, uuid.uuid4())

    try:
        payment_id = payment.id
    except Exception as ex:
        payment_id = False

        logging.error(f'{inspect.currentframe().f_code.co_name}: Не удалось сгенерировать автоплатеж. {ex}')
    
    return payment_id


def payment_status_check():
    while True:
        payments_info = db_functions.select_unfinished_payments()

        for payment_info in payments_info:
            user_id = payment_info[0]
            days = payment_info[1]
            referral = payment_info[2]
            payment_id = payment_info[3]
            message_id = payment_info[4]

            try:
                payment_obj = Payment.find_one(payment_id)
                payment_status = payment_obj.status
            except Exception as ex:
                payment_status = False
                logging.error(f'{inspect.currentframe().f_code.co_name}: Не удалось получить данные о платеже. {ex}')

            if payment_status == "succeeded" or payment_status == "canceled":
                if payment_status == "succeeded":
                    success = True

                    autorenew = False
                    payment_method_id = None

                    if referral:
                        current_balance = db_functions.get_balance(referral)

                        threading.Thread(daemon=True, 
                            target=db_functions.add_balance, 
                            args=(referral,
                                config.PRICE[days] * config.BONUS_PERCENT,
                                    ),
                            ).start()

                        threading.Thread(daemon=True, 
                            target=functions.notify_referral, 
                            args=(referral,
                                current_balance,
                                config.PRICE[days] * config.BONUS_PERCENT,
                                    ),
                            ).start()

                    if days == 30:
                        try:
                            if payment_obj.payment_method.saved:
                                autorenew = True
                                payment_method_id = payment_obj.payment_method.id
                        except:
                            pass
                    
                    db_functions.user_subscribe(user_id, days, autorenew, payment_method_id)

                    threading.Thread(daemon=True, 
                            target=functions.notify_success_payment, 
                            args=(user_id,
                                  days,
                                  ),
                            ).start()

                    logging.info(f'{inspect.currentframe().f_code.co_name}: Платеж {payment_id} прошел успешно.')

                else: 
                    success = False
                
                    logging.info(f'{inspect.currentframe().f_code.co_name}: Платеж {payment_id} отменен.')

                functions.delete_keyboard(user_id, message_id)
                db_functions.update_payment_status(payment_id, success)


def proceed_autopyments():
    while True:
        autorenew_users = db_functions.select_for_autorenew()

        for autorenew_user in autorenew_users:
            user_id = autorenew_user[0]
            referral = autorenew_user[1]
            payment_method_id = autorenew_user[2]

            payment_id = create_autopayment(payment_method_id)

            if payment_id:
                db_functions.add_payment(user_id, 30, referral, None, payment_id)
            else:
                db_functions.drop_autopayment(user_id)
                functions.notify_cancel_autorenew(user_id)
        
        time.sleep(600)