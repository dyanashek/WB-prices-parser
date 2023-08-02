import config
import datetime


START_MESSAGE = f'''
                \nПривет!\
                \n\
                \nВбей *поисковый запрос*, чтобы узнать реальные ставки в поиске (н/р: рубашка).\
                \nВбей *артикул*, чтобы узнать реальные ставки в карточке товара (н/р: 64384324).\
                \n\
                \nЕжедневно доступно *{config.FREE_REQUESTS} бесплатных запросов* 🆓. Лимит обновляется в *12:00 по МСК*.\
                \nДля снятия ограничения - *приобретите подписку*:\
                \n\
                \n- ⏳ 1 день (*{config.PRICE[1]} руб.*)\
                \n- 🕕 7 дней (*{config.PRICE[7]} руб.*)\
                \n- 📆 30 дней (*{config.PRICE[30]} руб.*)\
                '''

SUBSCRIBE = f'''
            \n🏆 В боте доступна реферальная программа. Воспользуйтесь командой */referral* для получения своей реферальной ссылки.\
            \n\
            \n💵 Вы будете получать *{config.REFERRAL_START_BONUS} бонусов* за каждого пользователя, перешедшего по вашей ссылке, а также *{int(config.BONUS_PERCENT * 100)}%* от оплаченных ими подписок.\
            \n\
            \n💰 Бонусы можно использовать для оплаты подписки (*1 бонус = 1 рубль*) или конвертации их в рубли (*2 бонуса = 1 рубль*, доступно при балансе от 1000 бонусов).\
            \n\
            \n📌 Воспользуйтесь командой */help*, если появятся какие-либо вопросы.\
            '''

QR_ERROR = 'При генерации qr-кода произошла ошибка, попробуйте позже.'

NO_PERMISSIONS = 'Недостаточно прав для выполнения команды.'

NO_USER = 'Нет такого пользователя.'

REQUEST_ERROR = 'Произошла ошибка, повторите попытку позже.'

CANCEL_AUTORENEW = 'Автопродление успешно отменено.'

SUBSCRIBE_DAYS = 'Выберите подписку:'

NO_REQUESTS = 'Исчерпан лимит бесплатных запросов на сегодня, для снятия ограничений приобретите подписку.'

NO_PAYMENT_LINK = 'Не удалось сгенерировать ссылку для совершения платежа. Попробуйте еще раз:'

EXPIRED = 'Истек срок действия подписки.'

AUTORENEW_ERROR = 'Автопродление отменено из-за неизвестной ошибки, подписка скоро закончится.'

DATA_TRANSFERRED = 'Данные успешно перенесены.'

def pending(request):
    return f'Ваш запрос ({request.lower()}) обрабатывается...'

HELP = '''
        \n*Команды:*\
        \n- */referral* - получить реферальную ссылку для приглашения пользователей\
        \n- */profile* - открыть данные о профиле\
        \n- */help* - помощь\
        \n\
        \nПри возникновении вопросов обращайтесь по адресу *support@wildboost.ru*.\
        '''

def referral_link(user_id):
    return f'Ваша реферальная ссылка: https://t.me/{config.BOT_NAME}?start={user_id}'


def balance_top_up(current_balance, amount):

    if current_balance + amount <= 1000:
        text = f'''
                \nВаш баланс пополнен на *{int(amount)} бонусов* - по реферальной программе.\
                \n\
                \nТекущий баланс: *{int(current_balance + amount)}*.\
                '''
    else:
        text = f'''
                \nВаш баланс пополнен на *{int(amount)} бонусов*  - по реферальной программе.\
                \n\
                \nТекущий баланс: *{int(current_balance + amount)}*.\
                \nДля вывода денежных средств свяжитесь с менеджером 👇\
                '''
    
    return text


def users_balance(user_id, balance):
    return f'Баланс пользователя *{user_id}*: {balance}'


def balance_to_zero(user_id):
    return f'Баланс пользователя *{user_id}* сброшен до 0.'


def profile_info(profile_info):
    counter = profile_info[0]
    subscribe = profile_info[1]
    autorenew = profile_info[2]
    valid_till = profile_info[3]
    balance = profile_info[4]

    reply_text = ''

    if subscribe:
        if autorenew:
            autorenew = 'активировано'
        else:
            autorenew = 'не активировано'

        valid_till = datetime.datetime.strptime(valid_till, '%Y-%m-%d %H:%M:%S.%f').strftime("%d.%m.%Y %H:%M")

        reply_text += f'*Подписка:* активирована (действительна до *{valid_till}* по МСК)\n*Автопродление:* {autorenew}\n'
    else:
        reply_text += f'*Подписка:* не активирована\n*Доступно запросов:* {counter}\n'
    
    if balance < 1000:
        reply_text += f'*Баланс:* {int(balance)} бонусов'
    else:
        reply_text += f'*Баланс:* {int(balance)} бонусов (можете связаться с менеджером для конвертации бонусов в рубли)'

    return reply_text


def pay_subscribe(days, price):
    if days == 1:
        text = f'Оплата подписки на *1 день* (стоимость {price} руб.):'
    elif days == 7:
        text = f'Оплата подписки на *{days} дней*  (стоимость {price} руб.):'
    else:
        text = f'Оплата подписки на *{days} дней*  (стоимость {price} руб.):\n\nПри приобретении данной подписки *автопродление* будет подключено автоматически, его можно будет *отменить в любой момент*, нажав кнопку "Профиль".'

    return text


def bonus_payment(days, price):
    if days == 1:
        text =  f'Оплачена подписка на *1 день* (потрачено *{price} бонусов*).'
    else:
        text =  f'Оплачена подписка на *{days} дней* (потрачено *{price} бонусов*).'
    
    return text

def search_reply(current_time, keyword):
    return f'{current_time}\n\nСтавки в поиске: *{keyword}*\n\n'
    
def search_error(keyword):
    return f'К сожалению, по запросу *{keyword}* ничего не нашлось, возможно фраза написана с ошибками.\nПопробуйте еще раз.'

def card_reply(current_time, vendor):
    return f'{current_time}\n\nСтавки в карточке: *{vendor}*\n\n'

def card_error(vendor):
    return f'К сожалению, по артикулу *{vendor}* ничего не нашлось, возможно он написан с ошибками.\nПопробуйте еще раз.'

def paid_profile_info(profile_info, days):
    counter = profile_info[0]
    subscribe = profile_info[1]
    autorenew = profile_info[2]
    valid_till = profile_info[3]
    balance = profile_info[4]

    if days == 1:
        reply_text = 'Подписка на *1 день* успешно оплачена.\n\n'
    else:
        reply_text = f'Подписка на *{days} дней* успешно оплачена.\n\n'

    if subscribe:
        if autorenew:
            autorenew = 'активировано'
        else:
            autorenew = 'не активировано'

        valid_till = datetime.datetime.strptime(valid_till, '%Y-%m-%d %H:%M:%S.%f').strftime("%d.%m.%Y %H:%M")

        reply_text += f'*Подписка:* активирована (действительна до *{valid_till}* по МСК)\n*Автопродление:* {autorenew}\n'
    else:
        reply_text += f'*Подписка:* не активирована\n*Доступно запросов:* {counter}\n'
    
    if balance < 1000:
        reply_text += f'*Баланс:* {int(balance)} бонусов'
    else:
        reply_text += f'*Баланс:* {int(balance)} бонусов (можете связаться с менеджером для конвертации бонусов в рубли)'

    return reply_text