from src.bot.exceptions.base_exception import BaseConnectorException


class DisabledException(BaseConnectorException):
    def __init__(self):
        super().__init__(f"Bot disabled")
