import sys
from telegram import Bot, TelegramError

from bot.settings import Config


class Notificator:
    def __init__(self):
        self.config = Config()
        self.bot = Bot(self.config.telegram_token)

    def send_warning_notification(self, text):
        self.send_message(f"🚨{text}")

    def send_notification(self, text, chatId=None):
        self.send_message(text, chatId)

    def send_message(self, text, chatId=None):
        try:
            text = f"{self.config.exchange_name}:\n{text}"

            if (chatId):
                self.bot.send_message(chatId, text)
            else:
                self.bot.send_message(self.config.telegram_chat_id, text)
                self.bot.send_message(self.config.telegram_chat_id2, text)
        except TelegramError as error:
            print(error.message, file=sys.stderr)
