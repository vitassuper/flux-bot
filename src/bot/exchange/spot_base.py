import abc
import re


class SpotBaseExchange(metaclass=abc.ABCMeta):
    def __init__(self, bot_id: int, exchange) -> None:
        self.bot_id = bot_id
        self.exchange = exchange

        self.exchange.load_markets()

    @abc.abstractmethod
    def market_sell(self, pair: str, amount: int):
        pass

    @abc.abstractmethod
    def market_buy(self, pair: str, amount: int):
        pass

    # TODO: temp solution
    def guess_symbol_from_tv(self, symbol: str):
        base = symbol.split('USDT')[0]
        base = re.sub(r'[^a-zA-Z\d]+', '', base)

        return self.exchange.market(f'{base}/USDT')['symbol']