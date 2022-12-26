from datetime import datetime
from peewee import fn
from telegram import ReplyKeyboardMarkup, Update, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from bot.models.deals import Deals
from bot.connector import Connector

from bot.settings import Config

def start(update: Update, context: CallbackContext) -> None:
    get_positions_button = KeyboardButton('Get positions')
    get_stats_button = KeyboardButton('Get stats')

    keyboard = [[get_positions_button, get_stats_button]]

    update.message.reply_text('Choose a command', reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

def get_stats_handler(update: Update, context: CallbackContext) -> None:

    now = datetime.now().timestamp()
    midnight = now - (now % 86400)  # 86400 seconds in a day

    deals = Deals.select().where(Deals.date_close >= midnight)

    pnl_sum = deals.select(fn.Sum(Deals.pnl)).scalar()

    update.message.reply_text(f"PNL: {pnl_sum}")   

def get_positions_handler(update: Update, context: CallbackContext) -> None:
    connector = Connector()
    result = connector.get_open_positions()

    update.message.reply_text(result)


def run():
    config = Config()
    updater = Updater(config.telegram_token)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('^Get positions$'), get_positions_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('^Get stats$'), get_stats_handler))

    updater.start_polling()
    updater.idle([])

