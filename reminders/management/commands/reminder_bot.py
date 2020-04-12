#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import os, json
from telegram import ReplyKeyboardMarkup, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from django.core.management.base import BaseCommand, CommandError
from reminders.models import Reminder

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

inline_hours = [InlineKeyboardButton(str(x) + ":00", callback_data=x) for x in [8, 10, 18, 20, 22]]
inline_keyboard = [[hour] for hour in inline_hours]
inline_markup = InlineKeyboardMarkup(inline_keyboard)

change_hour_button = InlineKeyboardButton("שינוי שעת תזכורת יומית", callback_data='hour')
reregister_button = InlineKeyboardButton("חידוש תזכורת יומית", callback_data='hour')
cancel_button = InlineKeyboardButton("ביטול תזכורת יומית", callback_data='cancel')
reminder_button = InlineKeyboardButton("coronaisrael.org", callback_data='clicked', url="https://coronaisrael.org/?source=telegram-reminder")

inline_menu = InlineKeyboardMarkup([[change_hour_button], [cancel_button]])
reminder_menu = InlineKeyboardMarkup([[reminder_button], [change_hour_button], [cancel_button]])
cancel_menu = InlineKeyboardMarkup([[reregister_button]])


class LogMessage(object):
    def __init__(self, message, **kwargs):
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        return json.dumps({'message': self.message, **self.kwargs})

_ = LogMessage


def start(update, context):
    logger.info(_("User started"))
    return ask_for_hour(update, context)


def ask_for_hour(update, context):
    update.message.reply_text("באיזו שעה ביום תרצו שנזכיר לכם למלא את השאלון?", reply_markup=inline_markup)


def change_hour(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text("באיזו שעה ביום תרצו שנזכיר לכם למלא את השאלון?", reply_markup=inline_markup)


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
    query.edit_message_text(text="התזכורת היומית בוטלה ונמחקה מהמערכת.", reply_markup=cancel_menu)

    chat_id = query.message.chat_id
    reminder = Reminder.objects.filter(chat_id=chat_id).first()

    if reminder:
        reminder.delete()


def choose_hour(update, context):
    query = update.callback_query
    hour = query.data
    user = query.message.from_user
    chat_id = query.message.chat_id
    set_user_updates(user, chat_id, hour)
    query.answer()

    query.edit_message_text(text=
        """*בחירתך נרשמה!*

נזכיר לך בכל יום ב-*{}:00* למלא את השאלון.
תודה! """.format(hour), parse_mode=ParseMode.MARKDOWN, reply_markup=inline_menu)


def set_user_updates(user, chat_id, hour):
    logger.info(_("User updating", chat_id=chat_id))

    reminder = Reminder.objects.filter(chat_id=chat_id).first()

    if reminder is None:
        reminder = Reminder(chat_id=chat_id)

    reminder.hour = hour
    reminder.save()

    return


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


class Command(BaseCommand):
    help = 'Reminder Telegram Bot'

    def handle(self, *args, **options):
        logger.info(_("Starting bot"))
        token = os.getenv('BOT_TOKEN')
        if token == None:
            logger.error(_('BOT_TOKEN is missing'))
            os.exit(1)
        updater = Updater(token, use_context=True)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        dp.add_handler(CommandHandler('start', start))
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
        else:
            updater.start_polling()

        updater.idle()
