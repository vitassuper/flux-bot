from dataclasses import dataclass
from datetime import datetime
from typing import Union

from src.db.models import Deal
from src.bot.exchanges.strategy_helper import StrategyHelper
from src.bot.types.side_type import SideType


@dataclass
class ActiveDealMessage:
    pair: str
    margin: str
    avg_price: str
    current_price: str
    liquidation_price: Union[str, None]
    unrealized_pnl: str
    notional_size: str
    deal: Deal
    side: Union[SideType.short, SideType.long]
    duration: str = "Unknown"
    safety_orders_count: Union[int, str] = "Unknown"

    def __post_init__(self):
        if self.deal:
            self.duration = StrategyHelper.get_time_duration_string(
                self.deal.date_open, datetime.now()
            )
            self.safety_orders_count = self.deal.safety_order_count

    def __str__(self):
        return (
            f"{self.pair}\n"
            f"{self.side.capitalize()} {'🟥' if self.side == SideType.short else '🟩'}\n"
            f"Margin: {self.margin}\n"
            f"Current price: {self.current_price}\n"
            f"Avg price: {self.avg_price}\n"
            f"Unrealized PNL: {self.unrealized_pnl}\n"
            f"liquidationPrice: {self.liquidation_price}\n"
            f"Pos size: {self.notional_size}💰\n"
            f"Duration: {self.duration}\n"
            f"Safety orders {self.safety_orders_count}\n"
        )
