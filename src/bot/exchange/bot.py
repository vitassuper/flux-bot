from src.bot.exceptions.connector_exception import ConnectorException
from src.bot.exchange.binance import Binance
from src.bot.exchange.okx import Okex
from src.bot.exchange.side.base_side import BaseSide
from src.bot.exchange.side.long_side import LongSide
from src.bot.exchange.side.short_side import ShortSide
from src.bot.exchange.strategies.grid_strategy import GridStrategy
from src.bot.exchange.strategies.simple_strategy import SimpleStrategy
from src.bot.types.margin_type import MarginType


class Bot:
    def __init__(self, bot_id: int, pair: str) -> None:
        self.bot_id = bot_id
        self.exchange = self.get_exchange()
        self.pair = self.guess_symbol_from_tv(symbol=pair)
        self.margin_type = self.get_margin_type()

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

    # TODO: remove it later
    def get_margin_type(self):
        if self.bot_id == 1 or self.bot_id == 3:
            return MarginType.isolated

        return MarginType.cross

    def get_side(self) -> BaseSide:
        if self.bot_id in range(15, 20) or self.bot_id == 3:
            LongSide(
                exchange=self.exchange, margin_type=self.margin_type)

        return ShortSide(exchange=self.exchange, margin_type=self.margin_type)

    def get_strategy(self, side: BaseSide):
        if self.bot_id == 3 or self.bot_id == 1 or self.bot_id == 2:
            return SimpleStrategy(bot_id=self.bot_id, side=side, pair=self.pair)

        return GridStrategy(bot_id=self.bot_id, side=side, pair=self.pair)

    def get_bot_name(self):
        return f'Bot id: {self.bot_id} ({self.exchange.get_exchange_name()})'

    # TODO: temp solution
    def guess_symbol_from_tv(self, symbol: str):
        return self.exchange.guess_symbol_from_tv(symbol=symbol)
