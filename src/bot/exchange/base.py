import abc
import re


class BaseExchange(metaclass=abc.ABCMeta):
    def __init__(self, bot_id: int, exchange) -> None:
        self.bot_id = bot_id
        self.exchange = exchange

        self.exchange.load_markets()

    # Abstract methods
    @abc.abstractmethod
    def get_exchange_name(self):
        pass

    @abc.abstractmethod
    def ensure_long_position_not_opened(self, pair: str) -> None:
        pass

    @abc.abstractmethod
    def ensure_short_position_not_opened(self, pair: str) -> None:
        pass

    @abc.abstractmethod
    def ensure_long_position_opened(self, pair: str) -> None:
        pass

    @abc.abstractmethod
    def ensure_short_position_opened(self, pair: str) -> None:
        pass

    @abc.abstractmethod
    def buy_short_position(self, pair: str, amount: int):
        pass

    @abc.abstractmethod
    def sell_short_position(self, pair: str, amount: int):
        pass

    @abc.abstractmethod
    def buy_long_position(self, pair: str, amount: int):
        pass

    @abc.abstractmethod
    def sell_long_position(self, pair: str, amount: int):
        pass

    @abc.abstractmethod
    def set_leverage_for_short_position(self, pair: str, leverage: int):
        pass

    @abc.abstractmethod
    def set_leverage_for_long_position(self, pair: str, leverage: int):
        pass

    @abc.abstractmethod
    def add_margin_to_short_position(self, pair: str, amount: float):
        pass

    @abc.abstractmethod
    def add_margin_to_long_position(self, pair: str, amount: float):
        pass

    @abc.abstractmethod
    def get_base_amount(self, symbol: str, quote_amount: float):
        pass

    @abc.abstractmethod
    def get_order_status(self, order, pair):
        pass

    @abc.abstractmethod
    def get_opened_position(self, pair: str):
        pass

    # End Abstract methods

    # TODO: temp solution
    def guess_symbol_from_tv(self, symbol: str):
        base = symbol.split('USDT')[0]
        base = re.sub(r'[^a-zA-Z\d]+', '', base)

        return self.exchange.market(f'{base}/USDT:USDT')['symbol']
