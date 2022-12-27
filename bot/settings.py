import os

from dotenv import load_dotenv


class Config:
    def __init__(self):
        self.connector_secret = ''
        self.apiKey = ''
        self.apiSecret = ''
        self.safety_margin = 0
        self.exchange_name = ''
        self.telegram_token = ''
        self.telegram_chat_id = ''
        self.telegram_chat_id2 = ''

        self.load_config()

    def load_config(self):
        load_dotenv()

        self.connector_secret = os.environ['CONNECTOR_SECRET']
        self.apiKey = os.environ['API_KEY']
        self.apiSecret = os.environ['API_SECRET']
        self.safety_margin = os.environ['SAFETY_MARGIN']
        self.exchange_name = os.environ['EXCHANGE_NAME']
        self.telegram_token = os.environ['TELEGRAM_BOT_TOKEN']
        self.telegram_chat_id = os.environ['TELEGRAM_CHAT_ID']
        self.telegram_chat_id2 = os.environ['TELEGRAM_CHAT_ID2']

    def validate_connector_secret(self, secret):
        return self.connector_secret == secret
