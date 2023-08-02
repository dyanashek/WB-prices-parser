from telebot import types

import config


def qr_keyboard():
    """Keyboard for qr generation."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('🖼 Сгенерировать qr-code', callback_data = 'qr'))

    return keyboard


def manager_keyboard():
    """Generates main keyboard that have option of filling form, check instagram."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('👨‍💼 Менеджер', url = f'https://t.me/{config.MANAGER_USERNAME}'))

    return keyboard

def profile_keyboard():
    """Keyboard for qr generation."""

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,)
    keyboard.add(types.KeyboardButton('🗂 Профиль'))

    return keyboard


def profile_settings_keyboard(profile_info):
    subscribe = profile_info[1]
    autorenew = profile_info[2]
    balance = profile_info[4]

    keyboard = types.InlineKeyboardMarkup()

    if not subscribe:
        keyboard.add(types.InlineKeyboardButton('💵 Приобрести подписку', callback_data = f'subscribe_{int(balance)}'))

    if autorenew:
        keyboard.add(types.InlineKeyboardButton('🔄 Отменить автопродление', callback_data = 'cancel'))

    if balance >= 1000:
        keyboard.add(types.InlineKeyboardButton('👨‍💼 Менеджер', url = f'https://t.me/{config.MANAGER_USERNAME}'))
    
    keyboard.add(types.InlineKeyboardButton('❌ Убрать клавиатуру', callback_data = 'close'))
    
    return keyboard


def days_keyboard(balance):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(f'⏳ 1 день ({config.PRICE[1]} руб.)', callback_data = f'days_1_{balance}'))
    keyboard.add(types.InlineKeyboardButton(f'🕕 7 дней ({config.PRICE[7]} руб.)', callback_data = f'days_7_{balance}'))
    keyboard.add(types.InlineKeyboardButton(f'📆 30 дней ({config.PRICE[30]} руб.)', callback_data = f'days_30_{balance}'))
    keyboard.add(types.InlineKeyboardButton('⬅️ Назад', callback_data = 'back_profile'))

    return keyboard


def payment_keyboard(days, balance, db_id, payment_url):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('💸 Оплатить', url = payment_url))

    if balance >= config.PRICE[days]:
        keyboard.add(types.InlineKeyboardButton('🏆 Оплатить бонусами', callback_data = f'balance_{days}_{db_id}'))
    
    keyboard.add(types.InlineKeyboardButton('⬅️ Назад', callback_data = f'back_subscribe_{balance}_{db_id}'))
    
    return keyboard


def buy_keyboard(balance):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('💵 Приобрести подписку', callback_data = f'subscribe_{int(balance)}'))
    return keyboard


def new_buy_keyboard(balance):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('💵 Приобрести подписку', callback_data = f'newsubscribe_{int(balance)}'))
    return keyboard