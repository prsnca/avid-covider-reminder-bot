from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from django.utils.translation import gettext as _, activate

URL = "https://coronaisrael.org/?source=telegram-reminder"
HOURS = [8, 10, 18, 20, 22]
DEFAULT_LANGUAGE = 'he'


def get_language(lang):
    return DEFAULT_LANGUAGE if lang is None else lang


def set_language(lang):
    lang = get_language(lang)
    activate(lang)


def get_callback_data(command, lang):
    return '{},{}'.format(command, lang)


def parse_callback_data(data):
    data = data.split(',')
    command = data[0]
    lang = data[1] if len(data) == 2 else None
    return command, lang


def hour_menu(lang=None):
    lang = get_language(lang)
    inline_hours = [InlineKeyboardButton(str(x) + ":00", callback_data=get_callback_data(x, lang)) for x in HOURS]
    inline_keyboard = [[hour] for hour in inline_hours]
    return InlineKeyboardMarkup(inline_keyboard)


def inline_menu(lang=None):
    set_language(lang)
    change_hour_button = InlineKeyboardButton(_('change_hour'), callback_data=get_callback_data('hour', lang))
    cancel_button = InlineKeyboardButton(_('unsubscribe'), callback_data=get_callback_data('cancel', lang))
    return InlineKeyboardMarkup([[change_hour_button], [cancel_button]])


def reminder_menu(lang=None):
    set_language(lang)
    reminder_button = InlineKeyboardButton("coronaisrael.org", callback_data=get_callback_data('clicked', lang), url=URL)
    change_hour_button = InlineKeyboardButton(_('change_hour'), callback_data=get_callback_data('hour', lang))
    cancel_button = InlineKeyboardButton(_('unsubscribe'), callback_data=get_callback_data('cancel', lang))
    return InlineKeyboardMarkup([[reminder_button], [change_hour_button], [cancel_button]])


def cancel_menu(lang=None):
    set_language(lang)
    reregister_button = InlineKeyboardButton(_('subscribe'), callback_data=get_callback_data('hour', lang))
    return InlineKeyboardMarkup([[reregister_button]])


def reminder_text(lang=None):
    set_language(lang)
    return _('reminder_text') + " 💪"


def reminder_set(lang=None):
    set_language(lang)
    return _('reminder_set')


def ask_for_hour_text(lang=None):
    set_language(lang)
    return _('ask_for_hour')


def cancel_text(lang=None):
    set_language(lang)
    return _('reminder_cancelled')
