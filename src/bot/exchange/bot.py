from src.bot.exception import ConnectorException
from src.bot.exchange.base_strategy import BaseStrategy
from src.bot.exchange.binance import Binance
from src.bot.exchange.grid_strategy import GridStrategy
from src.bot.exchange.long_strategy import LongStrategy
from src.bot.exchange.okx import Okex
from src.bot.exchange.short_strategy import ShortStrategy


class Bot:
    def __init__(self, bot_id: int) -> None:
        self.bot_id = bot_id
        self.exchange = self.get_exchange()

    def get_exchange(self):
        if self.bot_id == 1:
            return Okex(self.bot_id)
        if self.bot_id == 2:
            return Binance(self.bot_id)
        if self.bot_id == 3:
            return Okex(self.bot_id)

        if self.bot_id in range(10, 20):
            return Okex(self.bot_id)

        raise ConnectorException('Unknown bot id')

    def get_strategy(self):
        if self.bot_id == 3:
            return LongStrategy(bot_id=self.bot_id, exchange=self.exchange)

        if self.bot_id in range(10, 15):
            strategy = ShortStrategy(
                bot_id=self.bot_id, exchange=self.exchange, margin_type='cross')

            return GridStrategy(bot_id=self.bot_id, strategy=strategy)

        if self.bot_id in range(15, 20):
            strategy = LongStrategy(
                bot_id=self.bot_id, exchange=self.exchange, margin_type='cross')

            return GridStrategy(bot_id=self.bot_id, strategy=strategy)

        return ShortStrategy(bot_id=self.bot_id, exchange=self.exchange)

    # TODO: temp solution
    def guess_symbol_from_tv(self, symbol: str):
        return self.exchange.guess_symbol_from_tv(symbol=symbol)
