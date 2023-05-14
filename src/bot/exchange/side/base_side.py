import abc
from typing import Union

from src.bot.exchange.base import BaseExchange
from src.bot.types.margin_type import MarginType
from src.bot.types.side_type import SideType


class BaseSide(metaclass=abc.ABCMeta):

    def __init__(self, exchange: BaseExchange,
                 margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated) -> None:
        self.margin_type = margin_type
        self.exchange = exchange

    @abc.abstractmethod
    def ensure_deal_not_opened(self, pair: str) -> None:
        pass

    @abc.abstractmethod
    def ensure_deal_opened(self, pair: str) -> None:
        pass

    @abc.abstractmethod
    def set_leverage(self, pair: str, leverage: int):
        pass

    @abc.abstractmethod
    def open_market_order(self, pair: str, amount: float):
        pass

    @abc.abstractmethod
    def close_market_order(self, pair: str, amount: float):
        pass

    @abc.abstractmethod
    def add_margin(self, pair: str, quote_amount: float):
        pass

    @abc.abstractmethod
    def get_opened_position(self, pair: str):
        pass

    def get_type(self) -> Union[MarginType.cross, MarginType.isolated]:
        return self.margin_type

    @abc.abstractmethod
    def get_side_type(self) -> Union[SideType.long, SideType.short]:
        pass

    def average_market_order(self, pair: str, amount: float):
        return self.open_market_order(pair=pair, amount=amount)
