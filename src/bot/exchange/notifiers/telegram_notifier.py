import sys

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

from src.bot.exchange.notifiers.base_notifier import BaseNotifier
from src.core.config import settings


class TelegramNotifier(BaseNotifier):
    def __init__(self):
        self.bot = Bot(settings.TELEGRAM_BOT_TOKEN)

        super().__init__()

    async def send_message(self):
        try:
            text = f'{self.get_separator().join(self.stack)}'

            await self.bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID, text=text, parse_mode=ParseMode.HTML)
            await self.bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID2, text=text, parse_mode=ParseMode.HTML)
        except TelegramError as error:
            print(error.message, file=sys.stderr)
