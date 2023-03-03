from datetime import datetime
from src.app.models.deal import Deal
from src.bot.helper import get_time_duration_string


class Position:
    def __init__(
        self,
        ticker: str,
        margin: str,
        avg_price: str,
        current_price: str,
        liquidation_price: str,
        unrealized_pnl: str,
        notional_size: str,
        deal: Deal
    ):
        self.ticker = ticker
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
