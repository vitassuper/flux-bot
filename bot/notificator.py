from telegram import Bot
import os

def send_notification(text, chatId = None):
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    bot = Bot(token)

    if(chatId):
        bot.send_message(chatId, text)
    else:
        bot.send_message(os.getenv('TELEGRAM_CHAT_ID'), text)
        bot.send_message(os.getenv('TELEGRAM_CHAT_ID2'), text)