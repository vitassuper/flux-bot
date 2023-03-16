from datetime import datetime
from typing import Union
from src.app.models.deal import Deal
from src.bot.helper import get_time_duration_string
from src.bot.objects.base_position import BasePosition


class ActivePosition(BasePosition):
    def __init__(
        self,
        pair: str,
        margin: str,
        avg_price: str,
        current_price: str,
        liquidation_price: Union[str, None],
        unrealized_pnl: str,
        notional_size: str,
        deal: Deal
    ):
        self.margin = margin
        self.avg_price = avg_price
        self.current_price = current_price
        self.liquidation_price = liquidation_price
        self.unrealized_pnl = unrealized_pnl
        self.notional_size = notional_size

        duration = 'unknown'
        safety_orders_count = 'unknown'

        if deal:
            duration = get_time_duration_string(deal.date_open, datetime.now())
            safety_orders_count = deal.safety_order_count

        self.duration = duration
        self.safety_orders_count = safety_orders_count

        # TODO: notional size not the same like quote amount
        super().__init__(pair=pair, quote_amount=notional_size)
