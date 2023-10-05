from src.bot.exceptions.base_exception import BaseConnectorException


class JsonDecodeException(BaseConnectorException):
    def __init__(self, text: str):
        super().__init__(f"Cant parse json: {text}")
