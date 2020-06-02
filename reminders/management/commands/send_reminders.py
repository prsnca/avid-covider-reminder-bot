#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import os, json
from telegram import ReplyKeyboardMarkup, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from django.core.management.base import BaseCommand, CommandError
from reminders.models import Reminder
from reminders.keyboards import reminder_menu, reminder_text

from datetime import datetime
import pytz

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

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


class Command(BaseCommand):
    help = 'Send reminders at the specific hour'

    def handle(self, *args, **options):
        logger.info(_("Starting periodic job"))
        token = os.getenv('BOT_TOKEN')
        if token == None:
            logger.error(_('BOT_TOKEN is missing'))
            os.exit(1)
        updater = Updater(token, use_context=True)

        tz = pytz.timezone('Asia/Jerusalem')
        timenow = datetime.now(tz)
        hour = timenow.hour

        for reminder in Reminder.objects.filter(hour=hour).all():
            logger.info(_("Sending reminder", chat_id=reminder.chat_id))
            lang = reminder.lang
            try:
                updater.bot.send_message(chat_id=reminder.chat_id,
                                         text=reminder_text(lang),
                                         reply_markup=reminder_menu(lang))
            except BaseException as e:
                logger.error(_("Failed to send reminder", chat_id=reminder.chat_id, e=str(e)))
