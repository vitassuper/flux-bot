from datetime import datetime
from decimal import Decimal
from typing import Union, List

from src.app.models import Order
from src.bot.types.side_type import SideType


class StrategyHelper:
    def __init__(self, taker_fee: float, side: Union[SideType.short, SideType.long]):
        self.taker_fee = taker_fee
        self.side = side

    def get_sign(self) -> int:
        if self.side == SideType.short:
            return -1

        return 1

    def calculate_average_price(self, orders: List[Order]):
        total_volume = 0
        total_value = 0

        for order in orders:
            total_volume += order.volume
            total_value += order.price * order.volume

        return total_value / total_volume

    def calculate_realized_pnl(self, volume: float, avg_price: float, close_volume: float,
                               close_avg_price: float) -> float:
        entry_sum = volume * avg_price
        exit_sum = close_volume * close_avg_price

        u_pnl = exit_sum - entry_sum

        exit_fee = exit_sum * self.taker_fee
        entry_fee = entry_sum * self.taker_fee

        return (u_pnl - entry_fee - exit_fee) * self.get_sign()

    def calculate_pnl_percentage(self, avg_price: float, close_price: float):
        return Decimal(
            ((close_price - avg_price) / avg_price) * 100
        ).quantize(Decimal('0.01')) * self.get_sign()

    def calculate_position_pnl_percentage(self, avg_price: float, close_price: float, leverage: int):
        return self.calculate_pnl_percentage(close_price, avg_price) * Decimal(leverage)

    @staticmethod
    def get_time_duration_string(date_open: datetime, date_close: datetime) -> str:
        diff = date_close - date_open
        seconds = int(diff.total_seconds())

        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)

        return f'{int(days)} days, {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds'
