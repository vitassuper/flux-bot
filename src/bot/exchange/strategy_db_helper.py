from datetime import datetime
from decimal import Decimal
from typing import Literal, Union

from src.bot.models import Order, Deal
from src.bot.services.deal import update_deal, get_deal, create_deal, increment_safety_orders_count, get_or_create_deal
from src.bot.services.order import create_order, get_orders_volume, get_deal_stats
from src.bot.objects.deal_stats import DealStats
from src.bot.types.order_side_type import OrderSideType
from src.bot.types.side_type import SideType


class StrategyDBHelper:
    def __init__(self, side: SideType, bot_id: int, pair: str, position: Union[int, None] = None):
        self.side = side
        self.bot_id = bot_id
        self.pair = pair
        self.position = position

    def get_order_side(self, action: Literal['open', 'close']) -> OrderSideType:
        mapping = {
            (SideType.short, 'open'): OrderSideType.sell,
            (SideType.short, 'close'): OrderSideType.buy,
            (SideType.long, 'open'): OrderSideType.buy,
            (SideType.long, 'close'): OrderSideType.sell
        }

        return mapping.get((self.side, action), None)

    async def create_open_order(self, deal_id: int, price: Decimal, volume: Decimal) -> Order:
        return await create_order(deal_id=deal_id, side=self.get_order_side(action='open'), price=price, volume=volume)

    async def create_average_order(self, deal_id: int, price: Decimal, volume: Decimal) -> Order:
        return await create_order(deal_id=deal_id, side=self.get_order_side(action='open'), price=price, volume=volume)

    async def create_close_order(self, deal_id: int, price: Decimal, volume: Decimal) -> Order:
        return await create_order(deal_id=deal_id, side=self.get_order_side(action='close'), price=price, volume=volume)

    async def close_deal(self, deal_id: int, pnl: float) -> Deal:
        return await update_deal(deal_id=deal_id, pnl=pnl, date_close=datetime.now())

    async def get_deal(self) -> Deal:
        return await get_deal(bot_id=self.bot_id, pair=self.pair, position=self.position)

    async def get_or_create_deal(self) -> Deal:
        return await get_or_create_deal(bot_id=self.bot_id, pair=self.pair)

    async def open_deal(self) -> Deal:
        return await create_deal(bot_id=self.bot_id, pair=self.pair, date_open=datetime.now(), position=self.position)

    async def get_deal_stats(self, deal_id: int) -> DealStats:
        return await get_deal_stats(deal_id=deal_id)

    async def get_deal_base_amount(self, deal_id: int) -> float:
        return await get_orders_volume(deal_id=deal_id)

    # TODO: redundant in future because we have order model
    async def average_deal(self, deal_id: int) -> int:
        return await increment_safety_orders_count(deal_id=deal_id)
