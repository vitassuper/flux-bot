from datetime import datetime
from decimal import Decimal
from typing import Union

from src.bot.types.side_type import SideType
from src.bot.utils.helper import Helper


class StrategyHelper:
    def __init__(self, taker_fee: Decimal, side: Union[SideType.short, SideType.long], contract_size: Decimal):
        self.taker_fee = taker_fee
        self.side = side
        self.contract_size = contract_size

    def get_sign(self) -> int:
        if self.side == SideType.short:
            return -1

        return 1

    def calculate_realized_pnl(self, volume: Decimal, avg_price: Decimal, close_volume: Decimal,
                               close_avg_price: Decimal) -> Decimal:
        return Helper.calculate_realized_pnl(volume=volume * self.contract_size, avg_price=avg_price,
                                             close_volume=close_volume * self.contract_size,
                                             close_avg_price=close_avg_price, fee=self.taker_fee, sign=self.get_sign())

    # Todo move to Helper like calculate_realized_pnl
    def calculate_pnl_percentage(self, avg_price: Decimal, close_price: Decimal):
        percentage = ((close_price - avg_price) / avg_price) * 100

        return percentage.quantize(Decimal('0.01')) * self.get_sign()

    def calculate_position_pnl_percentage(self, avg_price: Decimal, close_price: Decimal, leverage: int):
        return self.calculate_pnl_percentage(close_price, avg_price) * Decimal(leverage)

    @staticmethod
    def get_time_duration_string(date_open: datetime, date_close: datetime) -> str:
        diff = date_close - date_open
        seconds = int(diff.total_seconds())

        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)

        return f'{int(days)} days, {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds'
