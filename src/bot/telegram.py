import asyncio
from typing import Dict, List, Tuple, Union

from telegram import ReplyKeyboardMarkup, Update, KeyboardButton
from telegram.ext import (
    Application,
    CallbackContext,
    MessageHandler,
    filters,
)

from src.app.services.deal import get_daily_pnl, get_total_pnl
from src.bot.exchange.async_exchange.async_base import BaseExchange
from src.bot.exchange.async_exchange.async_binance import Binance
from src.bot.exchange.async_exchange.async_okx import Okex
from src.bot.objects.active_deal import ActiveDeal
from src.core.config import settings


class Telegram:
    keyboard_keys: List[Dict[str, Union[str, Tuple[Update, CallbackContext]]]] = []

    @classmethod
    def initialize(cls):
        cls.keyboard_keys = [
            {'name': 'start', 'handler': cls.start_handler},
            {'name': '^Get positions$', 'handler': cls.positions_handler},
            {'name': '^Get stats$', 'handler': cls.stats_handler}
        ]

    @staticmethod
    async def start_handler(update: Update, context: CallbackContext) -> None:
        keyboard = [
            [KeyboardButton('Get positions'), KeyboardButton('Get stats')]]

        await update.message.reply_text(
            'Choose a command',
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        )

    @staticmethod
    async def stats_handler(update: Update, context: CallbackContext) -> None:
        total_pnl = await get_total_pnl()
        daily_png = await get_daily_pnl()

        await update.message.reply_text(
            f'Daily PNL: {daily_png}\n'
            f'Total PNL: {total_pnl}'
        )

    @staticmethod
    async def positions_handler(update: Update, context: CallbackContext) -> None:
        exchanges = await get_all_positions()

        text = ''

        for positions in exchanges:
            text += f'{positions}\n'

        await update.message.reply_text(text)

    def __init__(self, token):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.initialize()
        application = Application.builder().token(token).build()

        for command in self.keyboard_keys:
            application.add_handler(
                MessageHandler(filters.Regex(command['name']), command['handler']))

        application.run_polling(
            allowed_updates=Update.ALL_TYPES, stop_signals=[])


def run():
    Telegram(settings.TELEGRAM_BOT_TOKEN)


async def get_from_exchange(exchange: BaseExchange):
    text = f'{BaseExchange.get_exchange_name()}:\n\n'
    positions: List[ActiveDeal] = await exchange.get_open_positions_info()

    if not positions:
        return text + 'No positions'

    for position in positions:
        text += (
            f'{position.pair}\n'
            f"{position.side.capitalize()} {'🟥' if position.side == 'short' else '🟩'}\n"
            f'Margin: {position.margin}\n'
            f'Current price: {position.current_price}\n'
            f'Avg price: {position.avg_price}\n'
            f'Unrealized PNL: {position.unrealized_pnl}\n'
            f'liquidationPrice: {position.liquidation_price}\n'
            f'Pos size: {position.notional_size}💰\n'
            f'Duration: {position.duration}\n'
            f'Safety orders {position.safety_orders_count}\n\n'
        )

    return text


async def get_all_positions():
    exchanges = [Binance(), Okex()]
    tasks = []

    for exchange in exchanges:
        tasks.append(asyncio.create_task(get_from_exchange(exchange=exchange)))

    return await asyncio.gather(*tasks)
