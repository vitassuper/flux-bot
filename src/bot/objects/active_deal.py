from datetime import datetime
from typing import Union

from src.app.models.deal import Deal
from src.bot.exchange.strategy_helper import StrategyHelper
from src.bot.objects.base_deal import BaseDeal
from src.bot.types.side_type import SideType


class ActiveDeal(BaseDeal):
    def __init__(
        self,
        pair: str,
        margin: str,
        avg_price: str,
        current_price: str,
        liquidation_price: Union[str, None],
        unrealized_pnl: str,
        notional_size: str,
        deal: Deal,
        side: Union[SideType.short, SideType.long]
    ):
        self.margin = margin
        self.current_price = current_price
        self.liquidation_price = liquidation_price
        self.unrealized_pnl = unrealized_pnl
        self.notional_size = notional_size
        self.side = side

        duration = 'unknown'
        safety_orders_count = 'unknown'

        if deal:
            duration = StrategyHelper.get_time_duration_string(deal.date_open, datetime.now())
            safety_orders_count = deal.safety_order_count

        self.duration = duration
        self.safety_orders_count = safety_orders_count

        # TODO: notional size not the same like quote amount
        super().__init__(pair=pair, quote_amount=notional_size, price=avg_price)
