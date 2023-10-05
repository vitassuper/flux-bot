from src.bot.exceptions.base_exception import BaseConnectorException


class SecretException(BaseConnectorException):
    def __init__(self):
        super().__init__("Incorrect secret")
