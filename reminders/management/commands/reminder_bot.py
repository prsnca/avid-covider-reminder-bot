#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import os, json
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from reminders.models import Reminder
from reminders.keyboards import *

SUPPORTED_LANGUAGES = list(dict(settings.LANGUAGES).keys())

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)



class LogMessage(object):
    def __init__(self, message, **kwargs):
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        return json.dumps({'message': self.message, **self.kwargs})

_ = LogMessage

def get_language(context):
    lang = None
    if context.args:
        lang_arg = context.args[0]
        lang = lang_arg if is_language_available(lang_arg) else 'he'
    return lang


def is_language_available(lang):
    return lang in SUPPORTED_LANGUAGES


def start(update, context):
    logger.info(_("User started"))
    lang = get_language(context)
    update.message.reply_text(welcome_text(lang))
    return ask_for_hour(update, context)


def ask_for_hour(update, context):
    lang = get_language(context)
    update.message.reply_text(ask_for_hour_text(lang), reply_markup=hour_menu(lang))


def change_hour(update, context):
    query = update.callback_query
    _, lang = parse_callback_data(query.data)
    query.answer()
    query.edit_message_text(ask_for_hour_text(lang), reply_markup=hour_menu(lang))


def menu_choice(update, context):
    query = update.callback_query
    command, lang = parse_callback_data(query.data)
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
    _, lang = parse_callback_data(query.data)
    query.answer()
    query.edit_message_text(text=cancel_text(lang), reply_markup=cancel_menu(lang))

    chat_id = query.message.chat_id
    reminder = Reminder.objects.filter(chat_id=chat_id).first()

    if reminder:
        reminder.delete()


def choose_hour(update, context):
    query = update.callback_query
    hour, lang = parse_callback_data(query.data)
    user = query.message.from_user
    chat_id = query.message.chat_id
    set_user_updates(user, chat_id, hour, lang)
    query.answer()

    query.edit_message_text(text=reminder_set(lang).format(str(hour) + ':00'), parse_mode=ParseMode.MARKDOWN, reply_markup=inline_menu(lang))


def set_user_updates(user, chat_id, hour, lang):
    logger.info(_("User updating", chat_id=chat_id))

    reminder = Reminder.objects.filter(chat_id=chat_id).first()

    if reminder is None:
        reminder = Reminder(chat_id=chat_id)
        if lang is not None:
            reminder.lang = lang

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
