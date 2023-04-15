from datetime import datetime
from typing import Literal

from src.app.models import Order, Deal
from src.app.services.deal import update_deal, get_deal, create_deal, increment_safety_orders_count
from src.app.services.order import create_order, get_orders_volume
from src.bot.types.order_side_type import OrderSideType
from src.bot.types.side_type import SideType


class StrategyDBHelper:
    def __init__(self, side: SideType, bot_id: int, pair: str):
        self.side = side
        self.bot_id = bot_id
        self.pair = pair

    def get_order_side(self, action: Literal['open', 'close']) -> OrderSideType:
        mapping = {
            (SideType.short, 'open'): OrderSideType.sell,
            (SideType.short, 'close'): OrderSideType.buy,
            (SideType.long, 'open'): OrderSideType.buy,
            (SideType.long, 'close'): OrderSideType.sell
        }

        return mapping.get((self.side, action), None)

    async def create_open_order(self, deal_id: int, price: float, volume: float) -> Order:
        return await create_order(deal_id=deal_id, side=self.get_order_side(action='open'), price=price, volume=volume)

    async def create_average_order(self, deal_id: int, price: float, volume: float) -> Order:
        return await create_order(deal_id=deal_id, side=self.get_order_side(action='open'), price=price, volume=volume)

    async def create_close_order(self, deal_id: int, price: float, volume: float) -> Order:
        return await create_order(deal_id=deal_id, side=self.get_order_side(action='close'), price=price, volume=volume)

    async def close_deal(self, deal_id: int, pnl: float) -> Deal:
        return await update_deal(deal_id=deal_id, pnl=pnl, date_close=datetime.now())

    async def get_deal(self) -> Deal:
        return await get_deal(bot_id=self.bot_id, pair=self.pair)

    async def open_deal(self) -> Deal:
        return await create_deal(bot_id=self.bot_id, pair=self.pair, date_open=datetime.now())

    async def get_deal_base_amount(self, deal_id: int) -> float:
        return await get_orders_volume(deal_id=deal_id)

    # TODO: redundant in future because we have order model
    async def average_deal(self, deal_id: int) -> int:
        return await increment_safety_orders_count(deal_id=deal_id)
