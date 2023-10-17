import abc
import re
from decimal import Decimal
from typing import Union, Dict

from src.bot.exchanges.decorators import retry_on_exception
from src.bot.types.margin_type import MarginType


class BaseExchange(metaclass=abc.ABCMeta):
    def __init__(self, exchange) -> None:
        self.ccxt_exchange = exchange

        self.load_markets()

    # Abstract methods
    @abc.abstractmethod
    def get_exchange_name(self):
        pass

    @abc.abstractmethod
    def buy_short_position(
        self,
        pair: str,
        amount: float,
        margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated,
    ):
        pass

    @abc.abstractmethod
    def sell_short_position(
        self,
        pair: str,
        amount: float,
        margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated,
    ):
        pass

    @abc.abstractmethod
    def buy_long_position(
        self,
        pair: str,
        amount: float,
        margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated,
    ):
        pass

    @abc.abstractmethod
    def sell_long_position(
        self,
        pair: str,
        amount: float,
        margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated,
    ):
        pass

    @abc.abstractmethod
    def set_leverage_for_short_position(
        self,
        pair: str,
        leverage: int,
        margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated,
    ):
        pass

    @abc.abstractmethod
    def set_leverage_for_long_position(
        self,
        pair: str,
        leverage: int,
        margin_type: Union[MarginType.cross, MarginType.isolated] = MarginType.isolated,
    ):
        pass

    @abc.abstractmethod
    def add_margin_to_short_position(self, pair: str, amount: float):
        pass

    @abc.abstractmethod
    def add_margin_to_long_position(self, pair: str, amount: float):
        pass

    @abc.abstractmethod
    def get_base_amount(self, pair: str, quote_amount: Decimal):
        pass

    @abc.abstractmethod
    def get_order_status(self, order, pair):
        pass

    @abc.abstractmethod
    def get_opened_short_position(self, pair: str) -> Union[Dict, None]:
        pass

    @abc.abstractmethod
    def get_opened_long_position(self, pair: str) -> Union[Dict, None]:
        pass

    # End Abstract methods

    # Unified methods

    def get_market(self, pair: str):
        return self.ccxt_exchange.market(pair)

    @retry_on_exception()
    def load_markets(self):
        self.ccxt_exchange.load_markets()

    # TODO: temp solution
    def guess_symbol_from_tv(self, symbol: str):
        base = symbol.split("USDT")[0]
        base = re.sub(r"[^a-zA-Z\d]+", "", base)

        return self.ccxt_exchange.market(f"{base}/USDT:USDT")["symbol"]
