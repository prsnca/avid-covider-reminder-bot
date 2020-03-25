#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

import logging

import os
from telegram import ReplyKeyboardMarkup, ParseMode
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

HOUR, TYPING_REPLY, TYPING_CHOICE = range(3)

hours = [str(x) + ":00" for x in list(range(0, 24))]
hours = hours[8:] + hours[:8]
reply_keyboard = [hours[x:x+4] for x in range(0, 24, 4)]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def start(update, context):
    update.message.reply_text(
        "שלום!\n"
        "מתי תרצה לקבל את ההתראה היומית שלך?",
        reply_markup=markup)

    return HOUR


def hour(update, context):
    hour = update.message.text
    # user = update.message.from_user
    # chat_id = update.message.chat_id
    # set_user_updates(user, chat_id, hour)
    update.message.reply_text(
        "מעולה!\n"
        "נשלח לך לכאן כל יום בשעה *{}* התראה על מנת למלא את הטופס!".format(hour), parse_mode=ParseMode.MARKDOWN)
    # TODO add inline keyboard for - 1. hour change 2. unsubscribe

    return ConversationHandler.END


def done(update, content):
    return ConversationHandler.END


def set_user_updates(user, chat_id, hour):
    hour_value = int(hour.split(':')[0])
    user_name = user.username
    # TODO - save to database

    return


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    token = os.getenv('BOT_TOKEN')
    if token == None:
        logger.error(_('BOT_TOKEN is missing'))
        os.exit(1)
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            HOUR: [MessageHandler(Filters.text(hours),
                                      hour),
                       ],
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()