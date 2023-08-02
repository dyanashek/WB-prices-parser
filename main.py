import telebot
import logging
import threading
import inspect

import config
import payments
import functions
import db_functions
import keyboards
import text


logging.basicConfig(level=logging.ERROR, 
                    filename="py_log.log", 
                    filemode="w", 
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    )

bot = telebot.TeleBot(config.TELEGRAM_TOKEN)

threading.Thread(daemon=True, target=payments.payment_status_check).start()
threading.Thread(daemon=True, target=functions.check_subscription).start()
threading.Thread(daemon=True, target=payments.proceed_autopyments).start()
threading.Thread(daemon=True, target=functions.manage_free_requests).start()

@bot.message_handler(commands=['start'])
def start_message(message):
    '''Handles start command.'''

    user_id = message.from_user.id

    referral = message.text.replace('/start', '').replace(' ', '')
    if referral == '':
        referral = None
    
    if not db_functions.is_in_database(user_id):
        db_functions.add_user(user_id, referral)

        if referral and referral != str(user_id) and db_functions.is_in_database(referral):
            current_balance = db_functions.get_balance(referral)

            threading.Thread(daemon=True, 
                        target=db_functions.add_balance, 
                        args=(referral,
                              config.REFERRAL_START_BONUS,
                                ),
                        ).start()
            
            threading.Thread(daemon=True, 
                        target=functions.notify_referral, 
                        args=(referral,
                              current_balance,
                              config.REFERRAL_START_BONUS,
                                ),
                        ).start()
    
    balance = int(db_functions.get_balance(message.from_user.id))

    bot.send_message(chat_id=message.chat.id,
                         text=text.START_MESSAGE,
                         reply_markup=keyboards.new_buy_keyboard(balance),
                         parse_mode='Markdown',
                         )
    
    bot.send_message(chat_id=message.chat.id,
                         text=text.SUBSCRIBE,
                         reply_markup=keyboards.profile_keyboard(),
                         parse_mode='Markdown',
                         disable_notification=True,
                         )
    

@bot.message_handler(commands=['referral'])
def refferal_message(message):
    bot.send_message(chat_id=message.chat.id,
                     text=text.referral_link(message.from_user.id),
                     reply_markup=keyboards.qr_keyboard(),
                     disable_web_page_preview=True,
                     )


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(chat_id=message.chat.id,
                     text=text.HELP,
                     parse_mode='Markdown',
                     )


@bot.message_handler(commands=['balance'])
def referrals_balance_message(message):
    """Provides information about all referrals."""

    # check permissions
    if str(message.from_user.id) in config.MANAGER_ID:

        user = message.text.replace('/balance', '').replace(' ', '') 

        if db_functions.is_in_database(user):
            balance = int(db_functions.get_balance(user))

            bot.send_message(chat_id=message.chat.id,
                             text=text.users_balance(user, balance),
                             parse_mode='Markdown',
                             )
        else:
            bot.send_message(chat_id=message.chat.id,
                             text=text.NO_USER,
                             )

    # no permissions
    else:
        bot.send_message(chat_id=message.chat.id,
                                text=text.NO_PERMISSIONS,
                                )


@bot.message_handler(commands=['paid'])
def drop_balance(message):
    """Provides information about all referrals."""

    # check permissions
    if str(message.from_user.id) in config.MANAGER_ID:

        user = message.text.replace('/paid', '').replace(' ', '') 
        
        if db_functions.is_in_database(user):
            db_functions.drop_balance(user)

            bot.send_message(chat_id=message.chat.id,
                             text=text.balance_to_zero(user),
                             parse_mode='Markdown',
                             )
        else:
            bot.send_message(chat_id=message.chat.id,
                             text=text.NO_USER,
                             )

    # no permissions
    else:
        bot.send_message(chat_id=message.chat.id,
                                text=text.NO_PERMISSIONS,
                                )


@bot.message_handler(commands=['users'])
def all_users(message):
    if str(message.from_user.id) in config.MANAGER_ID:
        threading.Thread(daemon=True, target=functions.users_to_google, args=(message.from_user.id,)).start()
    else:
        bot.send_message(chat_id=message.chat.id,
                         text=text.NO_PERMISSIONS,
                         )


@bot.message_handler(commands=['payments'])
def all_payments(message):
    if str(message.from_user.id) in config.MANAGER_ID:
        threading.Thread(daemon=True, target=functions.payments_to_google, args=(message.from_user.id,)).start()
    else:
        bot.send_message(chat_id=message.chat.id,
                         text=text.NO_PERMISSIONS,
                         )
        

@bot.message_handler(commands=['profile'])
def profile_message(message):
    profile_info = db_functions.select_profile_info(message.from_user.id)

    bot.send_message(chat_id=message.chat.id,
                        text=text.profile_info(profile_info),
                        reply_markup=keyboards.profile_settings_keyboard(profile_info),
                        parse_mode='Markdown',
                        )


@bot.callback_query_handler(func = lambda call: True)
def callback_query(call):
    """Handles queries from inline keyboards."""

    # getting message's and user's ids
    message_id = call.message.id
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    call_data = call.data.split('_')
    query = call_data[0]

    if query == 'qr':
        try:
            bot.edit_message_reply_markup(chat_id=chat_id,
                                          message_id=message_id,
                                          reply_markup=telebot.types.InlineKeyboardMarkup(),
                                          )
        except:
            pass

        threading.Thread(daemon=True, 
                        target=functions.send_qr, 
                        args=(user_id,),
                        ).start()
    
    elif query == 'cancel':
        db_functions.cancel_autorenew(user_id)

        bot.send_message(chat_id=chat_id,
                         text=text.CANCEL_AUTORENEW,
                         parse_mode='Markdown',
                         )
        
        profile_info = db_functions.select_profile_info(user_id)

        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=text.profile_info(profile_info),
                              parse_mode='Markdown',
                              )
        
        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=keyboards.profile_settings_keyboard(profile_info),
                                      )
    
    elif query == 'subscribe':
        balance = int(call_data[1])

        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=text.SUBSCRIBE_DAYS,
                              )
        
        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=keyboards.days_keyboard(balance),
                                      )
    
    elif query == 'days':
        days = int(call_data[1])
        price = config.PRICE[days]
        balance = int(call_data[2])

        payment_url, payment_id = payments.create_payment(days)

        if payment_url and payment_id:
            referral = db_functions.get_referral(user_id)
            db_id = db_functions.add_payment(user_id, days, referral, message_id, payment_id)

            bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text=text.pay_subscribe(days, price),
                                parse_mode='Markdown',
                                )

            bot.edit_message_reply_markup(chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=keyboards.payment_keyboard(days, balance, db_id, payment_url),
                                        )
        
        else:
            bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text.NO_PAYMENT_LINK,
                                    )
            
            bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=keyboards.days_keyboard(balance),
                                            )

    
    elif query == 'balance':
        days = int(call_data[1])
        price = config.PRICE[days]

        db_functions.add_balance(user_id, price * (-1))
        db_functions.user_subscribe(user_id, days, False, None)

        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=text.bonus_payment(days, price),
                              parse_mode='Markdown',
                              )

        profile_info = db_functions.select_profile_info(user_id)

        bot.send_message(chat_id=chat_id,
                         text=text.profile_info(profile_info),
                         reply_markup=keyboards.profile_settings_keyboard(profile_info),
                         parse_mode='Markdown',
                         )

    elif query == 'back':

        destination = call_data[1]

        if destination == 'profile':
            profile_info = db_functions.select_profile_info(user_id)

            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text.profile_info(profile_info),
                                  parse_mode='Markdown',
                                  )
            
            bot.edit_message_reply_markup(chat_id=chat_id,
                                          message_id=message_id,
                                          reply_markup=keyboards.profile_settings_keyboard(profile_info),
                                          )
        
        elif destination == 'subscribe':
            # отменить ссылку на оплату
            balance = int(call_data[2])

            bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text=text.SUBSCRIBE_DAYS,
                                )
            
            bot.edit_message_reply_markup(chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=keyboards.days_keyboard(balance),
                                        )

    elif query == 'close':
        try:
            bot.edit_message_reply_markup(chat_id=chat_id,
                                          message_id=message_id,
                                          reply_markup=telebot.types.InlineKeyboardMarkup(),
                                          )
        except:
            pass
    
    elif query == 'newsubscribe':
        balance = int(call_data[1])

        bot.send_message(chat_id=chat_id,
                         text=text.SUBSCRIBE_DAYS,
                         reply_markup=keyboards.days_keyboard(balance),
                         )


@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Handles message with type text."""
    
    if message.text == '🗂 Профиль':
        profile_info = db_functions.select_profile_info(message.from_user.id)

        bot.send_message(chat_id=message.chat.id,
                         text=text.profile_info(profile_info),
                         reply_markup=keyboards.profile_settings_keyboard(profile_info),
                         parse_mode='Markdown',
                         )

    else:
        sub_counter = db_functions.select_sub_counter(message.from_user.id)

        if sub_counter[0] or sub_counter[1]:
            sended_message = bot.send_message(chat_id=message.chat.id,
                                              text=text.pending(message.text),
                                              reply_markup=keyboards.profile_keyboard(),
                                              )
            threading.Thread(daemon=True, 
                                target=functions.proceed_request, 
                                args=(message.text, message.from_user.id, message.chat.id, sub_counter[1], sended_message.id,),
                                ).start()
                
        # нет подписки, использованы бесплатные запросы
        else:
            balance = db_functions.get_balance(message.from_user.id)

            bot.send_message(chat_id=message.chat.id,
                                text=text.NO_REQUESTS,
                                reply_markup=keyboards.buy_keyboard(balance),
                                )


if __name__ == '__main__':
    # bot.polling(timeout=80)
    while True:
        try:
            bot.polling()
        except:
            pass