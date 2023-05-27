from src.app.repositories.bot import get_bot
from src.app.services.bot import get_copy_bots
from src.app.services.deal import is_deal_exist
from src.bot.exceptions.connector_exception import ConnectorException
from src.bot.exchange.binance import Binance
from src.bot.exchange.okx import Okex
from src.bot.exchange.side.base_side import BaseSide
from src.bot.exchange.side.long_side import LongSide
from src.bot.exchange.side.short_side import ShortSide
from src.bot.exchange.strategies.grid_strategy import GridStrategy
from src.bot.exchange.strategies.simple_strategy import SimpleStrategy
from src.bot.types.margin_type import MarginType

from src.bot.utils.helper import Helper


class Bot:
    def __init__(self, bot_id: int, pair: str, type_of_signal: str) -> None:
        self.margin_type = None
        self.exchange = None
        self.type_of_signal = type_of_signal
        self.bot_id = bot_id
        self.pair = pair

    async def get_copy_bots(self):
        if self.bot_id in range(100, 300):
            bot = await get_bot(bot_id=self.bot_id)

            return await get_copy_bots(bot_id=bot.id)

        return []

    async def process(self):
        self.exchange = await self.get_exchange()
        self.pair = self.guess_symbol_from_tv(symbol=self.pair)

        if self.bot_id in range(100, 300):
            bot = await get_bot(bot_id=self.bot_id)

            if not bot.enabled:
                if self.type_of_signal == 'open':
                    raise ConnectorException('Bot disabled')
                elif self.type_of_signal == 'add' and not await is_deal_exist(self.bot_id, self.pair):
                    raise ConnectorException('Bot disabled')

        self.margin_type = self.get_margin_type()

        return self.get_strategy(self.get_side())

    async def get_exchange_credentials(self):
        bot = await get_bot(bot_id=self.bot_id)

        api_key = Helper.decrypt_string(bot.api_key)
        api_secret = Helper.decrypt_string(bot.api_secret)

        return api_key, api_secret

    async def get_exchange(self):
        if self.bot_id in range(10, 20):
            return Okex(self.bot_id)

        if self.bot_id in range(100, 200):
            key, secret = await self.get_exchange_credentials()

            return Binance(self.bot_id, key, secret, False)

        if self.bot_id in range(200, 300):
            key, secret = await self.get_exchange_credentials()

            return Binance(self.bot_id, key, secret, True)

        raise ConnectorException('Unknown bot id')

    # TODO: remove it later
    def get_margin_type(self):
        if self.bot_id == 1 or self.bot_id == 3:
            return MarginType.isolated

        return MarginType.cross

    def get_side(self) -> BaseSide:
        if self.bot_id in range(15, 20) or self.bot_id == 3:
            return LongSide(
                exchange=self.exchange, margin_type=self.margin_type)

        if self.bot_id in range(100, 150):
            return ShortSide(exchange=self.exchange, margin_type=self.margin_type)

        if self.bot_id in range(150, 200):
            return LongSide(
                exchange=self.exchange, margin_type=self.margin_type)

        if self.bot_id in range(200, 250):
            return ShortSide(exchange=self.exchange, margin_type=self.margin_type)

        if self.bot_id in range(250, 300):
            return LongSide(
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
