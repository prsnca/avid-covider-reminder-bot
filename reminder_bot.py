#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import os, json
from telegram import ReplyKeyboardMarkup, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

inline_hours = [InlineKeyboardButton(str(x) + ":00", callback_data=x) for x in list(range(0, 24))]
inline_hours = inline_hours[8:] + inline_hours[:8]
inline_keyboard = [inline_hours[x:x+4] for x in range(0, 24, 4)]
inline_markup = InlineKeyboardMarkup(inline_keyboard)

inline_menu = InlineKeyboardMarkup([[InlineKeyboardButton("שנה שעה", callback_data='hour')], [InlineKeyboardButton("בטל תזכורת", callback_data='cancel')]])

reminder_menu = InlineKeyboardMarkup([[InlineKeyboardButton("coronaisrael.org", callback_data='clicked', url="https://coronaisrael.org/?source=telegram-reminder")]]);


class LogMessage(object):
    def __init__(self, message, **kwargs):
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        return json.dumps({'message': self.message, **self.kwargs})

_ = LogMessage


def start(update, context):
    update.message.reply_text("שלום וברוכים הבאים לבוט!")
    return ask_for_hour(update, context)


def reminder(update, context):
    update.message.reply_text("מלא את הטופס!", reply_markup=reminder_menu)


def ask_for_hour(update, context):
    update.message.reply_text("מתי תרצה לקבל את ההתראה היומית שלך?", reply_markup=inline_markup)


def change_hour(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text("מתי תרצה לקבל את ההתראה היומית שלך?", reply_markup=inline_markup)


def menu_choice(update, context):
    query = update.callback_query
    command = query.data
    if command == 'cancel':
        return cancel(update, context)
    elif command == 'hour':
        return change_hour(update, context)
    elif command == 'clicked':
        # TODO - Updated clicks/last clicked
        query.answer()
        return
    return choose_hour(update, context)


def cancel(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="התזכורת היומית בוטלה! לחץ /start על מנת להירשם מחדש.")

    # TODO - Delete from database


def choose_hour(update, context):
    query = update.callback_query
    hour = query.data
    user = query.message.from_user
    chat_id = query.message.chat_id
    set_user_updates(user, chat_id, hour)
    query.answer()

    query.edit_message_text(text=
        "מעולה!\n"
        "נשלח לך לכאן כל יום בשעה *{}:00* תזכורת על מנת למלא את הטופס!".format(hour), parse_mode=ParseMode.MARKDOWN, reply_markup=inline_menu)
    # TODO add inline keyboard for - 1. hour change 2. unsubscribe


def set_user_updates(user, chat_id, hour):
    logger.info(_("User updating", user_name=user.username, chat_id=chat_id))
    user_name = user.username
    # TODO - save to database

    return


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    logger.info(_("Starting bot"))
    token = os.getenv('BOT_TOKEN')
    if token == None:
        logger.error(_('BOT_TOKEN is missing'))
        os.exit(1)
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('reminder', reminder))
    dp.add_handler(CallbackQueryHandler(menu_choice))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    heroku_url = os.getenv('HEROKU_URL')
    if heroku_url:
        port = int(os.getenv('PORT', '8443'))
        updater.start_webhook(listen="0.0.0.0",
                          port=port,
                          url_path=token)
        updater.bot.set_webhook(heroku_url + token)
        updater.idle()
    else:
        updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()