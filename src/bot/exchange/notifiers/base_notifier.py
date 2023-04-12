import abc
from typing import List


class BaseNotifier(metaclass=abc.ABCMeta):
    def __init__(self):
        self.stack: List[str] = []
        self.exchange_name = 'Connector'

    def add_message_to_stack(self, message: str):
        self.stack.append(message)

    def set_exchange_name(self, exchange_name: str):
        self.exchange_name = exchange_name

    @abc.abstractmethod
    async def send_message(self):
        pass

    @staticmethod
    def get_separator():
        return '\n\n'
