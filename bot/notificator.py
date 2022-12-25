from telegram import Bot

from bot.settings import Config

class Notificator:
    def __init__(self):
        self.config = Config()
        self.bot = Bot(self.config.telegram_token)

    def send_warning_notification(self, text):
        text = f"{self.config.exchange_name}:\n🚨{text}"

        self.bot.send_message(self.config.telegram_chat_id, text)
        self.bot.send_message(self.config.telegram_chat_id2, text)
        

    def send_notification(self, text, chatId = None):
        text = f"{self.config.exchange_name}:\n{text}"

        if(chatId):
            self.bot.send_message(chatId, text)
        else:
            self.bot.send_message(self.config.telegram_chat_id, text)
            self.bot.send_message(self.config.telegram_chat_id2, text)
