import sqlite3
import logging
import inspect
import datetime
import time
import itertools

import config

def is_in_database(user_id):
    """Checks if user already in database."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    users = cursor.execute(f'''SELECT COUNT(id) 
                            FROM users 
                            WHERE user_id=?
                            ''', (user_id,)).fetchall()[0][0]
    
    cursor.close()
    database.close()

    return users


def add_user(user_id, referral):
    """Adds a new user to database."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''
        INSERT INTO users (user_id, referral)
        VALUES (?, ?)
        ''', (user_id, referral,))
        
    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Добавлен новый пользователь {user_id}.')


def add_balance(user_id, amount):
    """Adds bonuses to user."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute('''UPDATE users
                    SET balance = balance + ?
                    WHERE user_id=?
                    ''', (amount, user_id,))

    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Пользователю {user_id} добавлено {amount} бонусов.')


def get_balance(user_id):
    """Gets user's balance."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    balance = cursor.execute(f'''SELECT balance
                            FROM users 
                            WHERE user_id=?
                            ''', (user_id,)).fetchall()[0][0]
    
    cursor.close()
    database.close()

    return balance


def drop_balance(user_id):
    """Adds bonuses to user."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute('''UPDATE users
                    SET balance=?
                    WHERE user_id=?
                    ''', (0, user_id,))

    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Баланс пользователя {user_id} сброшен до 0.')


def select_sub_counter(user_id):
    """Selects style by user's id."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    sub_counter = cursor.execute(f'''SELECT counter, subscribe
                            FROM users 
                            WHERE user_id=?
                            ''', (user_id,)).fetchall()[0]
    
    cursor.close()
    database.close()

    return sub_counter


def decrease_counter(user_id):
    """Updates user's generations amount."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute('''UPDATE users
                    SET counter = counter + ?
                    WHERE user_id=?
                    ''', (-1, user_id,))

    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Пользователь {user_id} использовал одну бесплатную генерацию.')


def select_profile_info(user_id):
    """Selects style by user's id."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    profile_info = cursor.execute(f'''SELECT counter, subscribe, autorenew, valid_till, balance
                            FROM users 
                            WHERE user_id=?
                            ''', (user_id,)).fetchall()[0]
    
    cursor.close()
    database.close()

    return profile_info


def cancel_autorenew(user_id):
    """Updates user's generations amount."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute('''UPDATE users
                    SET autorenew=?, payment_method_id=?
                    WHERE user_id=?
                    ''', (False, None, user_id,))

    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Автопродление отменено для пользователя {user_id}.')


def user_subscribe(user_id, days, autorenew, payment_method_id):
    database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cursor = database.cursor()

    valid_till = datetime.datetime.utcnow() + datetime.timedelta(hours=3) + datetime.timedelta(days=days)

    cursor.execute('''UPDATE users
                    SET subscribe=?, valid_till=?, autorenew=?, payment_method_id=?
                    WHERE user_id=?
                    ''', (True, valid_till, autorenew, payment_method_id, user_id,))

    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Пользователем {user_id} приобретена подписка на {days} дней.')


def get_referral(user_id):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    referral = cursor.execute(f'''SELECT referral
                            FROM users 
                            WHERE user_id=?
                            ''', (user_id,)).fetchall()[0][0]
    
    cursor.close()
    database.close()

    return referral


def add_payment(user_id, days, referral, message_id, payment_id):
    database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cursor = database.cursor()

    payment_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)

    cursor.execute(f'''
        INSERT INTO payments (user_id, amount, days, referral, payment_id, message_id, payment_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, config.PRICE[days], days, referral, payment_id, message_id, payment_time,))
    
    db_id = cursor.lastrowid

    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Добавлен платеж для пользователя {user_id}.')

    return db_id


def select_unfinished_payments():

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    payments_info = cursor.execute(f'''SELECT user_id, days, referral, payment_id, message_id
                            FROM payments 
                            WHERE finished=?
                            ''', (False,)).fetchall()
    
    cursor.close()
    database.close()

    return payments_info

def update_payment_status(payment_id, success):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute('''UPDATE payments
                    SET finished=?, success=?
                    WHERE payment_id=?
                    ''', (True, success, payment_id,))

    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Обновлен статус платежа {payment_id}: {success}.')


def select_expired_users():
    database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cursor = database.cursor()

    time_filter = datetime.datetime.utcnow() + datetime.timedelta(hours=3)

    users_ids = cursor.execute(f'''SELECT user_id 
                            FROM users 
                            WHERE subscribe=? and valid_till<?
                            ''', (True, time_filter,)).fetchall()
    
    cursor.close()
    database.close()

    if users_ids:
        users_ids = itertools.chain.from_iterable(users_ids)
    
    return users_ids


def drop_subscription(user_id):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''
                UPDATE users
                SET subscribe=?, autorenew=?, payment_method_id=?
                WHERE user_id=?
                ''', (False, False, None, user_id,))
    
    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: У пользователя {user_id} закончилась подписка.')


def select_for_autorenew():
    database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cursor = database.cursor()

    lower_time_filter = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    upper_time_filter = lower_time_filter + datetime.timedelta(minutes=30)


    users_for_autorenew = cursor.execute(f'''SELECT user_id, referral, payment_method_id 
                            FROM users 
                            WHERE valid_till>? and valid_till<? and autorenew=?
                            ''', (lower_time_filter, upper_time_filter, True,)).fetchall()
    
    cursor.close()
    database.close()

    return users_for_autorenew


def drop_autopayment(user_id):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''
                UPDATE users
                SET autorenew=?, payment_method_id=?
                WHERE user_id=?
                ''', (False, None, user_id,))
    
    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: У пользователя {user_id} сброшен автоплатеж из-за ошибки при его формировании.')


def select_db_users():
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    users_info = cursor.execute('SELECT * FROM users').fetchall()
    
    cursor.close()
    database.close()

    return users_info


def select_db_payments():
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    payments_info = cursor.execute('SELECT * FROM payments').fetchall()
    
    cursor.close()
    database.close()

    return payments_info


def update_free_requests():
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'UPDATE users SET counter={config.FREE_REQUESTS}')
    
    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Обновлено количество бесплатных запросов.')