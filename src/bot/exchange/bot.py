from typing import Union

from src.bot.exceptions import NotFoundException
from src.bot.exceptions.connector_exception import ConnectorException
from src.bot.exceptions.disabled_exception import DisabledException
from src.bot.exchange.exchange_manager import ExchangeManager
from src.bot.exchange.side.base_side import BaseSide
from src.bot.exchange.side.long_side import LongSide
from src.bot.exchange.side.short_side import ShortSide
from src.bot.exchange.strategies.grid_strategy import GridStrategy
from src.bot.models import Bot as BotModel, Deal
from src.bot.repositories.bot import get_bot
from src.bot.services import get_exchange
from src.bot.services.deal import get_deal_by_id, get_deal
from src.bot.types.bot_side_type import BotSideType
from src.bot.types.margin_type import MarginType
from src.schemas import Signal


class Bot:
    def __init__(self, bot: BotModel, signal: Signal) -> None:
        self.margin_type = None
        self.exchange = None
        self.signal = signal
        self.bot = bot
        self.pair = signal.pair
        self.position = signal.position
        self.deal = None

    async def process(self):
        bot = await get_bot(self.signal.bot_id)

        self.exchange = await self.get_exchange(bot.exchange_id)
        self.pair = self.guess_symbol_from_tv(symbol=self.pair)
        self.deal = await self.get_active_deal()

        await self.ensure_bot_enabled(bot=bot)

        if self.is_open_signal() and self.deal:
            raise ConnectorException("Deal already exists")
        elif not self.is_open_signal() and not self.deal:
            raise NotFoundException("deal")

        self.margin_type = MarginType.cross

        return await self.get_strategy(self.get_side())

    async def get_exchange(self, exchange_id: int):
        exchange_manager = ExchangeManager(await get_exchange(exchange_id=exchange_id))
        return exchange_manager.get_exchange()

    def get_side(self) -> BaseSide:
        if self.bot.side == BotSideType.short:
            return ShortSide(exchange=self.exchange, margin_type=self.margin_type)

        return LongSide(exchange=self.exchange, margin_type=self.margin_type)

    async def get_strategy(self, side: BaseSide):
        return GridStrategy(
            bot_id=self.bot.id,
            side=side,
            pair=self.pair,
            position=self.position,
            deal=await self.get_active_deal(),
        )

    def get_bot_name(self):
        return f"Bot id: {self.bot.id} ({self.exchange.get_exchange_name()})"

    async def get_active_deal(self) -> Union[Deal, None]:
        if getattr(self.signal, "deal_id", None):
            return await get_deal_by_id(deal_id=self.signal.deal_id)

        return await get_deal(
            bot_id=self.bot.id, pair=self.pair, position=self.signal.position
        )

    async def ensure_bot_enabled(self, bot: BotModel):
        if not bot.enabled and (
            self.is_open_signal()
            or (self.signal.type_of_signal in ["add", "close"] and not self.deal)
        ):
            raise DisabledException()

    # TODO: temp solution
    def guess_symbol_from_tv(self, symbol: str):
        return self.exchange.guess_symbol_from_tv(symbol=symbol)

    def is_open_signal(self):
        return self.signal.type_of_signal == "open"
