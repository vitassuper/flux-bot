from decimal import Decimal
from typing import List

from src.app.models import Order
from src.bot.exceptions.connector_exception import ConnectorException


class Helper:
    @staticmethod
    def calculate_average_price(orders: List[Order]) -> float:
        total_volume = Helper.calculate_total_volume(orders=orders)
        total_value = sum(order.price * order.volume for order in orders)

        if total_volume == 0:
            raise ConnectorException('Total volume cant be zero')

        return total_value / total_volume

    @staticmethod
    def calculate_total_volume(orders: List[Order]) -> float:
        return sum(order.volume for order in orders)

    @staticmethod
    def calculate_realized_pnl(volume: Decimal, avg_price: Decimal, close_volume: Decimal, close_avg_price: Decimal,
                               fee: Decimal, sign: int):
        entry_sum = volume * avg_price
        exit_sum = close_volume * close_avg_price

        u_pnl = (exit_sum - entry_sum) * sign

        exit_fee = exit_sum * fee
        entry_fee = entry_sum * fee

        return u_pnl - entry_fee - exit_fee
