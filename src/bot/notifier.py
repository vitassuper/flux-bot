import sys
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
from src.core.config import settings


class Notifier:
    def __init__(self, exchange_name='Connector'):
        self.bot = Bot(settings.TELEGRAM_BOT_TOKEN)
        self.exchange_name = exchange_name

    async def send_warning_notification(self, text):
        await self.send_message(f'🚨{text}')

    async def send_notification(self, text, chatId=None):
        await self.send_message(text, chatId)

    async def send_message(self, text, chatId=None):
        try:
            text = f'{self.exchange_name}:\n{text}'

            if chatId:
                await self.bot.send_message(chatId, text)
            else:
                await self.bot.send_message(
                    chat_id=settings.TELEGRAM_CHAT_ID, text=text, parse_mode=ParseMode.HTML)
                await self.bot.send_message(
                    chat_id=settings.TELEGRAM_CHAT_ID2, text=text,  parse_mode=ParseMode.HTML)
        except TelegramError as error:
            print(error.message, file=sys.stderr)
