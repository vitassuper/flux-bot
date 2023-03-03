from typing import Callable, Dict, List
from telegram import ReplyKeyboardMarkup, Update, KeyboardButton
from telegram.ext import (
    Updater,
    CallbackContext,
    MessageHandler,
    Filters,
)
from src.app.services.deal import get_daily_pnl, get_total_pnl

from src.bot.exchange.binance import Binance
from src.bot.exchange.okx import Okex
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
        exchanges = [Binance(), Okex()]

        text = ''

        for exchange in exchanges:
            text += f"{exchange.get_exchange_name()}:\n\n"

            positions = exchange.get_open_positions_info()

            for position in positions:
                text += (
                    f"{position.ticker}\n"
                    f"Margin: {position.margin}\n"
                    f"Current price: {position.current_price}\n"
                    f"Avg price: {position.avg_price}\n"
                    f"Unrealized PNL: {position.unrealized_pnl}\n"
                    f"liquidationPrice: {position.liquidation_price}\n"
                    f"Pos size: {position.notional_size}💰\n"
                    f"Duration: {position.duration}\n"
                    f"Safety orders {position.safety_orders_count}\n\n"
                )

            text += '\n'

        update.message.reply_text(text)

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
