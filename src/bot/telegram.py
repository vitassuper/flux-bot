from typing import Callable, Dict, List
from telegram import ReplyKeyboardMarkup, Update, KeyboardButton
from telegram.ext import (
    Updater,
    CallbackContext,
    MessageHandler,
    Filters,
)
from src.app.services.deal import get_daily_pnl, get_total_pnl

from src.bot.connector import Connector
from src.core.config import settings


class Telegram:
    keyboard_keys: List[Dict[str, Callable[[], None]]] = []

    @classmethod
    def initialize(cls):
        cls.keyboard_keys = [
            {'name': 'start', 'handler': cls.start_handler},
            {'name': '^Get positions$', 'handler': cls.positions_handler},
            {'name': '^Get stats$', 'handler': cls.stats_handler}
        ]

    @staticmethod
    def start_handler(update: Update, context: CallbackContext) -> None:
        keyboard = [
            [KeyboardButton("Get positions"), KeyboardButton("Get stats")]]

        update.message.reply_text(
            "Choose a command",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        )

    @staticmethod
    def stats_handler(update: Update, context: CallbackContext) -> None:
        total_pnl = get_total_pnl()
        daily_png = get_daily_pnl()

        update.message.reply_text(
            f"Daily PNL: {daily_png}\n"
            f"Total PNL: {total_pnl}"
        )

    @staticmethod
    def positions_handler(update: Update, context: CallbackContext) -> None:
        connector = Connector()
        result = connector.get_open_positions_info()

        update.message.reply_text(result)

    def __init__(self, token):
        self.initialize()
        updater = Updater(token)

        for command in self.keyboard_keys:
            updater.dispatcher.add_handler(
                MessageHandler(Filters.regex(command['name']), command['handler']))

        updater.start_polling()
        updater.idle([])


def run():
    Telegram(settings.TELEGRAM_BOT_TOKEN)
