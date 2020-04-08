#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import os, json
from telegram import ReplyKeyboardMarkup, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from django.core.management.base import BaseCommand, CommandError
from reminders.models import Reminder

from datetime import datetime
import pytz

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

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

        for reminder in Reminder.objects.filter(hour=hour, active=True).all():
            logger.info(_("Sending reminder", chat_id=reminder.chat_id))
            updater.bot.send_message(chat_id=reminder.chat_id,
                                     text="הגיע הזמן לדווח שוב כיצד אתם מרגישים! רק ביחד ננצח את הקורונה %F0%9F%92%AA!",
                                     reply_markup=reminder_menu)
