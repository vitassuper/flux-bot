from src.bot.exception import ConnectorException
from src.bot.exchange.base_strategy import BaseStrategy
from src.bot.exchange.binance import Binance
from src.bot.exchange.long_strategy import LongStrategy
from src.bot.exchange.okx import Okex
from src.bot.exchange.short_strategy import ShortStrategy


class Bot:
    def __init__(self, bot_id: int) -> None:
        self.bot_id = bot_id
        self.exchange = self.get_exchange(bot_id=bot_id)

    def get_exchange(self, bot_id: int):
        if bot_id == 1:
            return Okex(bot_id)
        if bot_id == 2:
            return Binance(bot_id)
        if bot_id == 3:
            return Okex(bot_id)

        raise ConnectorException('Unknown bot id')

    def get_strategy(self) -> BaseStrategy:
        if self.bot_id == 3:
            return LongStrategy(bot_id=self.bot_id, exchange=self.exchange)

        return ShortStrategy(bot_id=self.bot_id, exchange=self.exchange)

    # TODO: temp solution

    def guess_symbol_from_tv(self, symbol: str):
        return self.exchange.guess_symbol_from_tv(symbol=symbol)
